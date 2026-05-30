# Research Notes: Promotion Behavior Anomaly Detection

## Project Research Question

This project studies **promotion-period user behavior anomaly detection under missing and sparse signals**.

The central question is:

> Can an unsupervised learning pipeline identify behaviorally unusual users during a large e-commerce promotion when user signals are sparse, partially missing, and unlabeled?

The current project is an introductory research prototype. It is not a finished fraud detection system.

## Why This Is Not Generic Customer Segmentation

Generic customer segmentation usually groups users for marketing, personalization, or customer management.

This project focuses on a different problem: identifying users whose promotion-period behavior deviates from the majority under incomplete and sparse behavior signals.

Clustering is included, but it is used mainly to support interpretation. The main focus is anomaly detection under missing and sparse user behavior data.

## Connection to Tabular Anomaly Detection

The current version uses user-level tabular behavior features, such as browsing activity, cart additions, purchases, spending, discount usage, returns, and session counts.

This tabular representation makes the first version easy to run, inspect, and explain. It also provides a baseline before moving to relational or temporal representations.

The current synthetic version is a controlled MVP for validating the pipeline. Real-data validation is the next step, with the main direction being event-level view/cart/purchase/session behavior from the Kaggle Multi-Category E-commerce Behavior Dataset. The long-term direction is to move from tabular anomaly screening to event-level behavior modeling and graph/tensor anomaly detection.

## Connection to Missing-Value Anomaly Detection

Promotion behavior data can contain missing values, especially for discount usage and return behavior. A missing value is not always equivalent to zero.

The project compares two feature representations:

- imputation-only features
- imputation plus missingness indicator features

This missingness sensitivity experiment checks whether explicitly modeling missingness changes anomaly detection results.

## Connection to Pseudo-Anomaly / Noise Evaluation

Real anomaly labels are usually unavailable in unsupervised anomaly detection.

To avoid overclaiming, this project includes a pseudo-anomaly sanity check. It perturbs normal users by increasing activity, discount dependency, and return behavior, then checks whether Isolation Forest assigns stronger anomaly scores to these perturbed users.

This is not a real benchmark. It is only a sanity check that the model reacts in the expected direction under controlled perturbations.

## Connection to Actionable Interpretation

The interpretation layer bridges anomaly detection output and real-world decision making. Instead of only returning anomaly labels, the project assigns each detected anomaly an interpretable type, supporting evidence, and a suggested next action.

This helps answer what an analyst could do after anomaly detection, such as reviewing high-value users, checking low-conversion behavior, inspecting promotion-abuse-like patterns, or investigating missingness-related data quality issues.

For Version 0.1, the interpretation layer uses transparent quantile-based heuristics. These rules are meant to be readable and easy to inspect, not universal decision rules. They should be recalibrated when real data is introduced.

This also motivates future graph-based analysis. Some follow-up actions require relational data that is not available in the current tabular prototype, such as user-product-coupon-device connections, repeated coupon use across products, or abnormal interaction bursts across sessions.

## Connection to Graph Anomaly Detection

Future work can extend the project from tabular user-level features to a user-product-coupon graph.

Possible graph components:

- nodes: users, products, coupons
- edges: view, cart, purchase, coupon use, return
- edge attributes: time, price, discount ratio, quantity

Graph anomaly detection could study unusual users, products, coupons, edges, or subgraphs, such as users connected to unusually many coupons or dense user-coupon-product interaction patterns during a short promotion window.

## Connection to Matrix and Tensor Methods

Promotion behavior can also be represented using sparse matrices or tensors.

Possible representations include:

- user x product interaction matrix
- user x coupon usage matrix
- user x product x time behavior tensor
- user x product x time x behavior tensor

These representations are relevant because e-commerce interaction data is naturally sparse and high-dimensional.

## Limitations

- The current data is synthetic.
- Synthetic data is used for controlled validation, not evidence of real promotion behavior.
- There are no real ground-truth anomaly labels.
- The models are simple baselines: K-means, PCA, and Isolation Forest.
- The current version uses aggregated user-level tabular features only.
- The anomaly categories are rule-based interpretations, not verified labels.
- The project does not claim to detect fraud.
- Real-data validation is the next step.

## Next Steps

- Validate the pipeline on sampled Kaggle Multi-Category event-level behavior data.
- Compare additional anomaly detection algorithms.
- Build a user-product-coupon graph representation.
- Add graph-based anomaly detection methods.
- Explore user-product-time-behavior tensor representations.
- Evaluate results with domain knowledge or business validation when real data is available.
