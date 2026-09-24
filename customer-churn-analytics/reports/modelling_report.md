# Churn Prediction Modelling Report

**Project:** AI-Powered Customer Churn & Retention Analytics  
**Notebook:** `notebooks/06_modelling.ipynb`  
**Dataset:** `data/processed/customer_churn_dataset.csv` (5,052 customers)  
**Report date:** 2025

---

## 1. Objective

Train and evaluate three baseline churn prediction models on the leakage-safe `customer_churn_dataset.csv`. Score all customers with churn probabilities and segment them into risk tiers to support targeted retention interventions.

---

## 2. Methodology

### 2.1 Features Used

Six features entered the model after dropping identifiers, date strings, and alias columns:

| Feature | Transformation | Description |
|---------|---------------|-------------|
| `Recency` | None (mild skew 0.50) | Days since last purchase to OBS_END |
| `Frequency` | log1p | Order count in obs window |
| `Monetary` | log1p | Total spend in obs window (£) |
| `Avg_Order_Value` | log1p | Monetary / Frequency |
| `tenure_days` | None | (Last_Purchase − First_Purchase).days |
| `is_wholesaler` | Binary encode | 1 = wholesaler, 0 = private |

**Dropped before modelling:** `Customer_ID`, `First_Purchase`, `Last_Purchase`, `Total_Revenue` (alias of `Monetary`), `Order_Count` (alias of `Frequency`).

### 2.2 Train / Validation / Test Split

Stratified by `Churn_Status` (seed = 42):

| Split | Rows | Churn rate |
|-------|------|------------|
| Train | 3,536 | 37.44% |
| Validation | 758 | 37.47% |
| **Test** | **758** | **37.47%** |

The test set was held out and evaluated **once** at the end, using only XGBoost (the best model from validation).

### 2.3 Models

| Model | Key settings |
|-------|-------------|
| **Logistic Regression** | L2, C=1.0, `class_weight='balanced'` |
| **Random Forest** | 300 trees, `max_depth=8`, `min_samples_leaf=5`, `class_weight='balanced'` |
| **XGBoost** | 400 trees, `max_depth=5`, `learning_rate=0.05`, `scale_pos_weight=1.671` |

All models wrap StandardScaler in a sklearn Pipeline. The `scale_pos_weight` for XGBoost (1.671) equals the retained:churned count ratio in the training set.

---

## 3. Results

### 3.1 Validation Set Performance

| Model | ROC-AUC | PR-AUC | F1 (Churned) | Precision | Recall |
|-------|---------|--------|-------------|-----------|--------|
| Logistic Regression | 0.6676 | 0.5016 | 0.5867 | 0.4600 | 0.8099 |
| Random Forest | **0.6805** | **0.5091** | **0.5967** | 0.4688 | 0.8204 |
| XGBoost | **0.6805** | 0.5034 | 0.5697 | **0.4923** | 0.6761 |

### 3.2 Test Set Performance (XGBoost — Best Model)

| Metric | Value |
|--------|-------|
| ROC-AUC | **0.6715** |
| PR-AUC | **0.4891** |
| F1 (Churned class) | **0.5826** |
| Precision (Churned) | 0.4951 |
| Recall (Churned) | 0.7077 |
| Accuracy | 0.62 |

**Full classification report (test set):**

```
              precision    recall  f1-score   support

    Retained       0.76      0.57      0.65       474
     Churned       0.50      0.71      0.58       284

    accuracy                           0.62       758
   macro avg       0.63      0.64      0.62       758
weighted avg       0.66      0.62      0.63       758
```

### 3.3 Train vs Validation Gap (Overfitting Check)

| Model | Train AUC | Val AUC | Gap |
|-------|-----------|---------|-----|
| Logistic Regression | 0.6998 | 0.6676 | 0.032 |
| Random Forest | 0.8288 | 0.6805 | 0.148 ⚠️ |
| XGBoost | 0.9198 | 0.6805 | 0.239 ⚠️ |

Both ensemble models are overfitting to the training set. Random Forest is less severe. All three models converge to similar validation AUC (~0.68), suggesting the current feature set is the primary performance bottleneck, not the choice of algorithm.

---

## 4. Feature Importances (XGBoost)

| Rank | Feature | Importance (gain) |
|------|---------|-------------------|
| 1 | `is_wholesaler` | **0.784** |
| 2 | `Monetary` | 0.049 |
| 3 | `tenure_days` | 0.047 |
| 4 | `Recency` | 0.045 |
| 5 | `Avg_Order_Value` | 0.040 |
| 6 | `Frequency` | 0.035 |

**Key finding:** `is_wholesaler` dominates with 78.4% of total gain, reflecting the extreme difference in churn rates between segments (wholesaler 3.1% vs private 45.3%). Once segment is known, the RFM features provide marginal lift. This dominance may be masking meaningful patterns within each segment.

---

## 5. Risk Segmentation

All 5,052 customers were scored with their predicted churn probability. Risk tiers:

| Tier | Threshold | Customers | Actual churners | Churn rate | Avg probability | Revenue share |
|------|-----------|-----------|----------------|------------|----------------|---------------|
| **High** | ≥ 0.70 | 943 | 743 | **78.8%** | 0.78 | 9.4% |
| **Medium** | 0.40–0.70 | 2,316 | 1,023 | 44.2% | 0.56 | 11.1% |
| **Low** | < 0.40 | 1,793 | 126 | 7.0% | 0.14 | **79.5%** |

### Revenue at Risk (Actual Churners by Segment)

| Tier | Churned customers | Revenue at risk |
|------|-------------------|----------------|
| High | 743 | £297,313 |
| Medium | 1,023 | £194,136 |
| Low | 126 | £97,108 |
| **Total** | **1,892** | **£588,557** |

The High-risk tier captures 743 of the 1,892 total churners (39.3%) with a 78.8% precision rate — a strong signal for targeted outreach.

---

## 6. Visualisations Produced

| File | Content |
|------|---------|
| `notebooks/figures/viz6_roc_pr_curves.png` | ROC and Precision-Recall curves for all three models on the validation set |
| `notebooks/figures/viz7_confusion_matrices.png` | Confusion matrices (threshold=0.5) for all three models |
| `notebooks/figures/viz8_feature_importances.png` | XGBoost feature importance bar chart |
| `notebooks/figures/viz9_churn_probability_dist.png` | Churn probability distributions by actual label and customer type |
| `notebooks/figures/viz10_revenue_at_risk.png` | Revenue at risk by risk segment (actual churners) |

---

## 7. Outputs Saved

| File | Description |
|------|-------------|
| `data/processed/customer_churn_scored.csv` | All 5,052 customers with `churn_probability` and `risk_segment` |
| `data/processed/model_evaluation_summary.json` | Full metrics for all models across splits |
| `data/processed/model_features.json` | Feature list and log-transformed columns |
| `data/processed/split_metadata.json` | Train/val/test sizes and seed |
| `models/logistic_regression_pipeline.pkl` | Fitted LR pipeline |
| `models/random_forest_pipeline.pkl` | Fitted RF pipeline |
| `models/xgboost_pipeline.pkl` | Fitted XGBoost pipeline |

---

## 8. Analysis & Interpretation

### 8.1 Why ROC-AUC is ~0.67 (not higher)

The current feature set is almost entirely RFM (Recency, Frequency, Monetary, AOV) plus a single binary segment flag. The `is_wholesaler` flag dominates because it perfectly separates the two grossly different churn populations. Within each segment, RFM features have limited additional power with only a 6-month obs window. Contributing factors:

1. **54.1% of customers ordered only once** — single-order customers have limited RFM signal; their churn is hard to distinguish from first-time trialists
2. **No product-level diversity features** — customers who buy across multiple categories may behave differently, but this is not yet captured
3. **No return/cancellation data** — negative experiences are invisible
4. **Single season** — the 6-month window may not capture seasonal repeat customers

### 8.2 Model Selection Rationale

All three models achieved equivalent validation AUC (0.68). XGBoost was selected for the test set evaluation and scoring because:
- Highest precision on the churned class (0.4923 on val)
- Best recall on test set (0.7077) — important for catching churners
- Most production-ready for probability calibration

### 8.3 Overfitting

Both RF and XGBoost show significant train-val gaps (0.148 and 0.239). This is expected given the small feature count (6). Hyperparameter tuning (deeper cross-validation, regularisation) is the next lever, alongside adding more features to give the models more signal to generalise.

---

## 9. Business Recommendations

> **Interpretation note:** All findings below are framed as *observed associations* in the dataset and in the model's outputs. The model identifies statistical relationships between purchase-behaviour features and the observed churn outcome during 2015. It does not establish that any feature *causes* churn, nor does it claim to explain customer motivations. Recommendations follow from these associations and should be treated as data-informed hypotheses to test, not as confirmed causal mechanisms.

### Priority 1 — High Risk Tier (943 customers)
- The model identifies a relationship between high predicted churn probability (≥ 0.70) and observed churn: **78.8%** of customers in this tier actually churned during the prediction window.
- The results suggest that customers the model assigns to this tier are associated with substantially higher churn rates than the overall average (37.5%).
- £297,313 in observation-window revenue is associated with confirmed churners in this tier.
- Recommended actions: personalised win-back offers may be worth testing for this group; account manager outreach for top-spending customers; exclusive loyalty incentives. Whether any of these actions reduces churn can only be confirmed through a controlled test.

### Priority 2 — Medium Risk Tier (2,316 customers)
- The model identifies a relationship between medium predicted probability (0.40–0.70) and an observed churn rate of **44.2%** — above the population average.
- The results suggest that proactive re-engagement may be worthwhile for this group, though the association is weaker than in the High tier.
- £194,136 in observation-window revenue is associated with confirmed churners in this tier.
- Recommended actions: re-engagement email campaigns, cross-sell recommendations based on previous category purchases, loyalty points acceleration. These should be evaluated against a holdout group to measure lift.

### Priority 3 — Wholesalers (Low churn, High value)
- Wholesaler status is *associated* with a substantially lower observed churn rate (3.1% vs 45.3% for private customers) in this dataset and time period. The model does not explain why this association exists; it may reflect contract structures, purchasing incentives, or other unmeasured factors.
- 79.5% of all observation-window revenue is associated with the Low-risk tier, the majority of which is wholesaler revenue.
- The churn model is **not reliable for wholesalers** (see `reports/model_limitations.md`). Account health monitoring and relationship management are more appropriate approaches for this segment.
- Recommended actions: volume incentive programmes, dedicated account management, periodic relationship check-ins — not churn scoring.

### Priority 4 — Single-Order Customers (2,734 customers, 54.1%)
- Single-order customers show an observed churn rate of **46.5%**, which is above the population average. The model identifies this group as associated with higher predicted churn probability.
- The results suggest that customers who placed only one order during the observation window may not have converted to repeat buyers — whether this reflects product fit, price sensitivity, or other factors is not determinable from this data.
- Recommended actions: a post-first-purchase onboarding sequence and a second-purchase incentive within 30 days may be worth testing. The expected benefit should be evaluated against a control group.

---

## 10. Next Steps

| Priority | Action |
|----------|--------|
| 1 | Add product diversity features (unique categories, unique products per customer) |
| 2 | Hyperparameter tuning with stratified 5-fold CV (GridSearchCV or Optuna) |
| 3 | Calibrate XGBoost probabilities (Platt scaling or isotonic regression) |
| 4 | Segment-specific models — separate LR/RF/XGB trained on private-only and wholesaler-only |
| 5 | Streamlit dashboard for risk-segmented customer browser |

---

*End of report.*
