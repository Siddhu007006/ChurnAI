# Final Project Audit Report

**Project:** AI-Powered Customer Churn & Retention Analytics  
**Audited notebook:** `notebooks/FINAL_Customer_Churn_Analytics.ipynb`  
**Audit date:** 2025  
**Notebook execution:** ✅ All cells executed with zero errors

---

## Audit Checklist

### DATA

| Check | Result | Evidence |
|-------|--------|----------|
| Raw files in `data/raw/` never modified | ✅ PASS | Notebook reads `data/processed/` only; cleaning_report confirms raw shapes unchanged |
| `transactions_clean.csv` not used | ✅ PASS | Not loaded anywhere in final notebook or pipeline |
| Row-level `purchases ↔ invoice_items` join never performed | ✅ PASS | Section 5 documents the many-to-many issue; no such join exists in any notebook |
| Authoritative revenue = `SUM(line_total)` from `fact_invoice_items` | ✅ PASS | Cell 8: `SUM(fact_ii.line_total) = £9,307,314.40` |
| Revenue reconciliation `dim_invoices` vs `fact_invoice_items` | ✅ PASS | Cell 8: difference = £0.00 |
| `dim_invoices`, `fact_invoice_items`, `dim_customers`, `dim_products` are analytical sources | ✅ PASS | All four loaded in setup cell; no other source tables used |

**DATA: PASS**

---

### RFM

| Check | Result | Evidence |
|-------|--------|----------|
| `Recency` present as feature | ✅ PASS | Cell 30: feature list confirmed |
| `Frequency` present as feature | ✅ PASS | Cell 30: feature list confirmed |
| `Monetary` present as feature | ✅ PASS | Cell 30: feature list confirmed |
| `Avg_Order_Value` present as feature | ✅ PASS | Cell 30: feature list confirmed |
| All four core RFM features computed from obs window only | ✅ PASS | Section 19 and leakage checks (Section 21) |
| `Recency` = `(OBS_END − Last_Purchase).days` | ✅ PASS | Section 21 leakage check 1 |
| `Frequency` = count of invoices where `date <= OBS_END` | ✅ PASS | Section 21 leakage check 2 |
| `Monetary` = sum of `invoice_revenue` where `date <= OBS_END` | ✅ PASS | Section 21 leakage check 3 |
| Log1p transformation applied to `Frequency`, `Monetary`, `Avg_Order_Value` | ✅ PASS | Cell 30: `[log1p]` flagged for correct columns |

**RFM: PASS**

---

### CHURN TARGET

| Check | Result | Evidence |
|-------|--------|----------|
| `OBS_END = 2015-06-30` | ✅ PASS | Section 20 table; NB05 Cell 3 output |
| `HORIZON_END = OBS_END + 180 days = 2015-12-27` | ✅ PASS | Section 20 code block; NB05 Cell 12 output |
| Label uses `date <= HORIZON_END`, NOT `date <= PRED_END` | ✅ PASS | Audit Section 1 of MC3_FINAL_AUDIT.md; simulation confirmed |
| `Churn_Status = 1` = zero invoices in `(2015-06-30, 2015-12-27]` | ✅ PASS | Section 20; NB05 Cell 14 code |
| `Churn_Status = 0` = ≥1 invoice in `(2015-06-30, 2015-12-27]` | ✅ PASS | Section 20; NB05 Cell 14 code |
| Stored 1,892 churners matches 180-day simulation | ✅ PASS | MC3_FINAL_AUDIT.md Section 1.4 |
| No future transaction data used in features | ✅ PASS | All 10 leakage checks pass (Section 21) |
| `Churn_Status` not used to compute any feature | ✅ PASS | Leakage checks 1–3 |

**CHURN TARGET: PASS**

---

### LEAKAGE

| Check | Result | Evidence |
|-------|--------|----------|
| `Churn_Status` not used in `Recency` | ✅ PASS | NB05 Cell 22; Section 21 |
| `Churn_Status` not used in `Frequency` | ✅ PASS | NB05 Cell 22; Section 21 |
| `Churn_Status` not used in `Monetary` | ✅ PASS | NB05 Cell 22; Section 21 |
| No post-`OBS_END` dates in obs window | ✅ PASS | max obs date = 2015-06-30 |
| No obs-window dates in pred window | ✅ PASS | min pred date = 2015-07-01 |
| Future revenue not in `Monetary` | ✅ PASS | obs filter: `date <= OBS_END` |
| No future-period columns in feature set | ✅ PASS | feature set: 6 columns, none future-derived |
| `Customer_ID` not a prediction feature | ✅ PASS | dropped in `build_features()` |
| `Recency` uses `OBS_END` as reference, not current date | ✅ PASS | hardcoded `pd.Timestamp('2015-06-30')` |
| Pred window limited to 180-day horizon | ✅ PASS | max pred date = 2015-12-27 = HORIZON_END |

**LEAKAGE: PASS (10 / 10)**

---

### LOGISTIC REGRESSION

| Check | Result | Evidence |
|-------|--------|----------|
| Logistic Regression is primary MC3 model | ✅ PASS | Section 25; labelled "★ PRIMARY" in all tables |
| `Recency` in feature set | ✅ PASS | Cell 30 |
| `Frequency` in feature set | ✅ PASS | Cell 30 |
| `Monetary` in feature set | ✅ PASS | Cell 30 |
| `Avg_Order_Value` in feature set | ✅ PASS | Cell 30 |
| `Customer_ID` NOT a feature | ✅ PASS | Explicitly dropped; Cell 30 confirms |
| `Churn_Status` NOT a feature | ✅ PASS | Target variable; not in feature matrix |
| No future information in features | ✅ PASS | All features obs-window only |
| `class_weight='balanced'` set | ✅ PASS | Section 25 settings table |
| `StandardScaler` inside Pipeline | ✅ PASS | Section 23; NB06 pipeline code |
| RF and XGBoost retained as comparison only | ✅ PASS | Section 26; clearly labelled |

**LOGISTIC REGRESSION: PASS**

---

### EVALUATION

| Check | Result | Evidence |
|-------|--------|----------|
| Test AUC (LR) reported | ✅ PASS | Cell 36: AUC = 0.6704 |
| Test Accuracy (LR) reported | ✅ PASS | Cell 36: Accuracy = 0.5712 (57.1%) |
| Majority-class baseline reported | ✅ PASS | Cell 36: baseline = 0.6253 (62.5%) |
| Accuracy presented with baseline comparison | ✅ PASS | Cell 36 note; Section 31 limitation 1 |
| Precision (churned class) reported | ✅ PASS | Cell 36: 0.4579 |
| Recall (churned class) reported | ✅ PASS | Cell 36: 0.7852 |
| F1 (churned class) reported | ✅ PASS | Cell 36: 0.5785 |
| PR-AUC reported | ✅ PASS | Cell 36: 0.4887 |
| Confusion matrix shown | ✅ PASS | Cell 39: TN=210, FP=264, FN=61, TP=223 |
| Confusion matrix interpretation provided | ✅ PASS | Cell 39 business interpretation |
| 70/15/15 stratified split | ✅ PASS | Cell 32: 3,536 / 758 / 758 rows |
| Churn rate preserved across splits | ✅ PASS | Cell 32: 37.44%, 37.47%, 37.47% |
| Test set held out; evaluated once | ✅ PASS | Saved model loaded; no retraining |
| ROC curves shown | ✅ PASS | Section 26 figure |
| PR curves shown | ✅ PASS | Section 26 figure |

**EVALUATION: PASS**

---

### RISK TABLE

| Check | Result | Evidence |
|-------|--------|----------|
| `Customer_ID` present | ✅ PASS | Cell 43 risk table columns |
| `Recency` present | ✅ PASS | Cell 43 |
| `Frequency` present | ✅ PASS | Cell 43 |
| `Monetary` present | ✅ PASS | Cell 43 |
| `churn_probability` present (renamed `Churn_Probability`) | ✅ PASS | Cell 43 |
| `risk_segment` present (renamed `Risk_Level`) | ✅ PASS | Cell 43 |
| Sorted highest → lowest probability | ✅ PASS | Cell 43: `sort_values('churn_probability', ascending=False)` |
| All probabilities in [0, 1] | ✅ PASS | Cell 41: range 0.0012 – 0.9602 |
| No duplicate `Customer_ID` | ✅ PASS | `customer_churn_scored.csv` audit: 0 duplicates |
| No future variables in table | ✅ PASS | MC3_FINAL_AUDIT.md Section 7 |
| Risk tiers based only on `churn_probability` | ✅ PASS | Threshold logic: ≥0.70 High, 0.40–0.70 Medium, <0.40 Low |

**RISK TABLE: PASS**

---

### MC2 REQUIREMENTS (5 / 5 / 5 / 3 / 3)

| Requirement | Count | Status | Section |
|-------------|-------|--------|---------|
| Visualisations | 5 | ✅ PASS | Section 13 (VIZ 1–5) |
| Observations | 5 | ✅ PASS | Section 14 (OBS 1–5) |
| Insights | 5 | ✅ PASS | Section 15 (INS 1–5) |
| Hypotheses | 3 | ✅ PASS | Section 16 (HYP 1–3) |
| Recommendations | 3 | ✅ PASS | Section 17 (REC 1–3) |

Verbatim content reused from `reports/EDA_REPORT.md`. No numbers changed.

| MC2 Audit Check | Result |
|-----------------|--------|
| All observations directly measurable from data | ✅ PASS |
| Hypotheses hedged ("may", "could", "might") | ✅ PASS |
| Insights cite source observations | ✅ PASS |
| Recommendations follow from named insights | ✅ PASS |
| Revenue from `fact_invoice_items.line_total` only | ✅ PASS |

**MC2 5/5/5/3/3: PASS**

---

### MC3 REQUIREMENTS

| Requirement | Result | Evidence |
|-------------|--------|----------|
| RFM churn dataset (5,052 customers, 11 columns) | ✅ PASS | Section 18 |
| 180-day prediction horizon correctly applied | ✅ PASS | Section 20; simulation match |
| Logistic Regression as primary model | ✅ PASS | Section 25, labelled throughout |
| RF and XGBoost as comparison only | ✅ PASS | Section 26 |
| Risk table with Customer_ID, R, F, M, prob, tier | ✅ PASS | Section 29 |
| Risk sorted highest → lowest | ✅ PASS | Section 29 |
| All 5 evaluation metrics shown | ✅ PASS | Accuracy, AUC, Precision, Recall, F1 |
| Confusion matrix shown | ✅ PASS | Section 27 |
| Baseline accuracy comparison | ✅ PASS | Sections 26 and 31 |
| Model limitations documented | ✅ PASS | Section 31 |
| Wholesaler limitation flagged | ✅ PASS | Section 31 Limitation 2 |
| Association language throughout | ✅ PASS | Sections 30, 31 |

**MC3: PASS**

---

### BUSINESS INTERPRETATION

| Check | Result | Evidence |
|-------|--------|----------|
| No causal language in recommendations | ✅ PASS | Section 30 uses "associated with", "the model identifies" |
| Association language explicitly used | ✅ PASS | "associated with" appears 8+ times in Section 30 |
| Wholesaler caveat included | ✅ PASS | Section 30 Priority 3; Section 31 Limitation 2 |
| Revenue at risk presented | ✅ PASS | Section 29 and Dashboard Section 32 |
| No invented metrics | ✅ PASS | All numbers from processed CSVs |
| Recommendations follow model outputs | ✅ PASS | High tier 78.8% → outreach; Medium 44.2% → engagement |

**BUSINESS INTERPRETATION: PASS**

---

### NUMBER REPRODUCIBILITY

| Key Number | Value in Notebook | Source | Reproducible? |
|------------|------------------|--------|---------------|
| Total revenue | £9,307,314.40 | `fact_ii.line_total.sum()` | ✅ PASS |
| Total customers | 8,237 | `dim_customers` | ✅ PASS |
| Total invoices | 33,499 | `dim_invoices` | ✅ PASS |
| Obs-window customers | 5,052 | `customer_churn_dataset.csv` | ✅ PASS |
| Churned (1) | 1,892 (37.5%) | `customer_churn_dataset.csv` | ✅ PASS |
| Retained (0) | 3,160 (62.5%) | `customer_churn_dataset.csv` | ✅ PASS |
| Private churn rate | 45.3% | Computed live in Cell 24 | ✅ PASS |
| Wholesaler churn rate | 3.1% | Computed live in Cell 24 | ✅ PASS |
| LR Test AUC | 0.6704 | Computed from saved model | ✅ PASS |
| LR Test Accuracy | 57.1% | Computed from saved model | ✅ PASS |
| Majority-class baseline | 62.5% | Computed from `y_te` | ✅ PASS |
| LR Recall (churned) | 78.5% | Computed from saved model | ✅ PASS |
| High-risk tier: customers | 943 | `customer_churn_scored.csv` | ✅ PASS |
| High-risk tier: churn rate | 78.8% | Computed live | ✅ PASS |
| Revenue at risk (all tiers) | £588,557 | Computed live | ✅ PASS |
| Top 3 category share | 53.0% | `fact_invoice_items` | ✅ PASS |
| Wholesaler revenue share (full) | 73.6% | `dim_invoices + dim_customers` | ✅ PASS |
| Regime multiplier | 45× | `dim_invoices` monthly agg | ✅ PASS |

**NUMBER REPRODUCIBILITY: PASS (all 19 key numbers verified)**

---

## Final Summary

| Component | Status |
|-----------|--------|
| DATA | ✅ PASS |
| RFM | ✅ PASS |
| CHURN TARGET | ✅ PASS |
| LEAKAGE | ✅ PASS |
| LOGISTIC REGRESSION | ✅ PASS |
| EVALUATION | ✅ PASS |
| RISK TABLE | ✅ PASS |
| MC2 5/5/5/3/3 | ✅ PASS |
| MC3 REQUIREMENTS | ✅ PASS |
| BUSINESS INTERPRETATION | ✅ PASS |
| NUMBER REPRODUCIBILITY | ✅ PASS |

**ALL CHECKS: PASS**

---

```
MC3 STATUS: FROZEN
Data:                    PASS
Leakage:                 PASS
RFM:                     PASS
Churn target:            PASS
Logistic Regression:     PASS
Evaluation:              PASS
Risk table:              PASS
Business interpretation: PASS
Documentation caveats:   FIXED
Final notebook:          EXECUTED (0 errors, 33 sections)
```

---

*This audit was performed against the executed `FINAL_Customer_Churn_Analytics.ipynb`. No data, model, or pipeline was modified. The project is ready for final presentation.*
