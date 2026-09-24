# AI-Powered Customer Churn Analytics

An end-to-end data analytics and machine learning project that analyses customer purchasing behaviour for a UK-based e-commerce retailer, identifies customers at higher risk of churn, and supports data-driven retention decisions.

---

## 1. Project Overview

This project follows the internship Masterclass workflow across three phases:

| Phase | Scope |
|-------|-------|
| **MC1 — Data** | Data understanding, cleaning, grain investigation, normalised data model |
| **MC2 — EDA** | Exploratory data analysis, five insights, three hypotheses, three recommendations |
| **MC3 — Prediction** | RFM feature engineering, 180-day churn target, Logistic Regression model, risk scoring |

The analytical pipeline moves from raw transaction CSVs to a scored, risk-segmented customer dataset ready for business action.

---

## 2. Problem Statement

The retailer sells across 25 product categories through two customer segments: private customers and wholesalers. Wholesalers represent 13.1% of the customer base but generate 73.6% of total revenue — an 18.5× per-customer revenue differential. The business has no existing mechanism to identify which customers are at risk of not returning before they stop purchasing.

This project addresses that gap: using historical purchasing data, it assigns each customer a churn probability and places them into a risk tier, enabling proactive rather than reactive retention actions.

---

## 3. Objectives

1. Clean and validate raw retail transaction data without modifying source files
2. Build a normalised analytical data model (star schema) from four raw CSVs
3. Understand customer and product behaviour through exploratory data analysis
4. Identify five key business insights, three hypotheses, and three recommendations
5. Engineer RFM (Recency, Frequency, Monetary) features from a defined observation window
6. Construct a leakage-safe binary churn target using a strict 180-day prediction horizon
7. Train a Logistic Regression churn prediction model
8. Score all customers with predicted churn probability
9. Segment customers into High / Medium / Low risk tiers
10. Quantify revenue at risk within each tier

---

## 4. Dataset

The project uses four raw CSV files from a UK-based e-commerce retailer (2014–2015):

| File | Rows | Key columns |
|------|------|-------------|
| `customers.csv` | 8,237 | CustomerID, customer_type |
| `purchases.csv` | 436,689 | InvoiceID, date, CustomerID, product_id, quantity |
| `invoice_items.csv` | 436,689 | InvoiceID, product_id, quantity, price, line_total |
| `products.csv` | 4,033 | product_id, item, category, price |

**Dataset source:** This dataset was provided as part of the internship programme (Dataset A). It covers transactions from 2014-01-01 to 2015-12-30 across 25 product categories.

**Important:** `data/raw/` is read-only throughout the project. All derived tables are written to `data/processed/`.

---

## 5. Data Architecture

Raw files are not joined at row level. Instead, a normalised star schema is built:

```
fact_invoice_items  ──→  dim_invoices  ──→  dim_customers
        │
        └──────────────→  dim_products
```

| Table | Grain | Purpose |
|-------|-------|---------|
| `dim_invoices` | One row per invoice | Invoice date, customer link, revenue total |
| `dim_customers` | One row per customer | Customer type (private / wholesaler) |
| `dim_products` | One row per product | Product name, category, price |
| `fact_invoice_items` | One row per line item | Authoritative revenue (`line_total`) |

**Why `purchases.csv` and `invoice_items.csv` are not joined row-by-row:**
Joining these two files on `(InvoiceID, product_id)` creates a many-to-many fan-out across 5,292 shared keys, inflating row count by 2.65% and total revenue by £80,705. All revenue calculations use `SUM(fact_invoice_items.line_total)` exclusively.

**Authoritative revenue:** `£9,307,314.40` — verified to agree to £0.00 between `fact_invoice_items` and `dim_invoices`.

---

## 6. Methodology

```
Raw Data (data/raw/)
    ↓  [02_data_cleaning.ipynb]
Clean Data (data/processed/)
    ↓  [04_exploratory_data_analysis.ipynb]
EDA → Visualisations → Observations
    ↓
Insights → Hypotheses → Recommendations
    ↓  [05_customer_features_and_churn.ipynb]
RFM Feature Engineering + Churn Target
    ↓  [06_modelling.ipynb]
Logistic Regression + Evaluation
    ↓
Churn Probability Scores + Risk Segmentation
    ↓
Decision Support (FINAL_Customer_Churn_Analytics.ipynb)
```

---

## 7. EDA

Five final visualisations (located in `notebooks/figures/`):

| # | Visualisation | Key finding |
|---|--------------|-------------|
| VIZ 1 | Monthly Revenue Trend (Jan 2014–Dec 2015) | 45× revenue step-change at December 2014 |
| VIZ 2 | Revenue by Product Category (Top 12) | Kitchen & Dining + Home Decor + Toys & Games = 53.0% of revenue |
| VIZ 3 | Customer Behaviour: Frequency & Revenue by Segment | Wholesalers generate 73.6% of revenue from 13.1% of customers |
| VIZ 4 | Top 15 Products by Revenue | Top product alone accounts for £168,470 |
| VIZ 5 | Customer Lifetime Revenue Distribution (log scale) | Top 10% of customers generate 70.3% of revenue |

**Major findings:**
- Revenue jumped 45× at December 2014 — observation windows must remain within a single regime
- 22.4% of all customers (8,237 total) placed only one invoice in 24 months
- Wholesalers generate 18.5× more revenue per customer than private customers

---

## 8. Churn Methodology

| Parameter | Value |
|-----------|-------|
| `OBS_START` | 2015-01-01 |
| `OBS_END` | 2015-06-30 |
| `PRED_START` | 2015-07-01 |
| `HORIZON_END` | 2015-12-27 (OBS_END + 180 days) |

**Churn definition:**
- `Churn_Status = 1`: customer made **zero** invoices in `(2015-06-30, 2015-12-27]`
- `Churn_Status = 0`: customer made **≥1** invoice in `(2015-06-30, 2015-12-27]`

The label uses `HORIZON_END = 2015-12-27`, not `PRED_END = 2015-12-30`. The 3-day difference accounts for exactly 12 customers who purchased only in the 2015-12-28–30 tail. All 10 automated leakage checks pass.

**Result:** 5,052 eligible customers — 1,892 churned (37.5%), 3,160 retained (62.5%).

---

## 9. Machine Learning

### Primary model: Logistic Regression

| Setting | Value |
|---------|-------|
| Penalty | L2 (Ridge) |
| C | 1.0 |
| class_weight | balanced |
| Solver | lbfgs |

### Features

| Feature | Transformation | Description |
|---------|---------------|-------------|
| `Recency` | None | Days since last purchase to OBS_END |
| `Frequency` | log1p | Order count in observation window |
| `Monetary` | log1p | Total spend in observation window (£) |
| `Avg_Order_Value` | log1p | Monetary / Frequency |
| `tenure_days` | None | Span of obs-window activity in days |
| `is_wholesaler` | Binary | 1 = wholesaler, 0 = private |

Split: 70% train / 15% validation / 15% test, stratified by `Churn_Status`, seed 42.

**Comparison models** (not primary): Random Forest (300 trees), XGBoost (400 trees, learning_rate=0.05).

---

## 10. Model Evaluation

Test-set results (758 held-out customers):

| Model | AUC | Accuracy | Precision | Recall | F1 |
|-------|-----|----------|-----------|--------|----|
| **Logistic Regression ★** | **0.6704** | 57.1% | 0.458 | 0.785 | 0.579 |
| Random Forest | 0.6825 | 58.7% | 0.471 | 0.838 | 0.603 |
| XGBoost | 0.6715 | 62.0% | 0.495 | 0.708 | 0.583 |

★ = Primary internship model

**Majority-class baseline accuracy: 62.5%**

Logistic Regression test accuracy (57.1%) is below the majority-class baseline. This is expected: `class_weight='balanced'` trades accuracy for churn detection. The model catches **78.5% of actual churners** (recall) at the cost of more false alarms. AUC and recall are the appropriate headline metrics.

---

## 11. Risk Segmentation

All 5,052 customers are scored with predicted churn probability and assigned to a risk tier:

| Tier | Threshold | Customers | Actual churn rate | Obs-window revenue share |
|------|-----------|-----------|-------------------|--------------------------|
| High | prob ≥ 0.70 | 943 | **78.8%** | 9.4% |
| Medium | 0.40–0.70 | 2,316 | 44.2% | 11.1% |
| Low | < 0.40 | 1,793 | 7.0% | **79.5%** |

**Revenue at risk (actual churners):**

| Tier | Revenue at risk |
|------|----------------|
| High | £297,313 |
| Medium | £194,136 |
| Low | £97,108 |
| **Total** | **£588,557** |

---

## 12. Limitations

**Model accuracy vs baseline:** LR test accuracy (57.1%) is below the majority-class baseline (62.5%). Accuracy must always be interpreted alongside the majority-class baseline and recall.

**Wholesaler evaluation unreliable:** The test set contained only 3 actual wholesaler churners out of 142 wholesaler test customers. The model predicted "retained" for all wholesalers: precision = 0.00, recall = 0.00. The churn model is not appropriate for wholesaler scoring. Wholesaler account management should use relationship monitoring, not this model's output.

**Associations, not causation:** The model identifies statistical associations between purchase-behaviour features and observed churn outcomes during 2015. It does not establish that any feature causes churn. All findings should be interpreted as observed associations.

**Scope:** Single 6-month observation window (Jan–Jun 2015); RFM-only features; no product diversity, return rates, or demographics.

---

## 13. Repository Structure

```
customer-churn-analytics/
├── data/
│   ├── raw/                          ← READ-ONLY, never modified
│   │   ├── customers.csv
│   │   ├── purchases.csv
│   │   ├── invoice_items.csv
│   │   └── products.csv
│   └── processed/
│       ├── dim_invoices.csv
│       ├── fact_invoice_items.csv
│       ├── dim_customers.csv
│       ├── dim_products.csv
│       ├── customer_churn_dataset.csv
│       ├── customer_churn_scored.csv
│       ├── model_evaluation_summary.json
│       ├── model_features.json
│       └── split_metadata.json
│
├── models/
│   ├── logistic_regression_pipeline.pkl  ← PRIMARY model
│   ├── random_forest_pipeline.pkl
│   └── xgboost_pipeline.pkl
│
├── notebooks/
│   ├── FINAL_Customer_Churn_Analytics.ipynb  ← FINAL integrated notebook
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_data_model_validation.ipynb
│   ├── 04_exploratory_data_analysis.ipynb
│   ├── 05_customer_features_and_churn.ipynb
│   ├── 06_modelling.ipynb
│   └── figures/                       ← all visualisation outputs
│
├── reports/
│   ├── EDA_REPORT.md
│   ├── modelling_report.md
│   ├── model_limitations.md
│   ├── presentation_metrics.md
│   ├── MC3_FINAL_AUDIT.md
│   ├── final_project_audit.md
│   └── ...
│
├── src/
│   ├── data_loader.py
│   ├── cleaning.py
│   ├── validation.py
│   └── data_model.py
│
├── DATA_MODEL.md
├── JOIN_GRAIN_INVESTIGATION.md
├── README.md
└── requirements.txt
```

---

## 14. Installation

```bash
# Clone or download the repository, then:
pip install -r requirements.txt
```

Tested on Python 3.12. All package versions are pinned with minimum compatible versions in `requirements.txt`.

---

## 15. Running the Project

**To reproduce the full project from scratch:**

```bash
# 1. Run in order (each notebook depends on the previous)
jupyter notebook notebooks/01_data_understanding.ipynb
jupyter notebook notebooks/02_data_cleaning.ipynb
jupyter notebook notebooks/03_data_model_validation.ipynb
jupyter notebook notebooks/04_exploratory_data_analysis.ipynb
jupyter notebook notebooks/05_customer_features_and_churn.ipynb
jupyter notebook notebooks/06_modelling.ipynb
```

**To view the final integrated results only:**

```bash
jupyter notebook notebooks/FINAL_Customer_Churn_Analytics.ipynb
```

The final notebook loads all saved outputs (processed CSVs and trained model `.pkl` files) and does not retrain any model.

---

## 16. Project Outputs

| Output | Location | Description |
|--------|----------|-------------|
| Final notebook | `notebooks/FINAL_Customer_Churn_Analytics.ipynb` | 33-section integrated narrative |
| Churn dataset | `data/processed/customer_churn_dataset.csv` | 5,052 customers with RFM features and churn label |
| Scored dataset | `data/processed/customer_churn_scored.csv` | 5,052 customers with churn probability and risk tier |
| Primary model | `models/logistic_regression_pipeline.pkl` | Fitted sklearn Pipeline (StandardScaler + LR) |
| EDA report | `reports/EDA_REPORT.md` | 5 visualisations, 5 insights, 3 hypotheses, 3 recommendations |
| Modelling report | `reports/modelling_report.md` | Full model evaluation and business recommendations |
| Model limitations | `reports/model_limitations.md` | Wholesaler caveat, causation disclaimer |
| Final audit | `reports/final_project_audit.md` | PASS/FAIL checklist for all project requirements |
| Figures | `notebooks/figures/` | 15+ PNG visualisations |
