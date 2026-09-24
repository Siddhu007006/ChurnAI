# MC3 Presentation Metrics Reference

**Project:** AI-Powered Customer Churn & Retention Analytics  
**Purpose:** Reference card for internship presentation — metric explanation and caveats  
**Status:** FROZEN (do not modify without re-running audit)

---

## Primary Internship Model

**Logistic Regression**  
- Role: primary MC3 model
- Scope: all 5,052 customers in the observation window
- Features: Recency, Frequency, Monetary, Avg_Order_Value (core RFM) + tenure_days, is_wholesaler
- Class balancing: `class_weight='balanced'`

---

## Key Test-Set Metrics

| Metric | Value | Notes |
|--------|-------|-------|
| **Test AUC (ROC)** | **0.67** | Primary evaluation metric |
| Test Accuracy | 57.1% | ⚠️ See explanation below |
| Majority-class baseline accuracy | 62.5% | Always-predict-retained benchmark |
| Churn recall | ~79% | % of real churners the model catches |
| Churn precision | ~46% | % of flagged customers who actually churned |
| Churn F1 | 0.58 | Harmonic mean of precision and recall |

---

## Why Test Accuracy (57.1%) Is Below the Majority-Class Baseline (62.5%) — And Why That Is Not a Problem

### The baseline explained

In this dataset, **62.55% of customers did not churn**. A completely naive strategy — predict "this customer will stay" for every single person, regardless of their purchase history — would be correct 62.5% of the time. This is called the majority-class baseline.

The Logistic Regression achieves **57.1% accuracy**, which is slightly *below* this baseline. At first glance this looks like the model is worse than doing nothing.

### Why this is misleading

Accuracy counts every correct prediction equally — catching a churner counts the same as correctly labelling a loyal customer. But these two outcomes are not equally valuable to a business:

- **Missing a real churner** means losing a customer with no chance to intervene.
- **Wrongly flagging a loyal customer as at-risk** means spending a small amount on an unnecessary retention offer — far less costly.

The Logistic Regression is configured with `class_weight='balanced'`, which deliberately shifts the model away from simply predicting the majority class. The result is that it catches **79% of actual churners** (recall = 0.79) at the cost of more false alarms — which pulls overall accuracy below the baseline.

### The right way to read these numbers

| Strategy | Accuracy | Churners caught |
|----------|----------|----------------|
| Always predict "retained" (baseline) | **62.5%** | **0%** |
| Logistic Regression | 57.1% | **~79%** |

The model trades a 5.4 percentage-point drop in accuracy for a 79 percentage-point improvement in churn detection. For the business goal of identifying customers at risk, this trade-off is clearly favourable.

### Why AUC is the right headline metric

ROC-AUC measures how well the model *ranks* customers by their churn probability, independent of any threshold. An AUC of 0.67 means: pick any churner and any non-churner at random; the model assigns a higher churn probability to the churner **67% of the time**. Random guessing would give 0.50. A perfect model would give 1.00.

**For presentations, lead with AUC = 0.67 and recall = 79%, not accuracy.**

---

## Model Applicability

| Segment | Customers | Observed churn rate | Model reliable? |
|---------|-----------|---------------------|----------------|
| Private customers | 4,113 | 45.3% | ✅ Yes — primary use case |
| Wholesalers | 939 | 3.1% | ❌ No — see `model_limitations.md` |

The churn model should be presented as applicable to **private customers**. Wholesaler results are unreliable due to near-zero churn rates in the available data (see full explanation in `reports/model_limitations.md`).

---

## MC3 STATUS: FROZEN

| Component | Status |
|-----------|--------|
| Data | PASS |
| Leakage | PASS |
| RFM | PASS |
| Churn target | PASS |
| Logistic Regression | PASS |
| Evaluation | PASS |
| Risk table | PASS |
| Business interpretation | PASS |
| Documentation caveats | FIXED |

---

*This file is documentation only. No data, model, or pipeline was modified to produce it.*
