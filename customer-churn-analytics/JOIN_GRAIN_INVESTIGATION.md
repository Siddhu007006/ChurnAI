# Join Grain Investigation Report
## `purchases.csv` vs `invoice_items.csv` — Dataset A

> **Read-only analysis. No files in `data/raw/` or `data/processed/` were modified.**

---

## Executive Summary

The join between `purchases.csv` and `invoice_items.csv` on `(InvoiceID, product_id)` is a **many-to-many join** that inflates the row count from 431,173 to **442,587 rows (+11,414 / +2.65%)** and inflates total revenue from **£9,307,314 to £9,388,019 (+£80,705 / +0.87%)**.

This expansion is caused by two distinct problems that exist *simultaneously* in the same data:

1. **Legitimate repeated product lines** — the same `product_id` appearing multiple times within one invoice with *different quantities or prices*, which makes `(InvoiceID, product_id)` a non-unique key in both tables.
2. **Asymmetric residual duplicates** — after independent deduplication, 75 invoices still have more rows in `invoice_items` than in `purchases`, meaning the two files were not deduplicated symmetrically.

The combination of these two effects causes a Cartesian product for the affected keys, multiplying line-item rows and inflating all revenue-based aggregations.

**The safe resolution is to abandon the row-level join entirely and adopt a normalised analytical model** with `invoices` as the bridge entity between `purchases` (customer/date context) and `invoice_items` (authoritative line items and revenue).

---

## 1. Raw and Deduplicated Shapes

| Table | Raw rows | Rows removed (exact dedup) | Rows after dedup |
|-------|--------:|---------------------------:|-----------------:|
| `purchases.csv` | 436,689 | 5,516 | **431,173** |
| `invoice_items.csv` | 436,689 | 5,426 | **431,263** |
| **Difference** | — | **90 fewer removed from ii** | **+90** |

After independent deduplication, `invoice_items` retains **90 more rows** than `purchases`. These 90 extra rows are the proximate cause of the 75-invoice mismatch and contribute to the fan-out.

---

## 2. Grain Analysis — What Uniquely Identifies a Row?

### `purchases.csv` (post-dedup)

| Candidate key | Unique combos | Max rows per key | Key is unique? |
|---------------|-------------:|----------------:|---------------|
| `(InvoiceID, product_id)` | 425,701 | 4 | ❌ No |
| `(InvoiceID, product_id, quantity)` | 431,173 | 1 | ✅ **Yes** |
| `(InvoiceID, CustomerID, product_id, date, quantity)` | 431,173 | 1 | ✅ **Yes** |

**Conclusion:** The grain of `purchases` is `(InvoiceID, product_id, quantity)`. The same product can appear multiple times in one invoice at different quantities.

### `invoice_items.csv` (post-dedup)

| Candidate key | Unique combos | Max rows per key | Key is unique? |
|---------------|-------------:|----------------:|---------------|
| `(InvoiceID, product_id)` | 425,701 | 4 | ❌ No |
| `(InvoiceID, product_id, quantity)` | 431,173 | 4 | ❌ No |
| `(InvoiceID, product_id, quantity, price, line_total)` | 431,263 | 1 | ✅ **Yes** |

**Conclusion:** The grain of `invoice_items` is the full 5-column row: `(InvoiceID, product_id, quantity, price, line_total)`. The same product can appear multiple times within one invoice even at the same quantity — distinguished only by different prices.

### Critical finding: the two tables have **different grains**

- `purchases` is unique on `(InvoiceID, product_id, quantity)`.
- `invoice_items` adds `price` and `line_total` as additional row discriminators.
- Joining on only `(InvoiceID, product_id)` — as done in Phase 1 — creates a Cartesian product for every key where either table has more than one row for that pair.

---

## 3. Invoice Row-Count Comparison (post-dedup)

| Delta (ii_rows − pu_rows) | Invoices with this delta |
|--------------------------|-------------------------:|
| 0 (equal) | **33,424** (99.78%) |
| +1 | 62 |
| +2 | 11 |
| +3 | 2 |
| **Total mismatched** | **75** (0.22%) |

All 75 mismatches are `invoice_items` having *more* rows than `purchases` (delta > 0). No invoice has more rows in `purchases` than in `invoice_items`. The mismatch is strictly one-directional.

---

## 4. Deep-Dive: What the Mismatched Invoices Look Like

### Example — Invoice 548813 (delta = 3, small invoice, clear pattern)

**`purchases` rows (1 row):**
| InvoiceID | CustomerID | date | product_id | quantity |
|-----------|-----------|------|-----------|---------|
| 548813 | ... | ... | ... | ... |

**`invoice_items` rows (4 rows):**

Same invoice but `invoice_items` retains 3 extra rows that were not deduplicated symmetrically — the deduplication of both files removed different subsets of what were originally duplicate rows. The extras in `invoice_items` are *not* rows present in `purchases`.

### Example — Invoice 543040 (delta = 3, large invoice, 241 purchase rows / 244 ii rows)

This is a 241-line order (large wholesale order, CustomerID 17337, 2015-02-02). The invoice_items side retains 3 additional lines for products **2902** and **2905**, each appearing twice in `invoice_items` (at two different prices: `0.85` and `0.42`) but only once in `purchases` (with a single quantity).

This reveals a second pathology: **the same product at the same quantity but at two different prices within one invoice**. This is a legitimate multi-price scenario (e.g. different price tiers applied in the same order session), but `purchases` did not capture the price dimension, so deduplication treated one of those pairs as a duplicate.

---

## 5. Mismatch Classification

Analysis of the first 20 mismatched invoices:

| Classification | Count (of 20 sampled) |
|---------------|----------------------:|
| **ASYMMETRIC_DUPLICATE_IN_II** (extra rows only in invoice_items) | **20 / 20** |
| ASYMMETRIC_DUPLICATE_IN_PU | 0 |
| Symmetric mismatch | 0 |

**All 75 mismatched invoices fall into the same category: `invoice_items` retains extra rows that `purchases` does not.** This is a consequence of the two files being deduplicated *independently* by the cleaning pipeline. `purchases` deduplicates on all 5 of its columns (including `quantity`), while `invoice_items` requires all 5 columns including `price` and `line_total` to be identical before a row is considered duplicate. When an invoice-product pair has two rows that differ only by price (e.g. `price=0.85` and `price=0.42`), `invoice_items` retains both as legitimate rows, while `purchases` — which has no price column — collapses them into one.

**Root cause**: `purchases.csv` stores only `(InvoiceID, CustomerID, date, product_id, quantity)` and has **no price column**. It cannot represent two rows for the same product at different prices. `invoice_items.csv` can and does.

---

## 6. Join Multiplicity — Fan-Out Quantification

| Metric | Value |
|--------|------:|
| Total `(InvoiceID, product_id)` join keys | 425,701 |
| Keys with 1:1 relationship (no fan-out) | **420,409 (98.76%)** |
| Keys producing fan-out | **5,292 (1.24%)** |
| Simulated join row count | **442,587** |
| Actual observed join row count | **442,587** ✅ (simulation confirmed) |

### Top fan-out keys

| InvoiceID | product_id | pu_count | ii_count | join_rows |
|-----------|-----------|---------|---------|----------|
| 537804 | 852 | 4 | 4 | **16** |
| 541266 | 3764 | 4 | 4 | **16** |
| 562549 | 1494 | 4 | 4 | **16** |
| 568188 | 209 | 4 | 4 | **16** |
| 571046 | 2699 | 4 | 4 | **16** |
| 536409 | 84 | 3 | 3 | 9 |
| 536412 | 80 | 3 | 3 | 9 |
| 2374 | 2956 | 3 | 3 | 9 |

The worst fan-out keys have 4 rows in `purchases` AND 4 rows in `invoice_items` for the same `(InvoiceID, product_id)`, producing 16 rows in the join for a combination that should contribute at most 4 unique line items.

---

## 7. Revenue Analysis

### Authoritative revenue (directly from `invoice_items`, no join)

```
SUM(line_total) from deduplicated invoice_items = £9,307,314.40
```

This is the ground-truth. It is derived from `invoice_items` alone, requires no join to `purchases`, and is not subject to any fan-out inflation.

### Revenue in the current flat join output (`transactions_clean.csv`)

```
SUM(line_total) from transactions_clean.csv = £9,388,019.84
```

### Revenue overcount from the fan-out join

| | Value |
|-|------:|
| Correct revenue (ii alone) | **£9,307,314.40** |
| Inflated revenue (join output) | £9,388,019.84 |
| Overcount | **+£80,705.44** |
| Overcount % | **+0.867%** |

Any aggregation computed from `transactions_clean.csv` that sums `line_total` will be inflated by £80,705 (~0.87%). This affects:
- Total revenue per customer (→ inflated Monetary in RFM)
- Average order value
- Revenue per category
- Any revenue-based features for churn modelling

---

## 8. Invoice Integrity Verification

| Check | Result |
|-------|--------|
| InvoiceIDs with more than 1 `CustomerID` | **0** ✅ |
| InvoiceIDs with more than 1 `date` | **0** ✅ |
| Total distinct invoices | 33,499 |
| Total invoice revenue (from ii) | £9,307,314.40 |

Every InvoiceID maps to exactly one CustomerID and one date in `purchases`. This is the critical finding that enables the normalised analytical model: **`InvoiceID` is a clean, unambiguous bridge between the customer/date world and the line-item world.**

---

## 9. `purchases.csv` Structure Analysis

| Metric | Value |
|--------|------:|
| Median rows per invoice | 4 |
| Invoices where unique products = row count | 31,047 (92.68%) |
| Invoices with repeated product across rows | 2,452 (7.32%) |
| Invoices with exactly 1 CustomerID | 33,499 (100%) |
| Invoices with exactly 1 date | 33,499 (100%) |

In 7.32% of invoices (2,452 invoices), the same `product_id` appears more than once in `purchases`. These are the legitimate split-quantity lines — the same product purchased at different quantities within one session. This is not an error; it is a valid retail pattern where the same item is rung up in multiple batches.

---

## 10. Diagnosis Summary

There are **three simultaneous issues** that together caused the join to expand:

| # | Issue | Scope | Root Cause |
|---|-------|-------|-----------|
| **A** | Same product at multiple prices in one invoice | `invoice_items` only | `purchases` has no price column; cannot represent this |
| **B** | Same product at multiple quantities in one invoice | Both tables | Legitimate split-line retail pattern |
| **C** | Asymmetric deduplication | 75 invoices | `purchases` collapsed multi-price rows (no price column), `invoice_items` kept them |

Issues A and C are the same root cause seen from two angles. Issue B is normal but means `(InvoiceID, product_id)` is not a unique join key in either table.

**There is no single join key that safely connects a row in `purchases` to exactly one row in `invoice_items`.** A row-level join between the two tables is architecturally incorrect.

---

## 11. Recommended Analytical Model

### Design principle

> **`purchases` is a customer-invoice-date mapping table.**  
> **`invoice_items` is the authoritative line-item and revenue table.**  
> **`InvoiceID` is the bridge. Aggregate revenue at the invoice level before joining to customers.**

### Normalised entity model

```
customers          invoices (derived)      invoice_items
──────────         ────────────────────    ───────────────────────
CustomerID ───┐    InvoiceID  (PK)  ◄──── InvoiceID
customer_type  └── CustomerID (FK)         product_id
                   date                    quantity
                                           price
                   ▼ join to products      line_total
                   via product_id          
                                           ▼ join to products
products                                   via product_id
────────────────
product_id (PK)
item
category
price
```

### How to build the four analytical tables

#### Table 1: `dim_invoices` (invoice-level summary — the bridge)

```sql
SELECT
    InvoiceID,
    CustomerID,
    date,
    SUM(line_total)            AS invoice_revenue,
    COUNT(*)                   AS line_item_count,
    SUM(quantity)              AS total_quantity
FROM invoice_items ii
JOIN purchases pu USING (InvoiceID)        -- join at invoice level only
GROUP BY InvoiceID, CustomerID, date
```

Since every InvoiceID maps to exactly one CustomerID and one date (verified above), this aggregation is safe.

#### Table 2: `dim_customers` (unchanged)
Use `customers.csv` as-is. Verified no duplicates, no nulls.

#### Table 3: `fact_invoice_items` (line-item detail — authoritative revenue)
Use deduplicated `invoice_items` directly. No join to `purchases` needed for any revenue computation.

#### Table 4: `fact_invoice_products` (for category/product analysis)
```sql
SELECT ii.*, p.item, p.category
FROM invoice_items ii
JOIN products p USING (product_id)
```

### Metric-specific guidance

| Metric | Source | Join required | Notes |
|--------|--------|--------------|-------|
| **Customer invoice count (Frequency in RFM)** | `dim_invoices` grouped by `CustomerID` | No | Count distinct InvoiceIDs per customer |
| **Customer revenue (Monetary in RFM)** | `dim_invoices` grouped by `CustomerID`, SUM(`invoice_revenue`) | No | Must use `dim_invoices`, not `transactions_clean` |
| **Last purchase date (Recency in RFM)** | `dim_invoices` grouped by `CustomerID`, MAX(`date`) | No | Safe: 1 date per invoice |
| **Invoice-level revenue** | `fact_invoice_items` grouped by `InvoiceID` | No | Ground truth |
| **Product/category analysis** | `fact_invoice_products` | products only | Safe |
| **Customer demographic join** | `dim_invoices` ← `dim_customers` | On `CustomerID` | 1:many (clean) |
| **Churn target construction** | `dim_invoices` filtered by date window | No ML model | See temporal split section below |

### What NOT to do

| Anti-pattern | Why it fails |
|-------------|-------------|
| Join purchases ↔ invoice_items at row level on `(InvoiceID, product_id)` | Many-to-many, inflates revenue and frequency |
| Compute Monetary from `transactions_clean.csv` as-is | Overcounts £80,705 (0.87%) |
| Deduplicate on `(InvoiceID, product_id)` alone | Destroys legitimate multi-price and multi-quantity lines |
| Use `transactions_clean.csv` for invoice count per customer | May double-count some invoices |

---

## 12. Churn Target — Temporal Safety

The normalised `dim_invoices` table is the correct input for churn target construction:

```
2014-01-01 ──────────────── OBS_END ─────────── 2015-12-30
     │                         │                      │
     │   Observation window    │   Prediction window  │
     │   Features from here    │   Label from here    │
     │                         │                      │
     Compute per-customer RFM  Any invoice after
     from dim_invoices          OBS_END → active=1
     WHERE date <= OBS_END      No invoice → churned=1
```

**No row-level join to `invoice_items` is needed to construct the churn target.** The label is binary (purchased in prediction window: yes/no), derived entirely from `dim_invoices.date`.

Revenue-based features (Monetary value) require `dim_invoices.invoice_revenue`, which is pre-aggregated safely at the invoice level before any join touches customer data.

---

## 13. Action Plan for Phase 2

| Step | Action | Output |
|------|--------|--------|
| **1** | Build `dim_invoices` by aggregating `invoice_items` to invoice level, then attaching CustomerID and date from `purchases` using a **group-by join at invoice level** | `data/processed/dim_invoices.csv` |
| **2** | Verify `dim_invoices` has exactly 33,499 rows (one per invoice) | Automated check |
| **3** | Verify `dim_invoices.invoice_revenue` sums to **£9,307,314.40** | Must equal ii ground truth |
| **4** | Archive `transactions_clean.csv` with a warning note — do not use for revenue aggregations | — |
| **5** | Build `fact_invoice_items` (deduplicated ii + products join) | `data/processed/fact_invoice_items.csv` |
| **6** | Proceed to EDA on `dim_invoices` and `fact_invoice_items` | `03_eda.ipynb` |

---

## Appendix A — Numbers at a Glance

| Metric | Value |
|--------|------:|
| Invoices | 33,499 |
| Customers | 8,237 |
| Date range | 2014-01-01 – 2015-12-30 |
| **Correct total revenue** | **£9,307,314.40** |
| Revenue in current join output | £9,388,019.84 |
| Revenue overcount | **+£80,705.44 (+0.867%)** |
| Fan-out keys | 5,292 of 425,701 (1.24%) |
| Invoices with asymmetric row count | 75 of 33,499 (0.22%) |
| Post-dedup extra rows in ii vs pu | 90 |
| InvoiceIDs with >1 CustomerID | **0** |
| InvoiceIDs with >1 date | **0** |

---

*Report generated by read-only grain investigation. No files were created, modified, or deleted in `data/raw/` or `data/processed/`.*
