# Real-Data Roadmap

## Purpose

Version 0.1 uses synthetic data for controlled pipeline validation. The next goal is to test whether the same anomaly screening workflow transfers to real event-level e-commerce behavior data.

This roadmap uses a simplified main path:

1. **Current stage:** synthetic controlled MVP.
2. **Next stage:** Kaggle Multi-Category E-commerce Behavior Dataset for real event-level validation.
3. **Later stage:** user-product graph and user-product-time-behavior tensor extension.

UCI Online Retail is only an optional transaction-level fallback smoke test. Olist Brazilian E-Commerce is only a possible later graph-oriented reference, not a required stage.

## Current Stage: Synthetic Controlled MVP

The current project validates the full workflow in a controlled setting:

- generate synthetic promotion-style users
- simulate sparse and missing behavior signals
- engineer interpretable user-level features
- run K-means clustering and PCA visualization
- run Isolation Forest anomaly detection
- run missingness sensitivity analysis
- run a pseudo-anomaly sanity check
- generate actionable anomaly interpretation

This stage is useful for checking that the full project structure works before introducing real-data noise, scale, and field mismatch.

## Next Stage: Kaggle Multi-Category E-commerce Behavior Dataset

**Main next dataset:** Kaggle Multi-Category E-commerce Behavior Dataset.

This dataset is the best match for the current research question because it contains event-level e-commerce behavior. It may include:

- view events
- cart events
- purchase events
- `user_id`
- `user_session`
- `product_id`
- `event_time`
- `price`

These fields directly support promotion-period user behavior screening based on view, cart, purchase, session, product, time, and spending patterns.

## Sampling Strategy

The Kaggle dataset can be large, so the first real-data validation should use a manageable sample before scaling up.

Possible sampling choices:

- use a limited time window, such as one week or one month
- sample a fixed number of events
- sample a fixed number of users
- filter to users with at least a small number of interactions
- keep the sampling rule documented for reproducibility

The goal is not to use the full dataset immediately. The goal is to create a reliable first real-data validation of the pipeline.

## Event-to-User Feature Mapping

Event-level records can be aggregated into user-level features that match the current pipeline.

| Event-level source | User-level feature |
|:-------------------|:-------------------|
| count of `view` events | `pages_viewed` or `view_count` |
| count of `cart` events | `cart_additions` or `cart_count` |
| count of `purchase` events | `purchase_count` |
| unique `user_session` values | `session_count` |
| sum of purchase prices | `total_spending` |
| purchase count divided by view count | `conversion_rate` |
| purchase count divided by cart count | `cart_to_purchase_rate` |
| unique `product_id` values | `product_diversity` |
| latest purchase time | `days_since_last_purchase` |

After aggregation, the same preprocessing, clustering, anomaly detection, missingness sensitivity, and interpretation workflow can be reused.

## What Kaggle Event Data Supports

This dataset can support:

- event-level view/cart/purchase behavior
- session-level behavior
- user-product interactions
- conversion behavior
- product diversity
- time-window analysis
- user-product graph construction
- future user-product-time-behavior tensor representation

## What Kaggle Event Data Does Not Directly Support

It may not directly support:

- real coupon usage
- real discount dependency
- return behavior
- confirmed anomaly or fraud labels
- business-validated risk outcomes

For these missing signals, the project should keep the interpretation cautious. Missing or unavailable fields should be documented instead of silently treated as real observed behavior.

## Later Stage: User-Product Graph and Tensor Extension

After event-level validation, the next research direction is to move beyond user-level tabular features.

Possible graph representation:

- nodes: users and products
- edges: view, cart, purchase
- edge attributes: event time, price, session id, behavior type

Possible tensor representation:

- user x product x time x behavior

This would move the project from tabular anomaly screening toward graph-based and tensor-based anomaly detection.

## Optional Fallback: UCI Online Retail

UCI Online Retail can be used as an optional lightweight transaction-level smoke test if a smaller real dataset is needed.

It can support:

- `purchase_count`
- `total_spending`
- `average_order_value`
- product diversity
- return or cancellation proxy
- days since last purchase

It does not directly support:

- browsing behavior
- cart behavior
- coupon behavior
- session-level behavior

For this reason, UCI Online Retail is not the main path. It is only a fallback transaction-level test.

## Optional Later Reference: Olist Brazilian E-Commerce Dataset

Olist Brazilian E-Commerce can be useful as a later graph-oriented reference because it contains multiple connected tables, such as customers, orders, products, sellers, payments, and reviews.

It can support customer-order-product-seller graph analysis, but it does not directly support view/cart/session behavior. Therefore, it is not the immediate real-data validation dataset for this project.

## Recommended Roadmap

| Stage | Dataset or representation | Purpose |
|:------|:--------------------------|:--------|
| Current | Synthetic promotion user behavior data | Controlled MVP for validating the full anomaly screening workflow |
| Next | Kaggle Multi-Category E-commerce Behavior Dataset | Real event-level view/cart/purchase/session validation |
| Optional fallback | UCI Online Retail | Lightweight transaction-level smoke test |
| Later | User-product graph or user-product-time-behavior tensor | Graph/tensor anomaly detection extension |
| Optional reference | Olist Brazilian E-Commerce Dataset | Later multi-table graph-oriented reference |

## Summary

The main next step is Kaggle event-level behavior validation. UCI and Olist are useful references, but they should not distract from the main project direction: moving from a synthetic tabular MVP to real event-level behavior anomaly screening, and later to user-product graph and tensor representations.
