# Dataset Profile — AI-Powered Customer Churn & Retention Analytics

> **Read-only analysis. No dataset was modified, cleaned, deleted, transformed, or renamed.**

---

## 1. Dataset Inventory

| # | Filename | Rows | Columns |
|---|----------|-----:|--------:|
| 1 | `customers.csv` | 8,237 | 2 |
| 2 | `invoice_items.csv` | 436,689 | 5 |
| 3 | `products.csv` | 4,033 | 4 |
| 4 | `purchases.csv` | 436,689 | 5 |
| 5 | `Retail_Transaction_Dataset.csv` | 100,000 | 10 |

---

## 2. Column Catalogue

### 2.1 `customers.csv`

| Column | Data Type | Missing | Unique Values | Notes |
|--------|-----------|--------:|--------------|-------|
| `CustomerID` | int64 | 0 | 8,237 | Primary key |
| `customer_type` | string | 0 | 2 | `private` (7,161) / `wholesaler` (1,076) |

---

### 2.2 `invoice_items.csv`

| Column | Data Type | Missing | Unique Values | Notes |
|--------|-----------|--------:|--------------|-------|
| `InvoiceID` | int64 | 0 | 33,499 | Foreign key → purchases |
| `product_id` | int64 | 0 | 4,033 | Foreign key → products |
| `quantity` | int64 | 0 | 302 | All ≥ 0 |
| `price` | float64 | 0 | 548 | Range: 0.00 – 8,142.75 |
| `line_total` | float64 | 0 | 3,177 | Pre-computed; all ≥ 0 |

---

### 2.3 `products.csv`

| Column | Data Type | Missing | Unique Values | Notes |
|--------|-----------|--------:|--------------|-------|
| `product_id` | int64 | 0 | 4,033 | Primary key |
| `item` | string | 0 | 4,033 | Free-text product name |
| `category` | string | 0 | 25 | See category breakdown below |
| `price` | float64 | 0 | 281 | All ≥ 0 |

**Product categories (25 total):**

| Category | Count | Category | Count |
|----------|------:|----------|------:|
| Kitchen & Dining | 863 | Seasonal | 215 |
| Home Decor | 758 | Garden & Outdoor | 160 |
| Apparel & Accessories | 642 | Miscellaneous | 39 |
| Stationery & Craft | 339 | Dairy | 18 |
| Toys & Games | 330 | Beverages | 17 |
| Health, Beauty & Personal Care | 291 | Administrative | 16 |
| Party & Festive | 247 | Bakery & Snacks | 16 |
| Produce | 15 | Condiments & Spices | 15 |
| Meat | 11 | Cleaning & Hygiene | 10 |
| Personal Care | 7 | Household | 6 |
| DIY & Tools | 5 | Pantry | 4 |
| Gardening | 3 | Pet Care | 3 |
| Kitchen | 3 | | |

---

### 2.4 `purchases.csv`

| Column | Data Type | Missing | Unique Values | Notes |
|--------|-----------|--------:|--------------|-------|
| `InvoiceID` | int64 | 0 | 33,499 | Transaction identifier |
| `date` | string (YYYY-MM-DD) | 0 | 728 | Parses cleanly to datetime |
| `CustomerID` | int64 | 0 | 8,237 | Foreign key → customers |
| `product_id` | int64 | 0 | 4,033 | Foreign key → products |
| `quantity` | int64 | 0 | 302 | All ≥ 0 |

---

### 2.5 `Retail_Transaction_Dataset.csv`

| Column | Data Type | Missing | Unique Values | Notes |
|--------|-----------|--------:|--------------|-------|
| `CustomerID` | int64 | 0 | 95,215 | Customer identifier |
| `ProductID` | string | 0 | 4 | Single-letter codes: A, B, C, D |
| `Quantity` | int64 | 0 | 9 | All ≥ 0 |
| `Price` | float64 | 0 | 100,000 | Near-continuous; all ≥ 0 |
| `TransactionDate` | string (M/D/YYYY H:MM) | 0 | 91,025 | Parses cleanly to datetime |
| `PaymentMethod` | string | 0 | 4 | Cash, PayPal, Debit Card, Credit Card |
| `StoreLocation` | string | 0 | 100,000 | Full street address; near-unique per row |
| `ProductCategory` | string | 0 | 4 | Books, Clothing, Electronics, Home Decor |
| `DiscountApplied(%)` | float64 | 0 | 100,000 | Range: ~0.00 – ~20.00 |
| `TotalAmount` | float64 | 0 | 99,998 | Pre-computed; all ≥ 0 |

---

## 3. Missing Values Summary

| File | Columns with Missing Values |
|------|-----------------------------|
| `customers.csv` | **None** |
| `invoice_items.csv` | **None** |
| `products.csv` | **None** |
| `purchases.csv` | **None** |
| `Retail_Transaction_Dataset.csv` | **None** |

No null values detected across any file.

---

## 4. Duplicate Rows

| File | Duplicate Rows |
|------|---------------:|
| `customers.csv` | 0 |
| `invoice_items.csv` | **5,426** |
| `products.csv` | 0 |
| `purchases.csv` | **5,516** |
| `Retail_Transaction_Dataset.csv` | 0 |

`invoice_items.csv` and `purchases.csv` share the same 436,689 row count and carry overlapping duplicate counts (~5,400–5,500 rows). These duplicates likely represent the same line-item repeated and should be investigated before feature engineering.

---

## 5. Key Column Classifications

### 5.1 Unique Customer Identifier

| File | Column | Unique Count |
|------|--------|-------------:|
| `customers.csv` | `CustomerID` | 8,237 (PK) |
| `purchases.csv` | `CustomerID` | 8,237 |
| `Retail_Transaction_Dataset.csv` | `CustomerID` | 95,215 |

The two datasets use **disjoint `CustomerID` spaces** — they cannot be joined.

---

### 5.2 Transaction / Order Identifier

| File | Column | Unique Count |
|------|--------|-------------:|
| `invoice_items.csv` | `InvoiceID` | 33,499 |
| `purchases.csv` | `InvoiceID` | 33,499 |
| `Retail_Transaction_Dataset.csv` | *(none)* | — |

`Retail_Transaction_Dataset.csv` has no explicit transaction or order ID column.

---

### 5.3 Date / Time Columns

| File | Column | Parsed Range | Granularity |
|------|--------|--------------|-------------|
| `purchases.csv` | `date` | 2014-01-01 – 2015-12-30 | Day |
| `Retail_Transaction_Dataset.csv` | `TransactionDate` | 2023-04-29 – 2024-04-28 | Minute |

Both columns parse without error. The two date ranges do not overlap and represent separate time windows.

---

### 5.4 Revenue / Sales-Related Columns

| File | Column | Description |
|------|--------|-------------|
| `invoice_items.csv` | `price` | Unit price per line item |
| `invoice_items.csv` | `line_total` | `quantity × price` (pre-computed) |
| `products.csv` | `price` | Catalogue price per product |
| `Retail_Transaction_Dataset.csv` | `Price` | Unit price (near-continuous distribution) |
| `Retail_Transaction_Dataset.csv` | `DiscountApplied(%)` | Discount percentage (0–20%) |
| `Retail_Transaction_Dataset.csv` | `TotalAmount` | Final amount after discount |

`purchases.csv` itself contains **no price or revenue column** — revenue must be derived by joining to `invoice_items.csv`.

---

### 5.5 Product / Category Columns

| File | Column | Cardinality |
|------|--------|------------:|
| `products.csv` | `product_id` | 4,033 |
| `products.csv` | `item` | 4,033 (free text) |
| `products.csv` | `category` | 25 categories |
| `invoice_items.csv` | `product_id` | 4,033 |
| `purchases.csv` | `product_id` | 4,033 |
| `Retail_Transaction_Dataset.csv` | `ProductID` | 4 (A/B/C/D — opaque codes) |
| `Retail_Transaction_Dataset.csv` | `ProductCategory` | 4 categories |

The `ProductID` values in `Retail_Transaction_Dataset.csv` (A/B/C/D) are **not mappable** to the `product_id` integers in `products.csv`.

---

### 5.6 Customer Demographic / Segmentation Columns

| File | Column | Values |
|------|--------|--------|
| `customers.csv` | `customer_type` | `private` (86.9%) / `wholesaler` (13.1%) |
| `Retail_Transaction_Dataset.csv` | `PaymentMethod` | Cash, PayPal, Debit Card, Credit Card |
| `Retail_Transaction_Dataset.csv` | `StoreLocation` | Full street address (near-unique, likely synthetic) |

No age, gender, income, geography (structured), or loyalty-tier columns exist in either dataset.

---

## 6. Churn / Retention Label

**No pre-existing churn or retention label exists in any file.**

A churn target must be engineered from historical transaction behaviour.

---

## 7. Historical Transaction Coverage for Leakage-Safe Churn Target

### Dataset A — `purchases.csv` + `customers.csv` + `invoice_items.csv` + `products.csv`

| Attribute | Value |
|-----------|-------|
| Date range | 2014-01-01 – 2015-12-30 (**24 months**) |
| Unique customers | 8,237 |
| Unique invoices | 33,499 |
| Total line items | 436,689 |
| Monthly active customers | 573 – 2,227 |

**Assessment — SUFFICIENT for churn target construction.**

24 months of daily transaction history enables:
- An observation window (e.g. first 12–18 months) to engineer RFM and behavioural features.
- A prediction window (e.g. last 3–6 months) to label whether a customer made any purchase.
- A clean temporal split between features and labels with no look-ahead leakage.

### Dataset B — `Retail_Transaction_Dataset.csv`

| Attribute | Value |
|-----------|-------|
| Date range | 2023-04-29 – 2024-04-28 (**~12 months**) |
| Unique customers | 95,215 |
| Customers with 1 transaction only | **90,594 (95.1%)** |
| Customers with 2+ transactions | 4,621 (4.9%) |
| Max transactions per customer | 4 |
| Total transactions | 100,000 |

**Assessment — INSUFFICIENT for a reliable churn target.**

95.1% of customers appear exactly once in 12 months. With near-zero repeat behaviour it is impossible to distinguish true churners from one-time buyers, and there is not enough longitudinal depth to construct a meaningful observation/prediction window split. Any churn label derived from this file would be dominated by spurious single-purchase "churners."

---

## 8. Referential Integrity Check (Dataset A)

| Check | Result |
|-------|--------|
| `purchases.CustomerID` → `customers.CustomerID` | ✅ 0 orphan rows |
| `purchases.InvoiceID` ↔ `invoice_items.InvoiceID` | ✅ Perfect match (0 unmatched) |
| Row count per invoice consistent across both files | ✅ 0 mismatches |
| `purchases.product_id` → `products.product_id` | (Not checked; same 4,033 unique values in both) |

The four files forming Dataset A are **fully referentially consistent**.

---

## 9. Potential Data-Quality Problems

| # | File(s) | Issue | Severity |
|---|---------|-------|----------|
| DQ-1 | `invoice_items.csv`, `purchases.csv` | **~5,400–5,500 exact duplicate rows.** Could inflate transaction counts, RFM metrics, and revenue features if not deduplicated before modelling. | ⚠️ High |
| DQ-2 | `invoice_items.csv` | `price = 0.00` for some rows (min price is 0.0). Zero-price line items may represent cancelled lines, promotional giveaways, or data errors. | ⚠️ Medium |
| DQ-3 | `Retail_Transaction_Dataset.csv` | `ProductID` values are opaque single-letter codes (A/B/C/D) with no lookup table in the dataset. Semantics are unknown. | ⚠️ Medium |
| DQ-4 | `Retail_Transaction_Dataset.csv` | `StoreLocation` is a fully unique free-text address per row (100,000 distinct values). Almost certainly synthetically generated. Not usable as a meaningful geographic segment without geocoding. | ⚠️ Medium |
| DQ-5 | `Retail_Transaction_Dataset.csv` | `Price` and `DiscountApplied(%)` both have 100,000 unique values (effectively continuous random draws). This statistical signature strongly suggests synthetic/randomly generated data, limiting real-world generalisation. | ⚠️ Medium |
| DQ-6 | `products.csv` | Category taxonomy is inconsistent: overlapping categories `Personal Care` vs `Health, Beauty & Personal Care`, `Kitchen` vs `Kitchen & Dining`, `Gardening` vs `Garden & Outdoor`. May cause fragmented category features. | ⚠️ Low–Medium |
| DQ-7 | `purchases.csv` | No revenue/price column. Customer-level spend must always be derived by joining through `invoice_items.csv`; a missing join step silently produces spend = 0. | ℹ️ Structural |
| DQ-8 | `customers.csv` | Only 2 columns. Extremely sparse customer profile with no demographic, geographic, or tenure information beyond `customer_type`. | ℹ️ Structural |
| DQ-9 | Dataset A vs Dataset B | `CustomerID` spaces are disjoint. The two datasets cannot be merged or cross-referenced. They must be treated as independent analytical datasets. | ℹ️ Structural |

---

## 10. Potential Target Leakage Risks

| # | Risk | Affected Dataset | Description |
|---|------|-----------------|-------------|
| TL-1 | **Using `line_total` as a feature without time-gating** | Dataset A | `line_total` in `invoice_items.csv` is a transaction-level field. If rows from the prediction window are included in feature aggregations, future revenue leaks into the model. Always filter to the observation window before aggregating. |
| TL-2 | **Duplicate rows inflating recency/frequency signals** | Dataset A | The ~5,426 duplicate rows in `invoice_items.csv` will inflate `frequency` and `monetary` RFM dimensions. Duplicates must be removed *before* the churn target is defined, not after, to avoid biasing the label. |
| TL-3 | **Using the last transaction date to define both features and the churn label** | Dataset A & B | A common pattern is: last purchase date → recency feature + churn label. If the same date field is used for both without strict cut-off discipline, the model learns to predict itself. A hard observation cut-off date must be fixed and the label defined solely from dates *after* that cut-off. |
| TL-4 | **`TotalAmount` / `DiscountApplied(%)` as-is features** | Dataset B | These are transaction-level columns recorded *at the time of purchase*. They cannot be used as pre-transaction features. They can only be historical aggregates computed over the observation window. |
| TL-5 | **Near-universal single-transaction customers producing trivial churn label** | Dataset B | If a churn label is constructed from `Retail_Transaction_Dataset.csv`, 95.1% of customers will be labelled "churned" by design (only 1 transaction). A classifier trained on such a target learns little about true churn behaviour and will trivially achieve ~95% accuracy by predicting "churned" for everyone. |
| TL-6 | **Price column in `products.csv` vs `invoice_items.csv`** | Dataset A | `products.csv` stores catalogue prices; `invoice_items.csv` stores actual transaction prices. Using catalogue price as a proxy for realised revenue without verification introduces subtle leakage if catalogue prices were updated after the observation window ended. |

---

## 11. Recommended Primary Dataset for Churn Modelling

**Dataset A** (`purchases.csv` + `invoice_items.csv` + `products.csv` + `customers.csv`) is the recommended foundation:

- 24 months of history (2014–2015) with 8,237 customers and 33,499 invoices.
- Fully referentially consistent across all four files.
- Rich enough to support observation / prediction window splits (e.g. 18-month obs / 6-month pred).
- Contains revenue, product category, and customer-type signals for feature engineering.

**Dataset B** (`Retail_Transaction_Dataset.csv`) is unsuitable as a standalone churn dataset due to extremely sparse repeat purchasing (95.1% single-transaction customers). It may be used for supplementary exploratory analysis only.

---

*Profile generated by read-only static analysis. No files were created, modified, or deleted in `data/raw/`.*
