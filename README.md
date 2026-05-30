# Promotion Behavior Anomaly Detection under Missing and Sparse User Signals

## Project Overview

This repository is an introductory, research-oriented prototype for **promotion-period user behavior anomaly detection** in e-commerce scenarios such as 618.

Current status: Version 0.1 is a synthetic-data MVP for controlled pipeline validation. Real-data validation is planned as Version 0.2/0.3.

Recommended reading order: `README.md` -> `docs/research_notes.md` -> `results/actionable_anomaly_report.md` -> `docs/real_data_roadmap.md`.

The project starts from a practical question:

> When user behavior during a large promotion is sparse, partially missing, and unlabeled, can we identify users whose behavior deviates from the majority in an interpretable way?

The current version is a **tabular unsupervised anomaly detection prototype**. It uses synthetic user-level behavior data to validate the end-to-end pipeline before moving to real promotion data. It is not a production fraud detection system.

The project turns unsupervised anomaly detection into an analyst review workflow: anomaly detection -> anomaly type -> evidence -> suggested action.

The final output is not a fraud label, but a prioritized review list with anomaly type, evidence, and suggested analyst action.

## What This Project Is Trying to Study

Promotion-period behavior is different from ordinary shopping behavior. Users may browse heavily, add many products to the cart, use coupons intensively, purchase rarely, return items, or show unusually high activity in a short time window.

At the same time, real e-commerce behavior logs are often:

- sparse: many users have few purchases, few returns, or many zero-valued behavior signals
- partially missing: discount usage or return records may be unavailable, delayed, or incomplete
- unlabeled: there may be no reliable ground-truth anomaly or fraud labels

This project studies how to build a simple, interpretable anomaly detection pipeline under these conditions.

## Important Interpretation

**Anomaly does not mean fraud.**

In this project, an anomaly means that a user's behavior differs from the majority pattern. A detected anomaly may be:

- a high-value customer
- a low-conversion user with heavy browsing
- a promotion-sensitive user
- a high-return user
- a high-activity user
- a data-quality or missingness-related case

Any real business conclusion would require further validation with domain knowledge and real data.

## Why This Is Not Generic Customer Segmentation

Generic customer segmentation usually focuses on grouping users for marketing, personalization, or customer management.

This project is different because it focuses on **unusual behavior under sparse and missing promotion signals**. Clustering is used only as one part of the analysis. The main goal is to connect segmentation, missing-data handling, and unsupervised anomaly detection.

Research-oriented elements include:

1. Simulating sparse and partially missing behavior signals.
2. Comparing imputation-only features with missingness-aware features.
3. Using unsupervised anomaly detection because real anomaly labels are unavailable.
4. Adding a pseudo-anomaly sanity check instead of claiming a real benchmark.
5. Preparing a path toward graph and tensor representations of user-product-coupon behavior.

## Dataset Strategy

### Synthetic Demo Data

The current version generates about 1,000 synthetic users with behavior patterns inspired by promotion-period e-commerce activity.

The synthetic setting is intentionally used to test whether the full workflow works before introducing real-data noise and field mismatch. It is used for controlled validation, not as evidence of real promotion behavior.

Raw features include:

- `user_id`
- `browsing_time`
- `pages_viewed`
- `cart_additions`
- `purchase_count`
- `total_spending`
- `average_order_value`
- `discount_usage_count`
- `discount_ratio`
- `return_count`
- `days_since_last_purchase`
- `session_count`
- `user_type`

The synthetic `user_type` field is used for sanity checking and interpretation only. It is not used as a supervised training label.

Synthetic user types:

- `normal`
- `high_value`
- `low_conversion`
- `promotion_abuse_like`
- `high_activity_anomaly`

### Real Data Later

The synthetic data is only used to make the first version runnable and easy to inspect. A future version should use real or public e-commerce promotion data, such as user behavior logs around a large campaign.

## Current MVP and Real-Data Roadmap

### Current Stage: Synthetic Controlled MVP

The current version uses synthetic data for controlled pipeline validation. Synthetic data makes it possible to test sparse and missing behavior signals, the missingness sensitivity experiment, the pseudo-anomaly sanity check, and the actionable anomaly interpretation layer in a reproducible way.

This is not a claim of real fraud detection. It is a controlled prototype for validating the project structure and research workflow.

The rule-based interpretation layer uses transparent quantile-based heuristics for Version 0.1. These thresholds are not claimed to be universal and should be recalibrated on real data.

### Next Stage: Kaggle Event-Level Behavior Validation

The main next real-data step is the Kaggle Multi-Category E-commerce Behavior Dataset because it best matches the project research question. It contains event-level view, cart, purchase, session, product, time, and price information.

The planned workflow is to sample a manageable subset of event-level data, aggregate events into user-level features, and run the same anomaly screening pipeline on real behavior logs. Candidate features include view count, cart count, purchase count, session count, total spending, conversion rate, cart-to-purchase rate, product diversity, and days since last purchase.

This stage will test whether the workflow transfers from synthetic data to real event-level e-commerce behavior.

### Later Stage: User-Product Graph and Tensor Extension

The longer-term direction is to move from tabular anomaly screening toward user-product graph and tensor representations. Event-level behavior can be used to build user-product interaction graphs and user x product x time x behavior tensors.

UCI Online Retail may be used as an optional lightweight transaction-level fallback smoke test. Olist Brazilian E-Commerce may be used as a later graph-oriented reference dataset, but neither is the main immediate path.

See `docs/real_data_roadmap.md` for the simplified real-data plan.

## Sparse and Missing Behavior Signals

The project explicitly simulates missing values in:

- `discount_usage_count`
- `return_count`

It also creates missingness indicator features:

- `discount_missing`
- `return_missing`

This design reflects a common issue in behavior data: a missing value is not always the same as zero. For example, a missing return count may mean no return, delayed return data, or incomplete data collection. The project therefore compares feature representations with and without missingness indicators.

## Feature Engineering

The pipeline creates interpretable user behavior features:

- `conversion_rate = purchase_count / pages_viewed`
- `cart_to_purchase_rate = purchase_count / cart_additions`
- `spending_per_session = total_spending / session_count`
- `discount_dependency = discount_usage_count / max(purchase_count, 1)`
- `return_rate = return_count / max(purchase_count, 1)`

Division by zero is handled safely. These features make the results easier to explain than raw counts alone.

## Methods

### K-means Clustering

K-means is used to form rough user behavior segments. This helps describe whether users appear to fall into groups such as high-value, low-conversion, promotion-sensitive, or high-activity behavior profiles.

### PCA Visualization

PCA reduces the feature space to two dimensions for visualization. It is used to inspect cluster structure and the location of detected anomalies.

### Isolation Forest

Isolation Forest is used for unsupervised anomaly detection. It does not require ground-truth labels and is suitable for a first prototype where real anomaly labels are unavailable.

### Missingness Sensitivity Experiment

The project compares two feature settings:

- imputation-only features
- imputation plus missingness indicator features

The experiment reports:

- anomaly overlap rate
- number of users whose anomaly label changes
- synthetic user types most affected by missingness-aware modeling

This makes the project closer to anomaly detection research under missing tabular signals.

### Pseudo-Anomaly Sanity Check

Because real anomaly labels are unavailable, the project includes a simple pseudo-anomaly check. It perturbs normal users by increasing activity, discount dependency, and return behavior, then checks whether Isolation Forest assigns stronger anomaly scores to these pseudo-anomalies.

This is only a sanity check. It is not a real benchmark and should not be interpreted as evidence of real fraud detection performance.

## What Happens After Anomaly Detection?

The project outputs a prioritized review list, not a final fraud decision.

Each detected anomaly receives:

- an interpretable anomaly type
- rule-based evidence
- a suggested next action for analysts

Example anomaly types include:

- `high_value_anomaly`
- `low_conversion_anomaly`
- `promotion_abuse_like_anomaly`
- `high_activity_anomaly`
- `data_quality_anomaly`
- `mixed_anomaly`

`mixed_anomaly` means multiple abnormal behavior signals overlap. It should be treated as a higher-priority review case rather than forced into a single category.

The goal is to help analysts decide what to investigate next. For example, a high-value anomaly may support VIP or retention analysis, while a promotion-abuse-like anomaly may require manual review or downstream risk scoring. This interpretation layer makes the prototype more useful for e-commerce promotion analysis while still avoiding any claim of confirmed fraud detection.

## Outputs

Running the pipeline creates:

- `data/synthetic_promotion_user_behavior.csv`
- `results/user_behavior_with_clusters_and_anomalies.csv`
- `results/summary.md`
- `results/missingness_sensitivity.md`
- `results/pseudo_anomaly_check.md`
- `results/actionable_anomaly_report.md`
- `figures/pca_clusters.png`
- `figures/anomaly_pca.png`
- `figures/feature_distributions.png`
- `figures/missingness_comparison.png`
- `figures/pseudo_anomaly_scores.png`

## Preliminary Findings

The generated reports summarize:

- dataset size and synthetic user type distribution
- K-means cluster profiles
- cluster-wise anomaly rates and interpretations
- normal vs anomalous user profile comparison
- missingness sensitivity results
- pseudo-anomaly sanity check results

These findings are preliminary because the data is synthetic and there are no real ground-truth anomaly labels.

## Connection to Prof. Jicong Fan's Research Directions

This project is designed to connect with several relevant research directions:

- **Clustering:** K-means is used to segment promotion-period users by behavior.
- **Anomaly detection:** Isolation Forest identifies behaviorally unusual users in an unsupervised setting.
- **Tabular and missing data:** The pipeline studies sparse and partially missing user behavior signals with imputation and missingness indicators.
- **Graph learning:** Future work can model users, products, coupons, and interactions as a heterogeneous graph.
- **Matrix and tensor methods:** User-product, user-coupon, and user-product-time behavior can be represented as sparse matrices or tensors.

The current version should be understood as a tabular starting point. The longer-term direction is graph-based and tensor-based anomaly detection for promotion-period user behavior.

## Graph and Tensor Extension

A future graph version could represent:

- nodes: users, products, coupons
- edges: view, cart, purchase, coupon use, return
- edge attributes: time, price, discount ratio, quantity

Possible graph anomalies include users connected to unusually many coupons, products linked to high-return users, dense user-coupon-product subgraphs, or abnormal bursts of interactions.

A future tensor version could represent:

- user x product x time behavior
- user x product x behavior type
- user x product x coupon x time

The graph extension blueprint is documented in `docs/graph_extension.md`.

## Limitations

- The current dataset is synthetic.
- Synthetic data is used for controlled validation, not evidence of real promotion behavior.
- There are no real ground-truth anomaly labels.
- The project does not claim to detect real fraud.
- Unsupervised anomaly results require business validation.
- The current version uses aggregated tabular features only.
- The anomaly categories are rule-based interpretations, not verified labels.
- The pseudo-anomaly experiment is a sanity check, not a real benchmark.
- Real-data validation is the next step.

## Future Work

- Use real e-commerce promotion data.
- Build a user-product-coupon graph.
- Explore graph-based anomaly detection.
- Add temporal behavior modeling.
- Represent user-product-time-behavior as a sparse tensor.
- Compare additional unsupervised anomaly detection methods.

## How to Run

Create and activate a Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the full pipeline:

```bash
python src/run_pipeline.py
```
