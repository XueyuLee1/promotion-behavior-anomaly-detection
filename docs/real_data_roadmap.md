# Real-Data Roadmap

## Purpose

Version 0.1 uses synthetic data for controlled pipeline validation. The next goal is to test whether the same anomaly screening workflow transfers to real event-level e-commerce behavior data.

This roadmap uses a simplified main path:

1. **Current stage:** synthetic controlled MVP.
2. **Next stage:** RecSys Challenge 2025 / Synerise for real event-level validation, with RetailRocket as a simpler fallback.
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

## Real Event-Level Validation: RecSys Challenge 2025 / Synerise

**Main next dataset:** RecSys Challenge 2025 / Synerise.

This dataset is the best match for the current research question because it is recent, real, and focused on online retailer event-level behavior. It includes interactions such as:

- page visit events
- search query events
- add-to-cart events
- remove-from-cart events
- product-buy events
- user identifier, such as `client_id`
- product identifier, such as `sku`
- timestamp
- anonymized price bucket from product properties, if available

These fields directly support promotion-period user behavior screening based on view, cart, remove-from-cart, purchase, product, time, and price-intensity patterns. The Synerise price field is a bucket, not an original transaction price.

## Sampling Strategy

The Synerise dataset can be large, so the current real-data validation uses a manageable sample before scaling up.

Possible sampling choices:

- use a limited time window, such as one week or one month
- sample a fixed number of events
- sample a fixed number of users
- filter to users with at least a small number of interactions
- keep the sampling rule documented for reproducibility

The current multi-file Synerise loader splits `sample_n_rows` approximately evenly across event files. This makes the workflow easier to validate on a small sample, but it does not preserve the natural traffic distribution of the full dataset.

The goal is not to use the full dataset immediately. The goal is to create a reliable first real-data validation of the pipeline.

## Event-to-User Feature Mapping

Event-level records can be aggregated into user-level features that match the current pipeline.

| Event-level source | User-level feature |
|:-------------------|:-------------------|
| count of `view` events | `pages_viewed` or `view_count` |
| count of `cart` events | `cart_additions` or `cart_count` |
| count of `purchase` events | `purchase_count` |
| unique session values, if available | `session_count` |
| sum of available purchase price signal | `price_signal_total` |
| purchase count divided by view count | `conversion_rate` |
| purchase count divided by cart count | `cart_to_purchase_rate` |
| unique `sku` or item values | `unique_items` |
| latest purchase time | `days_since_last_purchase` |

After aggregation, the same preprocessing, clustering, anomaly detection, missingness sensitivity, and interpretation workflow can be reused.

## What Synerise Event Data Supports

This dataset can support:

- event-level view/cart/purchase behavior
- remove-from-cart behavior
- session-level behavior, if session fields are available
- user-product interactions
- conversion behavior
- product diversity
- time-window analysis
- user-product graph construction
- future user-product-time-behavior tensor representation

## What Synerise Event Data Does Not Directly Support

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
- edges: view, cart, remove-from-cart, purchase
- edge attributes: event time, price, session id, behavior type

Possible tensor representation:

- user x product x time x behavior

This would move the project from tabular anomaly screening toward graph-based and tensor-based anomaly detection.

## Fallback: RetailRocket

RetailRocket can be used as a simpler fallback if Synerise is difficult to download or process.

It can support:

- view behavior
- add-to-cart behavior
- transaction behavior
- user-item interactions
- timestamp-based aggregation

It does not directly support:

- search behavior
- remove-from-cart behavior
- coupon behavior
- return behavior
- confirmed anomaly labels

For this reason, RetailRocket is a practical fallback for quickly validating the event-log-to-user-feature pipeline, but Synerise remains the preferred primary dataset.

## Optional Transaction Reference: UCI Online Retail

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
| Next | RecSys Challenge 2025 / Synerise | Real event-level page-visit/search/cart/remove/purchase validation |
| Fallback | RetailRocket | Simpler real event-log validation with view/add-to-cart/transaction events |
| Optional transaction reference | UCI Online Retail | Lightweight transaction-level smoke test |
| Later | User-product graph or user-product-time-behavior tensor | Graph/tensor anomaly detection extension |
| Optional reference | Olist Brazilian E-Commerce Dataset | Later multi-table graph-oriented reference |

## Summary

The main next step is Synerise event-level behavior validation. RetailRocket is the fallback if Synerise is too difficult to process quickly. UCI and Olist are useful references, but they should not distract from the main project direction: moving from a synthetic tabular MVP to real event-level behavior anomaly screening, and later to user-product graph and tensor representations.
