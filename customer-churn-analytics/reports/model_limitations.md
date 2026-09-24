# Model Limitations

**Project:** AI-Powered Customer Churn & Retention Analytics  
**Applies to:** `models/logistic_regression_pipeline.pkl` (primary), `random_forest_pipeline.pkl`, `xgboost_pipeline.pkl`  
**Status:** FROZEN — documentation only, no model changes

---

## 1. Wholesaler Segment: Model Is Unreliable

### What the evaluation showed

When the Logistic Regression was evaluated separately on the **wholesaler** portion of the test set (142 customers), the results were:

| Metric | Wholesaler segment | Private segment |
|--------|-------------------|----------------|
| Observed churn rate | **2.1%** | 45.6% |
| Test AUC | **0.45** | 0.54 |
| Precision (churned) | **0.00** | 0.46 |
| Recall (churned) | **0.00** | 0.79 |
| F1 (churned) | **0.00** | 0.58 |

The model predicted "retained" for every single wholesaler in the test set. Precision, recall, and F1 for the churned class are all zero.

### Why this happened

The test set contained only **3 actual wholesaler churners** out of 142 wholesaler test customers (2.1% churn rate). With so few positive examples, the model cannot learn a meaningful decision boundary for this segment. Predicting "retained" for all wholesalers yields 97.9% accuracy within the segment — which the model effectively does.

This is not a coding error. It is a fundamental limitation: the dataset does not contain enough wholesaler churn events for the model to learn a reliable churn signal for this segment.

### What this means in practice

- **Do not use the churn probability scores to rank or target wholesalers for churn-prevention campaigns.**
- The `risk_segment` labels assigned to wholesalers in `customer_churn_scored.csv` are **not meaningful** for this group and should be treated with caution.
- Wholesaler account management should rely on relationship monitoring, contract review cycles, and account-specific health indicators — not on this model's output.

---

## 2. Private-Customer Performance Is Substantially More Informative

The model was designed for and is most meaningful when applied to **private customers** (n=4,113, observed churn rate 45.3%).

On the private-customer subset of the test set:
- AUC = 0.54 (above random, though modest)
- Recall = 0.79 (catches most churners)
- Precision = 0.46 (roughly 1 in 2 flagged customers is a genuine churner)

While AUC = 0.54 within the private segment alone is modest, the full-dataset AUC of 0.67 reflects the model's ability to separate the two very different segments (private vs wholesale). RFM-based churn prediction within a single homogeneous segment is harder, and the results are consistent with the literature on RFM-only models.

---

## 3. Model Results Should Not Be Interpreted as Causal Relationships

The model identifies *statistical associations* between purchase-behaviour features (Recency, Frequency, Monetary, Avg_Order_Value, tenure_days, is_wholesaler) and the observed binary churn outcome during the 2015 prediction window.

**The model does not establish cause and effect.** Specifically:

- A high `Recency` value (many days since last purchase) is *associated with* a higher predicted churn probability. This does not mean that the passage of time *causes* a customer to churn. Both the long gap and the churn outcome may be driven by a third factor not present in the data (e.g. a negative service experience, a competitor offer, a change in the customer's circumstances).

- `is_wholesaler = 0` (private customer) is *associated with* higher observed churn rates. This does not mean that being a private customer *causes* churn. Wholesale and private customers may differ in ways not captured by this dataset — contract terms, order size incentives, category mix, or relationship management practices.

- High `Avg_Order_Value` carries a small positive coefficient in Logistic Regression, suggesting a weak *association* with higher churn probability. This does not mean high-value single orders *drive* churn. It may reflect single-occasion buyers who made one large purchase and never returned.

**In all presentations and recommendations, use language such as:**
- "customers associated with X show higher observed churn rates"
- "the model identifies a relationship between X and churn probability"
- "the results suggest that customers with X may be worth prioritising for retention outreach"
- "this association does not establish that X causes churn"

---

## 4. Other Known Limitations

| Limitation | Detail |
|-----------|--------|
| **Single observation window** | Features and label are derived from Jan–Jun 2015 (obs) and Jul–Dec 2015 (prediction). The model may not generalise to different seasons or years. |
| **RFM-only feature set** | No product diversity, return rates, customer service contacts, or marketing exposure data. These are likely meaningful predictors not captured here. |
| **No demographics** | Apart from `customer_type`, no age, geography, or acquisition-channel information is available. |
| **Overfitting in ensemble models** | Random Forest (train AUC 0.83 vs val 0.68) and XGBoost (train AUC 0.92 vs val 0.68) show substantial train-validation gaps. Their test-set results are more trustworthy than their training-set results. |
| **Probability calibration** | XGBoost and Random Forest probabilities are not calibrated. The raw probability values should be used for ranking customers, not as literal estimates of churn likelihood. |
| **54% single-order customers** | 2,734 of 5,052 customers placed exactly one order in the obs window. For these customers, the RFM signal is minimal (Frequency=1, Recency=days since that order). The model may be conflating first-time trialists with formerly regular customers who stopped purchasing. |

---

*This file is documentation only. No model, dataset, or pipeline was modified to produce it.*
