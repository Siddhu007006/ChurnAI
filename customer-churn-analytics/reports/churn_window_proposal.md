# Churn Window Proposal — Masterclass 3
## AI-Powered Customer Churn & Retention Analytics

> **Status:** Proposal — awaiting review before churn labels or features are created.  
> **Sources used:** `dim_invoices.csv`, `dim_customers.csv` (read-only).  
> **No churn labels, RFM features, or ML models created here.**

---

## 1. Dataset Date Range

| Metric | Value |
|--------|------:|
| Minimum invoice date | **2014-01-01** |
| Maximum invoice date | **2015-12-30** |
| Total months covered | **24** |
| Total days | 728 |
| Total invoices | 33,499 |
| Total customers | 8,237 |

---

## 2. Monthly Activity Summary

| Month | Invoices | Active Customers | Revenue |
|-------|--------:|-----------------:|--------:|
| 2014-01 | 665 | 612 | £15,516 |
| 2014-02 | 623 | 589 | £14,269 |
| 2014-03 | 608 | 573 | £14,727 |
| 2014-04 | 678 | 632 | £15,783 |
| 2014-05 | 711 | 660 | £17,033 |
| 2014-06 | 674 | 613 | £16,358 |
| 2014-07 | 680 | 628 | £16,276 |
| 2014-08 | 690 | 637 | £16,262 |
| 2014-09 | 651 | 602 | £14,738 |
| 2014-10 | 697 | 639 | £15,850 |
| 2014-11 | 647 | 608 | £14,955 |
| **2014-12** | **2,057** | **1,487** | **£585,560** ← regime step |
| 2015-01 | 1,609 | 1,321 | £588,893 |
| 2015-02 | 1,544 | 1,277 | £464,364 |
| 2015-03 | 1,894 | 1,505 | £613,607 |
| 2015-04 | 1,715 | 1,382 | £487,244 |
| 2015-05 | 2,172 | 1,635 | £697,751 |
| 2015-06 | 1,972 | 1,514 | £679,564 |
| 2015-07 | 1,909 | 1,488 | £619,109 |
| 2015-08 | 1,921 | 1,528 | £665,518 |
| 2015-09 | 2,305 | 1,780 | £968,501 |
| 2015-10 | 2,498 | 1,903 | £1,055,025 |
| 2015-11 | 3,262 | 2,227 | £1,176,131 |
| 2015-12 | 1,317 | 1,120 | £534,280 |

### Regime Comparison

| Metric | Jan–Nov 2014 (11 months) | Dec 2014–Dec 2015 (13 months) | Multiplier |
|--------|-------------------------:|------------------------------:|----------:|
| Avg monthly invoices | 666 | 2,013 | **3.0×** |
| Avg monthly customers | 618 | 1,551 | **2.5×** |
| Avg monthly revenue | £15,615 | £702,734 | **45×** |

The step-change is immediate and sustained. All three indicators shift simultaneously at December 2014 and do not revert.

---

## 3. Churn Definition

> **Churned = no purchase for 180 days or more after the last purchase in the observation window.**

A customer is considered **retained** if they placed at least one invoice in the prediction window.  
A customer is considered **churned** if they placed no invoice in the prediction window AND at least 180 days have elapsed since their last observation-window purchase before the prediction window ends.

This definition is:
- Applied strictly at the individual customer level using their own last purchase date
- Symmetric: no customer can be labelled "churned" if the prediction window is too short to observe 180 days of inactivity from their last known purchase

---

## 4. Candidate Windows Evaluated

Four windows were evaluated. All use only dates actually present in the dataset.

| Window Label | OBS_START | OBS_END | PRED_START | PRED_END | OBS months | PRED days | Obs Customers | Labellable | Churn % | Viable? |
|-------------|-----------|---------|-----------|---------|----------:|----------:|-------------:|----------:|--------:|--------|
| A — June split | 2015-01-01 | 2015-06-30 | 2015-07-01 | 2015-12-30 | 6 | **183** | 5,052 | 5,052 | 37.2% | ✅ |
| B — May split | 2015-01-01 | 2015-05-31 | 2015-06-01 | 2015-12-30 | 5 | 213 | 4,528 | 4,528 | 32.8% | ✅ |
| C — Regime start | 2014-12-01 | 2015-06-30 | 2015-07-01 | 2015-12-30 | 7 | 183 | 5,557 | 5,557 | 38.1% | ✅ |
| D — July split | 2015-01-01 | 2015-07-31 | 2015-08-01 | 2015-12-30 | 7 | **152** | 5,494 | 4,095 | 47.0% | ❌ |

**Window D is eliminated.** A 152-day prediction window is shorter than the 180-day churn threshold. Customers whose last purchase was in July 2015 cannot accumulate 180 days of inactivity before December 30, 2015. Only 4,095 of 5,494 customers can be labelled, and the high 47% churn rate is artefactual — customers are being labelled churned simply because the window is too short to observe their return.

---

## 5. Proposed Window — Recommendation A (June Split)

```
 2015-01-01                2015-06-30  2015-07-01             2015-12-30
      │                         │           │                       │
      │◄──── OBS window ───────►│           │◄──── PRED window ────►│
      │    6 months of history  │           │   183 days / ~6 months│
      │    Features computed    │           │   Label determined     │
      │    from this period     │           │   from this period     │
```

| Period | Start | End | Duration | Purpose |
|--------|-------|-----|---------|---------|
| **Observation** | **2015-01-01** | **2015-06-30** | 6 months (181 days) | Compute RFM and behavioural features per customer |
| **Prediction** | **2015-07-01** | **2015-12-30** | 183 days | Observe whether each customer purchases again |
| Data excluded | 2014-01-01 | 2014-11-30 | 11 months | Pre-regime data — structurally different behaviour |

### Why 2015-01-01 as OBS_START (not 2014-12-01)

December 2014 is the first month of the structural regime change. Using it as the observation start date risks including customers who were transitioning from the old to the new regime mid-purchase cycle, and the extreme revenue spike in that month (£585K vs the £15K monthly run-rate prior) would distort Monetary features. Starting the observation window from 2015-01-01 ensures the features are computed within a single, internally consistent regime.

> **Note on Window C:** Window C (starting 2014-12-01) adds 1,057 additional December 2014 customers that Window A does not see (5,557 vs 5,052). This makes the cohort larger and the churn rate marginally higher (38.1% vs 37.2%). It is a viable alternative but includes the December 2014 transition spike. Window A is preferred for cleaner regime consistency.

### Why 2015-06-30 as OBS_END

- It leaves exactly **183 days** of prediction window (July 1 – December 30, 2015), which exceeds the 180-day churn threshold by a 3-day buffer.
- It positions the prediction window inside the same post-regime period where customers are operating at the same purchasing frequency and revenue level as the observation window.
- All 5,052 customers active in the observation window can be reliably labelled — the leakage check confirms **zero customers have their 180-day window extend beyond December 30, 2015**.

---

## 6. Labelling Logic

For each customer active in the observation window (2015-01-01 to 2015-06-30):

```
LAST_OBS_DATE = last invoice date in observation window

IF any invoice exists in (2015-07-01, 2015-12-30]:
    Churn_Status = 0  (Retained)
ELSE IF LAST_OBS_DATE + 180 days <= 2015-12-30:
    Churn_Status = 1  (Churned)
ELSE:
    EXCLUDE from labelled set  (prediction window too short — NOT applicable given our window)
```

Under Window A, the leakage check confirms that **all 5,052 customers** satisfy the condition `LAST_OBS_DATE + 180 days <= 2015-12-30`. The earliest last-observation date in the cohort is 2015-01-01; 2015-01-01 + 180 days = 2015-07-01, which is still before December 30. Therefore, no customers need to be excluded for insufficient prediction time.

**Expected label distribution (from analysis):**

| Label | Count | Share |
|-------|------:|------:|
| Churned (Churn_Status = 1) | 1,880 | 37.2% |
| Retained (Churn_Status = 0) | 3,172 | 62.8% |
| **Total labellable** | **5,052** | 100% |

The 37.2% churn rate is plausible for a retail business. It is not trivially unbalanced (neither 5/95 nor 50/50), meaning a classifier trained on this dataset will have reasonable signal from both classes.

---

## 7. Customers Excluded from the Churn Cohort

The labelled cohort covers **5,052 of 8,237 total customers** (61.3%). The remaining 38.7% (3,185 customers) are excluded for the following reasons:

| Exclusion reason | Approx. count | Explanation |
|-----------------|-------------:|-------------|
| Never active in the 2015-01-01 – 2015-06-30 observation window | ~3,185 | Either first purchased after 2015-06-30 (late entrants) or only active in 2014 before the regime change |

This is expected. Not every customer who exists in the dataset is observable within the chosen observation window. Customers who first purchased after 2015-06-30 cannot be included because they have no observation-window history from which to compute features.

**The 3,185 excluded customers are not "lost" for the business.** They may be used as a live scoring cohort once the model is trained, applying the trained model to their behaviour to generate churn probability scores.

---

## 8. Leakage Risks

| Risk | Description | Mitigation in this design |
|------|-------------|--------------------------|
| **Temporal leakage** | Using any information from the prediction window (2015-07-01 onwards) when computing features | Features must be computed using ONLY `date <= 2015-06-30` |
| **Target leakage** | Including the churn label (derived from prediction window) as a feature | Churn_Status must not be present in the feature table |
| **Recency leakage** | Using the last purchase date as a feature without time-gating | Recency must be computed as `OBS_END - last_obs_date` (days since last purchase before cut-off), not the raw date |
| **Regime leakage** | Including pre-December 2014 purchase history in features when the label is based on 2015 behaviour | By starting OBS at 2015-01-01, all observation history is in the same behavioural regime as the label period |
| **Label lookahead** | Checking whether a customer "almost" purchased in the pred window and treating them differently | Labels are binary (purchased / did not purchase in pred window). No partial or continuous label. |
| **Recent-buyer bias** | A customer who purchased on 2015-06-29 has only 1 day of "inactivity" at the start of the pred window, yet is expected to meet the 180-day threshold | Under Window A, 180 days from 2015-06-29 = 2015-12-27, which is still before 2015-12-30. So this customer CAN be correctly labelled. |

---

## 9. Justification for the Proposed Windows

**Why the observation window is 6 months (not longer or shorter):**

- **Lower bound:** Fewer than 3 months of observation history would make Frequency features unreliable — many customers who purchase monthly would appear as single-purchase customers in a 2-month window.
- **Upper bound:** Extending the observation window back before January 2015 would incorporate the December 2014 regime transition and pre-transition data with structurally different purchasing patterns, contaminating RFM features.
- **6 months** provides enough history to observe multiple invoices for the majority of the cohort and produces a clean, regime-consistent feature window.

**Why the prediction window is ~6 months (183 days):**

- The churn definition is 180 days of inactivity. A prediction window must be *at least* 180 days to allow any customer to be correctly labelled as churned.
- 183 days (July 1 – December 30) provides a 3-day buffer beyond the 180-day threshold, ensuring that even customers whose last observation-window purchase was on the final day of the observation window (June 30) can be correctly labelled.
- The prediction window ends on December 30, 2015, which is the last date with invoice data. No future data beyond this point exists.

**Why the dataset end (2015-12-30) is used as PRED_END:**

- It is the maximum date available. Any earlier PRED_END would reduce the number of labellable customers or force the prediction window below 180 days.
- Using the maximum available date maximises the prediction window length and ensures no customer is excluded due to an artificially shortened observation of their inactivity.

---

## 10. Limitations

| Limitation | Detail |
|------------|--------|
| **No full-year 2015 observation history** | The 6-month observation window is the maximum available within the post-regime period that still leaves a valid 180-day prediction window. A longer observation window (e.g. 12 months) would require starting in January 2015 and ending in December 2015, leaving zero prediction window. |
| **No information on customers before January 2014** | The dataset start date is 2014-01-01. Customers who existed before this date may have prior purchase history that is not captured. |
| **54.1% of obs-window customers have only 1 invoice** | In a 6-month observation window, many customers will have limited history. RFM features for single-invoice customers will be less discriminating. |
| **No channel, promotion, or acquisition data** | Features are limited to purchase behaviour. No marketing channel, pricing, or acquisition source information is available to enrich the feature set. |
| **Single cohort, single cut-off** | This design uses one temporal cross-section. A walk-forward validation with multiple cut-offs would produce more robust model evaluation, but requires more data than the 24-month window provides. |

---

## 11. Period Summary Table

| Period | Start | End | Duration | Purpose |
|--------|-------|-----|---------|---------|
| Pre-regime (excluded) | 2014-01-01 | 2014-11-30 | 11 months | Structurally different behaviour — not used |
| Regime transition (excluded from OBS) | 2014-12-01 | 2014-12-31 | 1 month | Step-change month — excluded from OBS to avoid regime mixing |
| **Observation window** | **2015-01-01** | **2015-06-30** | **6 months (181 days)** | **Compute RFM and behavioural features per customer** |
| **Prediction window** | **2015-07-01** | **2015-12-30** | **183 days (~6 months)** | **Determine churn label: purchased or not?** |

---

> **Next step (pending review):** If this proposal is approved, proceed to Masterclass 3 feature engineering:
> - Compute RFM + behavioural features for the 5,052 observation-window customers using only `date <= 2015-06-30`
> - Assign Churn_Status using the prediction window
> - Create the labelled customer-level dataset
> - Apply train/validation/test split

*No churn labels, RFM, or model outputs have been created. This document is a proposal only.*
