# Data Model — AI-Powered Customer Churn & Retention Analytics

> **Status:** Normalised analytical layer verified. All 19 integrity checks PASS.  
> **Authoritative revenue:** £9,307,314.40  
> **Source:** Dataset A (customers, purchases, invoice_items, products)  
> **Raw files:** untouched in `data/raw/`

---

## 1. Table Inventory

| Table | File | Grain | Rows | Columns |
|-------|------|-------|-----:|--------:|
| `dim_invoices` | `data/processed/dim_invoices.csv` | One row per InvoiceID | 33,499 | 5 |
| `fact_invoice_items` | `data/processed/fact_invoice_items.csv` | One row per line-item record | 431,263 | 7 |
| `dim_customers` | `data/processed/dim_customers.csv` | One row per CustomerID | 8,237 | 2 |
| `dim_products` | `data/processed/dim_products.csv` | One row per product_id | 4,033 | 4 |

---

## 2. Table Schemas and Grain

### `dim_invoices`

**Grain:** One row per unique `InvoiceID`.

| Column | Type | Description |
|--------|------|-------------|
| `InvoiceID` | int64 | **Primary key** — unique invoice identifier |
| `CustomerID` | int64 | FK → `dim_customers.CustomerID` |
| `date` | datetime | Date of the invoice (from purchases) |
| `invoice_revenue` | float64 | `SUM(line_total)` from invoice_items for this invoice |
| `line_item_count` | int64 | Count of line items in invoice_items for this invoice |

**Source logic:**
1. Deduplicate `purchases.csv` (removes 5,516 exact rows).
2. Group by `InvoiceID`, take `.first()` of CustomerID and date (verified: each invoice maps to exactly 1 of each).
3. Separately aggregate `invoice_items.csv` by `InvoiceID` → `SUM(line_total)` + `COUNT`.
4. Merge the two aggregations on `InvoiceID` only.

---

### `fact_invoice_items`

**Grain:** One row per legitimate invoice line-item record.

| Column | Type | Description |
|--------|------|-------------|
| `InvoiceID` | int64 | FK → `dim_invoices.InvoiceID` |
| `product_id` | int64 | FK → `dim_products.product_id` |
| `quantity` | int64 | Units purchased on this line |
| `price` | float64 | Unit price on this line |
| `line_total` | float64 | `quantity × price` (authoritative revenue field) |
| `item` | string | Product name (from `dim_products`) |
| `category` | string | Product category (from `dim_products`) |

**Source logic:**
1. Deduplicate `invoice_items.csv` (removes 5,426 exact rows → 431,263 rows remain).
2. Left-join `dim_products` on `product_id` to enrich with `item` and `category`.
3. **Do not collapse** rows where `(InvoiceID, product_id)` repeats — these are legitimate multi-price or multi-quantity lines within one invoice.

---

### `dim_customers`

**Grain:** One row per unique `CustomerID`.

| Column | Type | Description |
|--------|------|-------------|
| `CustomerID` | int64 | **Primary key** |
| `customer_type` | string | `private` (86.9%) or `wholesaler` (13.1%) |

**Source:** `customers.csv` — no duplicates, no nulls, used as-is.

---

### `dim_products`

**Grain:** One row per unique `product_id`.

| Column | Type | Description |
|--------|------|-------------|
| `product_id` | int64 | **Primary key** |
| `item` | string | Free-text product name |
| `category` | string | One of 25 product categories |
| `price` | float64 | Catalogue unit price |

**Source:** `products.csv` — no duplicates, no nulls, used as-is.

---

## 3. Primary Keys

| Table | Primary Key |
|-------|------------|
| `dim_invoices` | `InvoiceID` |
| `fact_invoice_items` | *(composite)* `(InvoiceID, product_id, quantity, price, line_total)` |
| `dim_customers` | `CustomerID` |
| `dim_products` | `product_id` |

`fact_invoice_items` has no single-column surrogate key. The 5-column composite uniquely identifies every row. For ML pipelines, a row-number index may be added but must not be used as a join key.

---

## 4. Foreign Keys

| Table | Column | References | Verified |
|-------|--------|-----------|---------|
| `dim_invoices` | `CustomerID` | `dim_customers.CustomerID` | ✅ 0 orphans |
| `fact_invoice_items` | `InvoiceID` | `dim_invoices.InvoiceID` | ✅ 0 orphans |
| `fact_invoice_items` | `product_id` | `dim_products.product_id` | ✅ 0 orphans |

All foreign key constraints hold. Verified by `notebooks/03_data_model_validation.ipynb`.

---

## 5. Entity-Relationship Diagram

```
dim_customers                dim_invoices                fact_invoice_items
─────────────                ────────────                ──────────────────
CustomerID (PK) ◄──────────  CustomerID (FK)             InvoiceID (FK) ──────►  dim_invoices
customer_type                InvoiceID (PK) ◄────────── InvoiceID
                             date                        product_id (FK) ───────► dim_products
                             invoice_revenue             quantity
                             line_item_count             price
                                                         line_total
                                                         item
                                                         category

dim_products
────────────
product_id (PK)
item
category
price
```

**Cardinalities:**
- `dim_customers` → `dim_invoices`: 1:many (one customer, many invoices)
- `dim_invoices` → `fact_invoice_items`: 1:many (one invoice, many line items)
- `dim_products` → `fact_invoice_items`: 1:many (one product, many line-item appearances)

---

## 6. Why `purchases` and `invoice_items` Must Not Be Joined at Row Level

### The grain mismatch

`purchases.csv` records `(InvoiceID, CustomerID, date, product_id, quantity)`.  
Its unique grain is `(InvoiceID, product_id, quantity)`.

`invoice_items.csv` records `(InvoiceID, product_id, quantity, price, line_total)`.  
Its unique grain is `(InvoiceID, product_id, quantity, price, line_total)`.

**The difference:** `purchases` has no `price` column. When the same product appears in one invoice at two different price points (a legitimate retail scenario — e.g. volume discounts applied mid-order), `invoice_items` stores two rows while `purchases` stores one (it cannot distinguish them). Deduplicating each file independently preserves this asymmetry.

### The fan-out arithmetic

Joining on `(InvoiceID, product_id)` — the shared key — creates a Cartesian product for any invoice-product combination where either table has more than one row:

```
purchases has 2 rows for (invoice X, product Y)
invoice_items has 3 rows for (invoice X, product Y)
→  join produces 2 × 3 = 6 rows
```

Across 5,292 such keys, this expands the dataset from 431,173 rows to **442,587 rows (+2.65%)** and inflates total revenue by **£80,705 (+0.87%)**.

### The safe pattern

```python
# ✅ CORRECT: aggregate first, join second
invoice_rev = invoice_items.groupby('InvoiceID')['line_total'].sum()
dim_invoices = purchases_deduped.groupby('InvoiceID').first()
dim_invoices = dim_invoices.join(invoice_rev)

# ❌ WRONG: row-level join
transactions = purchases.merge(invoice_items, on=['InvoiceID','product_id'])
```

---

## 7. Revenue Calculation Rule

**Always derive revenue from `fact_invoice_items.line_total`.** Never from a joined flat table.

```python
# Customer-level revenue (Monetary for RFM)
customer_revenue = (
    fact_invoice_items
    .groupby('InvoiceID')['line_total']
    .sum()
    .rename('invoice_revenue')
    .reset_index()
    .merge(dim_invoices[['InvoiceID','CustomerID']], on='InvoiceID')
    .groupby('CustomerID')['invoice_revenue']
    .sum()
)

# Or equivalently (using the pre-aggregated dim_invoices):
customer_revenue = dim_invoices.groupby('CustomerID')['invoice_revenue'].sum()
```

**Validated totals:**
- `SUM(line_total)` from `fact_invoice_items`: **£9,307,314.40**
- `SUM(invoice_revenue)` from `dim_invoices`: **£9,307,314.40**
- Difference: **£0.00**

---

## 8. How Frequency (RFM) Will Be Calculated

```python
# Number of distinct invoices per customer
frequency = (
    dim_invoices
    .groupby('CustomerID')['InvoiceID']
    .nunique()
    .rename('frequency')
)
```

**Important:** Use `nunique()` on `InvoiceID`, not `count()` on rows. This prevents any inflated count if the dim_invoices table were ever modified to add multiple rows per invoice (it should not be, but the pattern is safer).

**Source:** `dim_invoices` only. No join to `fact_invoice_items` required.

---

## 9. How Monetary Value (RFM) Will Be Calculated

```python
# Total customer spend
monetary = (
    dim_invoices
    .groupby('CustomerID')['invoice_revenue']
    .sum()
    .rename('monetary')
)
```

**Source:** `dim_invoices.invoice_revenue` (pre-aggregated from `fact_invoice_items`).  
Do not re-aggregate from `fact_invoice_items` in a join path through `dim_invoices` — this would re-introduce the fan-out risk if any join is accidentally added upstream.

For **observation-window-safe RFM**, filter `dim_invoices` by date before aggregating:

```python
# Example: observation window ends 2015-06-30
obs_end = pd.Timestamp('2015-06-30')
obs_invoices = dim_invoices[dim_invoices['date'] <= obs_end]
monetary_obs = obs_invoices.groupby('CustomerID')['invoice_revenue'].sum()
```

---

## 10. How Product/Category Analysis Will Be Calculated

```python
# Revenue by category
category_revenue = (
    fact_invoice_items
    .groupby('category')['line_total']
    .sum()
    .sort_values(ascending=False)
)

# Number of invoices per category (distinct purchases)
category_invoices = (
    fact_invoice_items
    .groupby(['InvoiceID','category'])
    .size()
    .reset_index()
    .groupby('category')['InvoiceID']
    .nunique()
)
```

**Source:** `fact_invoice_items` (already enriched with `item` and `category` from `dim_products`).  
No join required — both columns are present in the fact table.

For customer-level product affinity (useful for churn features):

```python
# Categories purchased per customer
cust_category = (
    fact_invoice_items
    .merge(dim_invoices[['InvoiceID','CustomerID']], on='InvoiceID')
    .groupby(['CustomerID','category'])
    .agg(spend=('line_total','sum'), quantity=('quantity','sum'))
)
```

---

## 11. Temporal Cut-off for Churn Target (Reference)

> No churn labels are created yet. This section documents the intended pattern only.

```
2014-01-01 ──────────────── OBS_END ─────────── 2015-12-30
     │                         │                      │
     │   Observation window    │   Prediction window  │
     │   Features from here    │   Label from here    │
```

The exact `OBS_END` date will be selected during EDA (Phase 2), based on the transaction volume distribution across months. Candidate values: 2015-06-30 (18m obs / 6m pred), 2015-03-31 (15m obs / 9m pred), 2014-12-31 (12m obs / 12m pred).

All feature engineering and churn label construction uses `dim_invoices` filtered by date. Revenue features use `dim_invoices.invoice_revenue`. Product features join `dim_invoices` → `fact_invoice_items` at the invoice level.

---

## Appendix — Files Created by This Phase

| File | Description |
|------|-------------|
| `data/processed/dim_invoices.csv` | 33,499 rows — one per invoice |
| `data/processed/fact_invoice_items.csv` | 431,263 rows — one per line item |
| `data/processed/dim_customers.csv` | 8,237 rows — one per customer |
| `data/processed/dim_products.csv` | 4,033 rows — one per product |
| `data/processed/cleaning_report.json` | Phase 1 cleaning audit trail |
| `src/data_model.py` | Pipeline to build and validate the four tables |
| `notebooks/03_data_model_validation.ipynb` | Executed validation notebook |
| `reports/data_model_validation_report.md` | Human-readable validation report |
| `JOIN_GRAIN_INVESTIGATION.md` | Full grain investigation findings |

---

*Data model version 1.0 — Phase 1 complete. Ready for Phase 2: EDA.*
