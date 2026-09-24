# Customer Churn Dataset Report

**Project:** AI-Powered Customer Churn & Retention Analytics  
**File:** `data/processed/customer_churn_dataset.csv`  
**Produced by:** `notebooks/05_customer_features_and_churn.ipynb`  
**Report date:** 2025  
**Status:** Ready for modelling

---

## 1. Overview

| Attribute | Value |
|-----------|-------|
| Total rows (customers) | **5,052** |
| Total columns | **11** |
| Missing values | **0** |
| Duplicate rows | **0** |
| Target column | `Churn_Status` |
| Unique customer identifier | `Customer_ID` |
| Eligible population source | Customers with ≥1 invoice in the observation window |

---

## 2. Churn Window Definition

| Parameter | Date |
|-----------|------|
| Observation start (`OBS_START`) | 2015-01-01 |
| Observation end (`OBS_END`) | 2015-06-30 |
| Prediction window start (`PRED_START`) | 2015-07-01 |
| Churn horizon end (`HORIZON_END`) | 2015-12-27 (OBS_END + 180 days) |
| Last date in dataset (`PRED_END`) | 2015-12-30 |

**Churn definition:**  
A customer is labelled **churned (`Churn_Status = 1`)** if they placed **zero invoices** in the interval `(2015-06-30, 2015-12-27]`.  
A customer is labelled **retained (`Churn_Status = 0`)** if they placed **≥1 invoice** in the same interval.

All RFM features are computed exclusively from data on or before `OBS_END = 2015-06-30`. No information from the prediction window leaks into any feature. All 10 automated leakage checks pass.

---

## 3. Column Definitions

| # | Column | Dtype | Role | Description |
|---|--------|-------|------|-------------|
| 1 | `Customer_ID` | int64 | Identifier | Unique customer key — drop before model training |
| 2 | `Order_Count` | int64 | Feature | Count of distinct invoices in the observation window (alias of `Frequency`) |
| 3 | `Total_Revenue` | float64 | Feature | Sum of invoice revenue in the observation window (alias of `Monetary`) |
| 4 | `Avg_Order_Value` | float64 | Feature | `Total_Revenue / Order_Count` |
| 5 | `First_Purchase` | object (date string) | Feature | Date of the customer's earliest invoice in the observation window |
| 6 | `Last_Purchase` | object (date string) | Feature | Date of the customer's most recent invoice in the observation window |
| 7 | `Recency` | int64 | Feature | Days from `Last_Purchase` to `OBS_END` (2015-06-30). Higher = less recent |
| 8 | `Frequency` | int64 | Feature | Count of distinct invoices in the observation window (same as `Order_Count`) |
| 9 | `Monetary` | float64 | Feature | Sum of invoice revenue in the observation window (same as `Total_Revenue`) |
| 10 | `customer_type` | object (str) | Feature | Customer segment: `private` or `wholesaler` |
| 11 | `Churn_Status` | int64 | **Target** | Binary label: `1` = churned, `0` = retained |

> **Note:** `Order_Count`/`Frequency` and `Total_Revenue`/`Monetary` are intentional duplicates retained for legibility. Remove one of each pair before training to avoid collinearity.

---

## 4. Data Quality

### 4.1 Missing Values

| Column | Missing | % Missing |
|--------|---------|-----------|
| All columns | **0** | **0.0%** |

No imputation required.

### 4.2 Duplicates

| Check | Result |
|-------|--------|
| Duplicate rows | **0** |
| Duplicate `Customer_ID` | **0** |

### 4.3 Value Ranges

| Column | Min | Max | Notes |
|--------|-----|-----|-------|
| `Recency` | 0 | 180 | Bounded by construction (0 = purchased on OBS_END) |
| `Frequency` | 1 | 67 | All customers have ≥1 purchase (eligibility criterion) |
| `Monetary` | £2.19 | £127,410.23 | Extreme right skew — log-transform recommended |
| `Avg_Order_Value` | £2.19 | £77,183.60 | Extreme right skew — log-transform recommended |
| `First_Purchase` | 2015-01-01 | 2015-06-30 | Within obs window |
| `Last_Purchase` | 2015-01-01 | 2015-06-30 | Within obs window |
| `customer_type` | — | — | Only two values: `private`, `wholesaler` |
| `Churn_Status` | 0 | 1 | Binary, no nulls |

---

## 5. Target Variable: `Churn_Status`

### 5.1 Class Distribution

| Label | Count | Share |
|-------|-------|-------|
| `0` — Retained | 3,160 | **62.55%** |
| `1` — Churned | 1,892 | **37.45%** |
| **Total** | **5,052** | 100% |

**Class imbalance ratio:** 1.67 : 1 (retained : churned)

The imbalance is moderate and unlikely to require aggressive resampling (e.g. SMOTE). Standard class-weight adjustments in tree models or `class_weight='balanced'` in logistic regression are sufficient starting points.

### 5.2 Churn Rate by Customer Segment

| Segment | Customers | Churned | Retained | Churn Rate |
|---------|-----------|---------|----------|------------|
| `private` | 4,113 | 1,863 | 2,250 | **45.3%** |
| `wholesaler` | 939 | 29 | 910 | **3.1%** |

Wholesalers churn at **14.7× lower rate** than private customers. `customer_type` will be a highly discriminative feature. Separate models per segment or interaction terms should be explored.

---

## 6. Feature Distributions

### 6.1 Recency (days since last purchase, relative to OBS_END)

| Statistic | Value |
|-----------|-------|
| Mean | 67.9 days |
| Median | 56.0 days |
| Std | 50.4 days |
| Min | 0 |
| Max | 180 |
| Skewness | 0.50 (mild right skew) |

| Percentile | Recency (days) |
|------------|----------------|
| 10th | 9 |
| 25th | 23 |
| 50th | 56 |
| 75th | 106 |
| 90th | 147 |

**Churn rate by recency band:**

| Recency band | Customers | Churn rate |
|-------------|-----------|------------|
| 0–30 days | 1,483 | 27.0% |
| 31–60 days | 1,103 | 33.8% |
| 61–90 days | 749 | 40.6% |
| 91–120 days | 667 | 45.1% |
| 121–150 days | 552 | 49.8% |
| 151–180 days | 428 | 53.0% |

Strong monotonic relationship: churn rate nearly doubles from the most-recent to least-recent band.

### 6.2 Frequency (order count)

| Statistic | Value |
|-----------|-------|
| Mean | 2.16 |
| Median | 1 |
| Std | 2.95 |
| Min | 1 |
| Max | 67 |
| Skewness | 9.70 (extreme right skew) |

54.1% of customers placed exactly one order in the observation window.

**Churn rate by frequency band:**

| Frequency band | Customers | Churn rate |
|----------------|-----------|------------|
| 1 order | 2,734 | 46.5% |
| 2 orders | 1,240 | 35.4% |
| 3–5 orders | 818 | 21.4% |
| 6–10 orders | 183 | 4.4% |
| 11+ orders | 77 | **0.0%** |

Frequency is strongly inversely correlated with churn. No customer with ≥11 orders in the obs window churned.

### 6.3 Monetary (total spend in obs window, £)

| Statistic | Value |
|-----------|-------|
| Mean | £699 |
| Median | £136 |
| Std | £3,416 |
| Min | £2.19 |
| Max | £127,410 |
| Skewness | 20.74 (extreme right skew) |

| Percentile | Monetary |
|------------|----------|
| 10th | £21 |
| 25th | £43 |
| 50th | £136 |
| 75th | £554 |
| 90th | £1,400 |

Top 10% of customers account for **66.7%** of total observation-window revenue.

### 6.4 Average Order Value (£)

| Statistic | Value |
|-----------|-------|
| Mean | £238.81 |
| Median | £108.26 |
| Std | £1,172 |
| Min | £2.19 |
| Max | £77,183.60 |
| Skewness | 56.85 (extreme right skew) |

### 6.5 Customer Type

| Value | Count | Share |
|-------|-------|-------|
| `private` | 4,113 | 81.4% |
| `wholesaler` | 939 | 18.6% |

Wholesalers account for only 18.6% of customers but generate an estimated **74.4% of observation-window revenue** (£2,628,025 vs £903,399 for private).

---

## 7. Revenue Concentration

| Metric | Value |
|--------|-------|
| Total obs-window revenue | £3,531,423 |
| Private customers revenue | £903,399 (25.6%) |
| Wholesaler revenue | £2,628,025 (74.4%) |
| Top 10% customer revenue share | 66.7% |
| Customers with 1 order | 2,734 (54.1%) |
| Churn rate for 1-order customers | 46.5% |

---

## 8. Leakage Safety Assessment

All 10 automated leakage checks pass. Key guarantees:

| Check | Result |
|-------|--------|
| No feature uses data after 2015-06-30 | ✅ PASS |
| `Recency` computed from `Last_Purchase ≤ OBS_END` | ✅ PASS |
| `Frequency` counts invoices `≤ OBS_END` only | ✅ PASS |
| `Monetary` sums revenue `≤ OBS_END` only | ✅ PASS |
| `Last_Purchase` max = 2015-06-30 | ✅ PASS |
| `First_Purchase` min = 2015-01-01 | ✅ PASS |
| Churn label derived from prediction window only | ✅ PASS |
| No prediction-window dates appear in any feature | ✅ PASS |
| `Recency` range consistent with [0, 180] | ✅ PASS |
| No future invoice counts appear in feature set | ✅ PASS |

---

## 9. Recommendations for Modelling

### 9.1 Pre-processing

| Step | Recommendation |
|------|----------------|
| Drop columns | `Customer_ID`, `First_Purchase`, `Last_Purchase`, `Total_Revenue` (alias of `Monetary`), `Order_Count` (alias of `Frequency`) |
| Log-transform | `Monetary`, `Avg_Order_Value`, `Frequency` — all have skewness > 9 |
| Encode `customer_type` | Binary encode: `wholesaler = 1`, `private = 0` |
| Scale numerics | StandardScaler or RobustScaler post log-transform |
| Class imbalance | Use `class_weight='balanced'` (sklearn) or `scale_pos_weight` (XGBoost) |

### 9.2 Recommended Model Sequence

1. **Logistic Regression (L2)** — baseline interpretable model
2. **Random Forest** — handles skewed features and non-linearity well
3. **Gradient Boosting (XGBoost / LightGBM)** — likely best performer given feature skew and segment heterogeneity
4. **Segment-specific models** — consider separate models for `private` and `wholesaler` given the 14.7× difference in churn rates

### 9.3 Evaluation Metrics

Given the moderate class imbalance (1.67:1) and the business cost asymmetry (missing a churner costs more than a false alarm):

- **Primary:** ROC-AUC
- **Secondary:** F1-score (churned class), Precision-Recall AUC
- **Business metric:** Expected revenue at risk from predicted churners

### 9.4 Split Strategy

| Split | Proportion | Method |
|-------|------------|--------|
| Train | 70% | Stratified by `Churn_Status` |
| Validation | 15% | Stratified by `Churn_Status` |
| Test | 15% | Stratified by `Churn_Status` — hold out until final evaluation |

Stratification by `customer_type` in addition to `Churn_Status` is advisable given the extreme segment difference in churn rates.

---

## 10. Known Limitations

1. **Single obs window:** The churn label is derived from one 6-month observation window (Jan–Jun 2015). The model may not generalise to different seasonal periods.
2. **No product-level features:** The current feature set is RFM-only. Product category, diversity of purchases, and return rates are not yet included.
3. **No customer demographics:** Apart from `customer_type`, no age, geography, or acquisition-channel data is available.
4. **Wholesaler leakage risk (business logic):** Wholesalers have a 3.1% churn rate. A naive model may learn to always predict "retained" for wholesalers. Separate treatment is strongly recommended.
5. **Alias columns:** `Order_Count` = `Frequency` and `Total_Revenue` = `Monetary`. These will cause collinearity if both are included in a linear model. Remove one of each pair.
6. **`First_Purchase` / `Last_Purchase` as raw dates:** These should be converted to derived numeric features (e.g. `tenure_days = (Last_Purchase - First_Purchase).days`) before use in tree models. Raw date strings must not be passed directly.

---

## 11. File Provenance

| Source file | Role |
|-------------|------|
| `data/processed/dim_invoices.csv` | Invoice dates and revenue (authoritative join key) |
| `data/processed/fact_invoice_items.csv` | Line-item revenue (authoritative revenue source) |
| `data/processed/dim_customers.csv` | Customer type |
| `data/processed/customer_churn_dataset.csv` | **This file — final churn dataset** |

Revenue figures use `invoice_revenue` from `dim_invoices`, which is derived from `SUM(line_total)` in `fact_invoice_items`. The broken `transactions_clean.csv` (revenue inflated by £80,705 due to many-to-many join fan-out) was **not used** at any stage of this dataset construction.

---

*End of report.*
