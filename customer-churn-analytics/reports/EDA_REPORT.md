# EDA Report — Masterclass 2
## AI-Powered Customer Churn & Retention Analytics

**Notebook:** `notebooks/04_exploratory_data_analysis.ipynb`  
**Phase:** 2 — Exploratory Data Analysis → Business Insights  
**Status:** ✅ Complete — 5 visualisations | 5 observations | 5 insights | 3 hypotheses | 3 recommendations  

---

## Dataset Overview

| Metric | Value |
|--------|------:|
| Observation period | 2014-01-01 to 2015-12-30 (24 months) |
| Unique customers | 8,237 |
| Unique invoices | 33,499 |
| Total line items | 431,263 |
| Unique products | 4,033 |
| Product categories | 25 |
| **Total revenue** | **£9,307,314.40** |

**Customer type breakdown:**
| Type | Count | Share |
|------|------:|------:|
| Private | 7,161 | 86.9% |
| Wholesaler | 1,076 | 13.1% |

**Analytical sources used:** `dim_invoices`, `fact_invoice_items`, `dim_customers`, `dim_products`  
Revenue calculated exclusively from `dim_invoices.invoice_revenue` and `fact_invoice_items.line_total`.  
`transactions_clean.csv` and row-level `purchases ↔ invoice_items` joins were not used.

---

## Methodology

All analysis was performed on the four normalised analytical tables produced in Phase 1. Key methodological choices:

- **Revenue** is always `SUM(line_total)` from `fact_invoice_items` or `SUM(invoice_revenue)` from `dim_invoices`. The two are verified to agree to £0.00.
- **Zero-price rows** (40 rows, 0.009%) are excluded from all revenue aggregations via `line_total > 0`.
- **Regime analysis** is conducted by separating the data at December 2014, where a structural step-change in all three key metrics (revenue, invoice count, active customers) is observable. No causal attribution is made.
- **Customer-level metrics** are aggregated from `dim_invoices` grouped by `CustomerID`, then joined to `dim_customers` for type enrichment.
- No feature engineering, RFM metrics, or churn labels are created in this phase.

---

## Monthly Revenue Summary

| Month | Revenue | Invoices | Active Customers |
|-------|--------:|--------:|-----------------:|
| 2014-01 | £15,516 | 665 | 612 |
| 2014-02 | £14,269 | 623 | 589 |
| 2014-03 | £14,727 | 608 | 573 |
| 2014-04 | £15,783 | 678 | 632 |
| 2014-05 | £17,033 | 711 | 660 |
| 2014-06 | £16,358 | 674 | 613 |
| 2014-07 | £16,276 | 680 | 628 |
| 2014-08 | £16,262 | 690 | 637 |
| 2014-09 | £14,738 | 651 | 602 |
| 2014-10 | £15,851 | 697 | 639 |
| 2014-11 | £14,955 | 647 | 608 |
| **2014-12** | **£585,560** | **2,057** | **1,487** |
| 2015-01 | £588,893 | 1,609 | 1,321 |
| 2015-02 | £464,364 | 1,544 | 1,277 |
| 2015-03 | £613,607 | 1,894 | 1,505 |
| 2015-04 | £487,244 | 1,715 | 1,382 |
| 2015-05 | £697,751 | 2,172 | 1,635 |
| 2015-06 | £679,564 | 1,972 | 1,514 |
| 2015-07 | £619,109 | 1,909 | 1,488 |
| 2015-08 | £665,518 | 1,921 | 1,528 |
| 2015-09 | £968,501 | 2,305 | 1,780 |
| 2015-10 | £1,055,025 | 2,498 | 1,903 |
| 2015-11 | £1,176,131 | 3,262 | 2,227 |
| 2015-12 | £534,280 | 1,317 | 1,120 |

**Regime averages:**
- Jan 2014 – Nov 2014: **£15,615/month** (11 months)
- Dec 2014 – Dec 2015: **£702,734/month** (13 months)
- Multiplier: **45×**

---

## Top Revenue Categories

| Rank | Category | Revenue | Share |
|------|----------|--------:|------:|
| 1 | Kitchen & Dining | £2,253,891 | 24.2% |
| 2 | Home Decor | £1,801,098 | 19.4% |
| 3 | Toys & Games | £878,241 | 9.4% |
| 4 | Health, Beauty & Personal Care | £838,500 | 9.0% |
| 5 | Apparel & Accessories | £806,046 | 8.7% |
| 6 | Stationery & Craft | £788,585 | 8.5% |
| 7 | Party & Festive | £563,068 | 6.0% |
| 8 | Seasonal | £422,605 | 4.5% |
| 9 | Garden & Outdoor | £377,138 | 4.1% |
| 10+ | All others (16 categories) | £578,143 | 6.2% |

---

## Top Products by Revenue

| Rank | Product | Category | Revenue | Quantity |
|------|---------|----------|--------:|--------:|
| 1 | paper craft, little birdie | Stationery & Craft | £168,470 | 80,995 |
| 2 | regency cakestand 3 tier | Kitchen & Dining | £142,265 | 12,374 |
| 3 | white hanging heart t-light holder | Home Decor | £100,392 | 36,706 |
| 4 | jumbo bag red retrospot | Kitchen & Dining | £85,041 | 46,078 |
| 5 | medium ceramic top storage jar | Kitchen & Dining | £81,417 | 77,916 |
| 6 | postage | Administrative | £77,804 | 3,120 |
| 7 | party bunting | Party & Festive | £68,785 | 15,279 |
| 8 | assorted colour bird ornament | Home Decor | £56,413 | 35,263 |
| 9 | manual | Administrative | £53,420 | 6,933 |
| 10 | rabbit night light | Home Decor | £51,251 | 27,153 |

---

## Customer-Level Statistics

| Metric | Value |
|--------|------:|
| Median invoices per customer | 3 |
| Mean invoices per customer | 4.1 |
| Max invoices per customer | 210 |
| Customers with 1 invoice | 1,843 (22.4%) |
| Customers with 2 invoices | 1,524 (18.5%) |
| Customers with 5+ invoices | 2,397 (29.1%) |
| Customers with 10+ invoices | 417 (5.1%) |

| Customer Type | Count | Total Revenue | Avg Revenue/Customer | Avg Invoice Value |
|--------------|------:|--------------:|---------------------:|------------------:|
| Private | 7,161 | £2,458,519 | £343 | £149 |
| Wholesaler | 1,076 | £6,848,796 | **£6,365** | **£791** |

---

## Five Final Visualisations

### VIZ 1 — Monthly Revenue Trend (Jan 2014 – Dec 2015)
**Chart type:** Bar chart with regime boundary annotation  
**Location:** `notebooks/figures/viz1_monthly_revenue.png`

Shows monthly revenue across the full 24-month period. A vertical dashed line marks the structural regime change at December 2014. Pre-December bars are shown in blue; December 2014 onwards in orange. The chart makes the step-change immediately visible and prevents a single average from concealing it.

---

### VIZ 2 — Revenue by Product Category (Top 12)
**Chart type:** Horizontal bar chart with percentage labels  
**Location:** `notebooks/figures/viz2_revenue_by_category.png`

Shows the 12 highest-revenue categories ranked by total `line_total` from `fact_invoice_items`. Kitchen & Dining (24.2%) and Home Decor (19.4%) stand clearly above the rest. Percentage labels on each bar show revenue concentration.

---

### VIZ 3 — Customer Behaviour: Invoice Frequency & Revenue by Type
**Chart type:** Two-panel — histogram (left) + bar chart (right)  
**Location:** `notebooks/figures/viz3_customer_behaviour.png`

Left panel: distribution of invoices per customer (capped at 30), with the spike at 1 annotated. Right panel: total revenue by customer type showing wholesaler disproportionality despite lower headcount.

---

### VIZ 4 — Top 15 Products by Revenue
**Chart type:** Horizontal bar chart  
**Location:** `notebooks/figures/viz4_top_products_revenue.png`

Shows individual product names ranked by total revenue. Reveals concentration: the top product ("paper craft, little birdie") alone accounts for £168,470 (1.8% of total revenue). Multiple top-15 products are from Kitchen & Dining and Home Decor.

---

### VIZ 5 — Distribution of Customer Lifetime Revenue (Log Scale)
**Chart type:** Histogram, log x-axis, percentile lines  
**Location:** `notebooks/figures/viz5_customer_revenue_dist.png`

Plots all 8,237 customers' lifetime revenue on a log scale. Median (p50), p90, and p95 lines are annotated. An inset box highlights that the top 10% of customers generate ~70% of total revenue.

---

## Five Observations

### OBSERVATION 1 — Structural Revenue Regime Change at December 2014
Monthly revenue was stable between January 2014 and November 2014, averaging £15,615/month. Beginning December 2014, monthly revenue rose to £585,560 and remained at an elevated run-rate through all of 2015, averaging £702,734/month — a **45× increase**. The shift is simultaneous across revenue, invoice count (666 → 2,013 avg/month), and active customers (618 → 1,551 avg/month).

### OBSERVATION 2 — Revenue Is Concentrated in Three Product Categories
Kitchen & Dining (24.2%), Home Decor (19.4%), and Toys & Games (9.4%) together account for **53.0% of total revenue** across 24 months. These three categories represent 12% of the total 25 categories. The remaining 22 categories contribute the other 47%.

### OBSERVATION 3 — One in Five Customers Placed Only a Single Invoice
Of 8,237 unique customers, **1,843 (22.4%) placed exactly one invoice** in the 24-month window. The median customer placed 3 invoices. 417 customers (5.1%) placed 10 or more invoices.

### OBSERVATION 4 — Wholesalers: 13% of Customers, 73.6% of Revenue
Wholesaler customers (1,076 customers, 13.1% of the base) account for **£6,848,796 — 73.6% of total revenue**. Their average revenue per customer is £6,365, versus £343 for private customers — an **18.5× differential**. Their average invoice value is £791 versus £149 for private customers.

### OBSERVATION 5 — Customer Revenue Is Highly Right-Skewed
The top 10% of customers by lifetime revenue generate **70.3% of total revenue**. The bottom 50% of customers generate only **4.3%** of total revenue. The median customer lifetime revenue is £193; the mean is £1,130 — a 5.8× gap indicating extreme right-skew.

---

## Five Business Insights

### INSIGHT 1 — Two Revenue Regimes Require Separate Analytical Treatment
**Supporting metric:** 45× revenue multiplier between pre- and post-December 2014 average monthly revenue.  
**Business significance:** A single aggregate average across 24 months misrepresents both periods. Churn models that use the full period without regime awareness will blend features from structurally different states. The observation and prediction windows for churn modelling must be placed within the same regime to produce valid predictions. Specifically, any observation window that crosses December 2014 will produce features that mix two fundamentally different customer behaviour environments.

### INSIGHT 2 — Three Categories Drive Half the Business
**Supporting metric:** Kitchen & Dining + Home Decor + Toys & Games = 53.0% of total revenue from 12% of categories.  
**Business significance:** Inventory, retention, and promotional decisions concentrated on these three categories are likely to have the highest revenue impact. Stock availability, pricing decisions, or category-level promotional campaigns in these areas carry outsized business risk and opportunity. Understanding churn in the context of customer product affinity should start with these categories.

### INSIGHT 3 — The Single-Purchase Segment Represents a Measurable Retention Gap
**Supporting metric:** 22.4% of customers (1,843) placed only one invoice in 24 months.  
**Business significance:** One-in-five customers did not return after their first transaction. This segment represents a concrete, data-supported opportunity for retention improvement. However, the dataset does not provide time-since-first-purchase context for each single-invoice customer, so some fraction may simply not have had time to reorder by the observation period end date. Any retention programme targeting this group must account for this timing ambiguity.

### INSIGHT 4 — Wholesalers Are the Single Highest-Risk Revenue Segment
**Supporting metric:** 1,076 wholesalers (13.1% of customers) generate 73.6% of revenue at 18.5× the per-customer revenue rate of private customers.  
**Business significance:** The loss of even a small number of wholesale accounts would have a disproportionate revenue impact. A single wholesaler lost at the mean revenue rate (£6,365) requires acquiring ~18.5 private customers at mean private revenue (£343) to compensate. Wholesale customer churn must be treated as a materially different and higher-priority risk than private customer churn.

### INSIGHT 5 — Standard Churn Classification Understates Revenue Risk
**Supporting metric:** Top 10% of customers generate 70.3% of revenue; bottom 50% generate 4.3%.  
**Business significance:** A churn model that treats all customers equally will optimise for minimising the count of churned customers, not the revenue at risk from churning customers. Given the extreme revenue concentration, a model that correctly retains the top decile while misclassifying the bottom decile is far more valuable to the business than the reverse. Retention interventions must be ranked by **revenue-at-risk** (churn probability × customer lifetime revenue), not raw churn probability.

---

## Three Hypotheses

### HYPOTHESIS 1 — The December 2014 Step-Change May Reflect a New Wholesale Channel or Customer Segment Entering the Business

**Based on:** Insight 1 (regime change) and Insight 4 (wholesaler disproportionality).

The simultaneous jump in revenue, invoice size, and customer count in December 2014 **could** indicate the onboarding of a new distribution arrangement, wholesale partnership, or institutional customer segment. The fact that wholesaler revenue accounts for 73.6% of all revenue is consistent with this hypothesis — the post-December regime **may** be characterised primarily by large-volume wholesale orders. However, no channel attribution, acquisition source, or contract data is available in the dataset to confirm this.

**What would be needed to test this:** Acquisition date per customer; channel or source field; whether the spike consists primarily of new customers or existing customers increasing order volume.

---

### HYPOTHESIS 2 — Single-Invoice Customers Who Purchased in Jan–Nov 2014 Might Represent the Business's Pre-Scale Churn Rate

**Based on:** Insight 3 (single-purchase segment) and Insight 1 (regime change).

Among the 1,843 single-invoice customers, those who purchased during January–November 2014 (when the business was operating at a much smaller scale) have had more than a year to re-purchase and did not do so. This sub-group **may** represent the genuine one-time buyer or early-stage churn rate of the business, uncontaminated by the timing issue affecting December 2015 purchasers. If confirmed, this would suggest the pre-scale churn rate was already significant.

**What would be needed to test this:** Segment single-invoice customers by first-purchase date and examine whether those who purchased in early 2014 have a materially different profile from those who purchased in late 2015.

---

### HYPOTHESIS 3 — The Top Revenue Decile May Be Almost Exclusively Composed of Wholesale Accounts

**Based on:** Insight 4 (wholesaler revenue) and Insight 5 (revenue concentration).

Wholesalers generate 73.6% of total revenue while comprising 13.1% of customers. The top 10% of customers generate 70.3% of revenue. If the revenue distributions were uncorrelated, we would expect some wholesale customers to fall outside the top decile. However, the magnitude of both numbers suggests the top decile and the wholesaler segment **might** be largely the same population. If so, customer-level revenue concentration is primarily a customer-type concentration problem, and retention of wholesale accounts is the single most important revenue-protection lever.

**What would be needed to test this:** Distribution of `customer_type` within each revenue decile; specifically, what fraction of the top-10% revenue customers are wholesalers.

---

## Three Recommendations

### RECOMMENDATION 1 — Design the Churn Observation Window Within the Post-December 2014 Regime

**Insight:** The business operates in two structurally different revenue regimes separated by December 2014.

**Business implication:** Features computed across both regimes encode regime-level effects rather than individual customer behaviour. A model trained on mixed-regime data may not generalise to the 2015 operating environment that the business will actually be predicting over.

**Recommended action:** In Masterclass 3, select the observation window cut-off between July 2015 and September 2015 (e.g. 2015-07-31), leaving at least 3–5 months of prediction window within 2015. Validate that the selected cut-off leaves sufficient customers active in both observation and prediction windows before committing to it. Exclude pre-December 2014 customers from the training set unless their 2015 behaviour data is sufficient to characterise their purchasing pattern.

**Expected business purpose:** Ensures the churn model reflects the current operating environment of the business, reducing the risk that predicted churn probabilities are biased by the structural shift.

---

### RECOMMENDATION 2 — Build Separate Churn Risk Scores Weighted by Revenue-at-Risk for Wholesale and Private Segments

**Insight:** Wholesalers represent 13.1% of customers but 73.6% of revenue. The top 10% of customers generate 70.3% of revenue.

**Business implication:** A uniform churn intervention applied to all customers will misallocate retention resources. High-value customers whose loss would disproportionately impact revenue require proactive, differentiated treatment.

**Recommended action:** When churn probabilities are produced in Masterclass 5, create a **Revenue-at-Risk** metric: `churn_probability × trailing_12m_revenue`. Sort all customers by this metric and define three intervention tiers: (1) High Revenue-at-Risk (top 10%): proactive outreach; (2) Medium Revenue-at-Risk (10–30%): automated triggered communication; (3) Low Revenue-at-Risk (bottom 70%): monitor only. Analyse these tiers separately for wholesaler vs private composition.

**Expected business purpose:** Maximises revenue protected per pound spent on retention, directing premium-cost interventions only at customers whose loss would be most costly.

---

### RECOMMENDATION 3 — Apply a Minimum Observation Time Filter to Single-Invoice Customers Before Labelling Them as Churned

**Insight:** 22.4% of customers placed only one invoice. The dataset alone cannot distinguish between a customer who purchased in January 2014 and genuinely did not return, and one who purchased in December 2015 and has not yet had the opportunity to return.

**Business implication:** Including recently-acquired single-purchase customers in the "churned" label introduces noise into the churn model, reducing precision and potentially flagging active new customers as churned.

**Recommended action:** In Masterclass 3, apply the following label construction rule: only assign a churn label to customers whose **first purchase** falls at least 90 days before the observation window cut-off. Customers with a first purchase within 90 days of the cut-off should be excluded from the labelled training set and treated as a separate "too new to label" cohort. Sensitivity-test the 90-day threshold against 60-day and 120-day alternatives.

**Expected business purpose:** Reduces label noise in the churn training set, improves model calibration, and prevents retention interventions from being mistakenly triggered on customers who are genuinely in their first purchase cycle.

---

## Analytical Limitations

| Limitation | Description |
|------------|-------------|
| **Cause of regime change unknown** | The dataset provides no channel, acquisition source, or contract data to explain the December 2014 structural shift. All references to this shift are descriptive, not causal. |
| **No customer acquisition date** | First purchase date is used as a proxy for acquisition date. Customers who existed before January 2014 (the observation start) cannot be identified. |
| **No product-level context beyond category** | Product meaning is inferred from category labels. The dataset does not provide brand, supplier, or margin information. |
| **No information on promotional activity** | The dataset contains no promotional, discount, or campaign flags. Seasonal patterns cannot be attributed to specific business actions. |
| **Single-invoice timing ambiguity** | Without a minimum observation time filter, 22.4% of customers labelled as single-purchase cannot be reliably classified as non-returning. |
| **No external benchmarks** | Without industry benchmarks, statements like "22.4% single-purchase rate" cannot be assessed relative to sector norms. |

---

## MC2 Quality Audit Results

| Category | Count | Status |
|----------|------:|--------|
| Final visualisations | 5 | ✅ PASS |
| Observations | 5 | ✅ PASS |
| Insights | 5 | ✅ PASS |
| Hypotheses | 3 | ✅ PASS |
| Recommendations | 3 | ✅ PASS |

| Audit Check | Result |
|-------------|--------|
| Unsupported statements | ✅ None identified |
| Hypotheses presented as facts | ✅ None — hedged language throughout |
| Insights beyond observations | ✅ None — each insight cites its observation |
| Recommendations not following from insights | ✅ None — each cites its source insight |
| Revenue calculation grain | ✅ Always `fact_ii.line_total` or `dim_inv.invoice_revenue` |
| Accidental row multiplication | ✅ No `purchases ↔ invoice_items` row-level join |
| Misleading aggregation | ✅ Pre/post regime averages reported separately |
| Number reproducibility | ✅ All numbers computable from processed tables |

---

## Key Numbers Reference

| Metric | Value | Source |
|--------|------:|--------|
| Total revenue | £9,307,314.40 | `dim_invoices.invoice_revenue` |
| Pre-Dec 2014 avg monthly revenue | £15,615 | `dim_invoices` filtered by date |
| Post-Dec 2014 avg monthly revenue | £702,734 | `dim_invoices` filtered by date |
| Regime multiplier | 45× | Computed |
| Top 3 category revenue share | 53.0% | `fact_invoice_items` grouped by category |
| Single-invoice customers | 1,843 (22.4%) | `dim_invoices` grouped by CustomerID |
| Wholesaler revenue share | 73.6% | `dim_invoices` + `dim_customers` |
| Wholesaler avg revenue / customer | £6,365 | Customer-level aggregation |
| Private avg revenue / customer | £343 | Customer-level aggregation |
| Revenue differential (wholesale/private) | 18.5× | Computed |
| Top 10% customer revenue share | 70.3% | Customer-level aggregation |
| Bottom 50% customer revenue share | 4.3% | Customer-level aggregation |

---

*Phase 2 complete. All deliverables verified. Ready for Masterclass 3: Feature Engineering, RFM, and Churn Target Construction.*
