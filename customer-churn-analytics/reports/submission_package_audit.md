# Submission Package Audit

**Project:** AI-Powered Customer Churn & Retention Analytics  
**Audit date:** 2025  
**Files audited:**  
- `requirements.txt`  
- `README.md`  
- `Student_Customer_Churn_Analytics_ProjectReport.docx`

---

## README.md Audit

| Check | Status | Evidence |
|-------|--------|----------|
| Project name | ✅ PASS | H1: "AI-Powered Customer Churn & Retention Analytics" |
| Problem statement | ✅ PASS | Section 2: wholesaler revenue concentration, lack of early-warning system |
| Objectives | ✅ PASS | Section 3: 10 numbered objectives |
| Dataset documented | ✅ PASS | Section 4: all 4 files with row counts and key columns |
| Dataset source stated | ✅ PASS | "Provided as part of the internship programme (Dataset A)" — no invented URL |
| Data architecture explained | ✅ PASS | Section 5: star schema, many-to-many join risk, authoritative revenue rule |
| Methodology workflow | ✅ PASS | Section 6: full pipeline diagram Raw→Clean→EDA→Insights→Prediction→Decision |
| EDA summarised | ✅ PASS | Section 7: all 5 VIZ with key finding; major findings listed |
| Churn methodology | ✅ PASS | Section 8: OBS_START, OBS_END, PRED_START, HORIZON_END, exact definition |
| Machine learning | ✅ PASS | Section 9: LR as primary; RF and XGB as comparison only; features table |
| Model evaluation with actual metrics | ✅ PASS | Section 10: AUC 0.6704, Acc 57.1%, baseline 62.5%, Prec 0.458, Rec 0.785, F1 0.579 |
| Risk segmentation | ✅ PASS | Section 11: High/Medium/Low table with thresholds, customer counts, churn rates |
| Limitations | ✅ PASS | Section 12: accuracy/baseline, wholesaler caveat, association disclaimer |
| Repository structure | ✅ PASS | Section 13: full tree with annotations |
| Installation | ✅ PASS | Section 14: pip install -r requirements.txt, Python 3.12 |
| Running the project | ✅ PASS | Section 15: sequential notebook execution + final notebook shortcut |
| Project outputs | ✅ PASS | Section 16: 8 outputs listed with locations and descriptions |

**README: PASS (17 / 17)**

---

## Project Report Audit

| Check | Status | Evidence |
|-------|--------|----------|
| Title page (title, subtitle, dataset, status) | ✅ PASS | Lines 1–5 of document |
| Abstract | ✅ PASS | Section present; includes AUC, recall, churn rate, association disclaimer |
| Introduction | ✅ PASS | Section 1: business context, revenue concentration, project motivation |
| Problem statement | ✅ PASS | Section 2: reactive vs proactive retention, gap defined |
| Objectives | ✅ PASS | Section 3: 8 numbered objectives |
| Dataset description | ✅ PASS | Section 4: table with 4 files, row counts, columns; GBP9,307,314.40 revenue |
| Data architecture | ✅ PASS | Section 5: star schema table, many-to-many join risk, revenue reconciliation |
| Data cleaning | ✅ PASS | Section 6: 5 cleaning steps listed |
| EDA | ✅ PASS | Section 7: 5-row VIZ table with key findings |
| Observations (5) | ✅ PASS | Section 8: exactly 5 observations, each measurable, no interpretation |
| Business insights (5) | ✅ PASS | Section 9: exactly 5 insights, each citing source observation |
| Hypotheses (3) | ✅ PASS | Section 10: exactly 3 hypotheses, hedged language ("may", "could", "might") |
| Recommendations (3) | ✅ PASS | Section 11: exactly 3 recommendations, follow from named insights |
| Customer-level feature engineering | ✅ PASS | Section 12: feature table with types and descriptions |
| RFM analysis | ✅ PASS | Section 13: statistics table, churn rates by frequency and recency band |
| Churn definition | ✅ PASS | Section 14: parameter table, label construction explained, 1,892/3,160 |
| Leakage prevention | ✅ PASS | Section 15: 4 bullet-point checks, assertion methodology |
| Machine learning methodology | ✅ PASS | Section 16: pipeline, split sizes, preprocessing steps |
| Logistic Regression | ✅ PASS | Section 17: feature table with coefficients and direction descriptions |
| Model evaluation with actual metrics | ✅ PASS | Section 18: table with AUC, accuracy, baseline, precision, recall, F1; confusion matrix |
| Majority-class baseline alongside accuracy | ✅ PASS | Table column "Baseline" = 62.5% for all models; explanatory paragraph |
| Wholesaler evaluation unreliability disclosed | ✅ PASS | Section 21 Limitation 2: "only 3 actual wholesaler churners", precision/recall/F1 = 0.00 |
| Customer risk segmentation | ✅ PASS | Section 19: 3-tier table, revenue-at-risk figures |
| Business actions | ✅ PASS | Section 20: 4 priorities, all using association language |
| Limitations | ✅ PASS | Section 21: 3 primary + additional limitations |
| Dashboard / decision summary | ✅ PASS | Section 22: summary table, reference to 6-panel figure |
| Conclusion | ✅ PASS | Section 23: overall summary, AUC 0.6704, recall 78.5%, association disclaimer |
| References / dataset source | ✅ PASS | Section 24: dataset provenance, library versions, project report references |
| No unsupported claims | ✅ PASS | No invented statistics, no causal language, no external benchmarks |
| Observations distinguished from insights | ✅ PASS | Sections 8 and 9 explicitly labelled and separated |
| Hypotheses distinguished as propositions | ✅ PASS | "may", "could", "might" hedging throughout Section 10 |
| Recommendations follow from insights | ✅ PASS | Each recommendation cites its source insight |
| No causal language | ✅ PASS | "associated with", "observed", "may be worth testing" throughout |
| Document validation | ✅ PASS | `office_read mode:validate` → "Validation passed: no errors found" |
| Section count | ✅ PASS | 24 sections (Title + Abstract + 1–24) = 25 headings |
| Table count | ✅ PASS | 10 tables covering datasets, data model, features, RFM stats, model comparison, etc. |

**REPORT: PASS (36 / 36)**

---

## requirements.txt Audit

| Check | Status | Evidence |
|-------|--------|----------|
| pandas included | ✅ PASS | `pandas>=2.0.0` |
| numpy included | ✅ PASS | `numpy>=1.24.0` |
| matplotlib included | ✅ PASS | `matplotlib>=3.7.0` |
| seaborn included | ✅ PASS | `seaborn>=0.12.0` |
| scikit-learn included | ✅ PASS | `scikit-learn>=1.2.0` |
| xgboost included | ✅ PASS | `xgboost>=1.7.0` |
| joblib included | ✅ PASS | `joblib>=1.2.0` |
| notebook/jupyter included | ✅ PASS | `notebook>=7.0.0`, `nbformat>=5.9.0`, `nbconvert>=7.9.0`, `ipykernel>=6.0.0` |
| No unnecessary packages | ✅ PASS | Only imports verified from FINAL_Customer_Churn_Analytics.ipynb and src/ |
| No invented packages | ✅ PASS | All packages confirmed installed in project environment |
| lightgbm not included | ✅ PASS | Not used in any notebook or source file |
| tensorflow/torch not included | ✅ PASS | Not used |
| Compatible package names | ✅ PASS | `scikit-learn` (correct PyPI name, not `sklearn`) |

**REQUIREMENTS: PASS (13 / 13)**

---

## Submission Package File Inventory

| File | Size | Status |
|------|------|--------|
| `requirements.txt` | 330 bytes | ✅ Present |
| `README.md` | ~10 KB | ✅ Present |
| `Student_Customer_Churn_Analytics_ProjectReport.docx` | ~50 KB | ✅ Present |
| `notebooks/FINAL_Customer_Churn_Analytics.ipynb` | ~120 KB | ✅ Present (executed) |
| `data/processed/customer_churn_dataset.csv` | ~250 KB | ✅ Present (frozen) |
| `data/processed/customer_churn_scored.csv` | ~258 KB | ✅ Present (frozen) |
| `models/logistic_regression_pipeline.pkl` | ~2 KB | ✅ Present (frozen) |
| `models/random_forest_pipeline.pkl` | ~4 MB | ✅ Present (frozen) |
| `models/xgboost_pipeline.pkl` | ~857 KB | ✅ Present (frozen) |
| `reports/EDA_REPORT.md` | ~22 KB | ✅ Present (frozen) |
| `reports/modelling_report.md` | ~12 KB | ✅ Present (frozen) |
| `reports/model_limitations.md` | ~6 KB | ✅ Present (frozen) |
| `reports/presentation_metrics.md` | ~4 KB | ✅ Present (frozen) |
| `reports/MC3_FINAL_AUDIT.md` | ~21 KB | ✅ Present (frozen) |
| `reports/final_project_audit.md` | ~12 KB | ✅ Present (frozen) |

---

## Final Verdict

```
README:        PASS (17/17)
REPORT:        PASS (36/36)
REQUIREMENTS:  PASS (13/13)

TOTAL:         PASS (66/66)

Analytical project: FROZEN
data/raw/:     UNTOUCHED
Models:        UNTOUCHED
Notebooks:     UNTOUCHED
MC1/MC2/MC3:   UNTOUCHED
```

---

*This audit was performed against the files as they exist at submission. No analytical outputs were modified during packaging.*
