# Real-Data Roadmap

## Purpose

Version 0.1 uses synthetic data for controlled pipeline validation. The next goal is to make the project more convincing by testing the same ideas on public e-commerce datasets.

This roadmap compares three candidate datasets and explains how each one fits a staged research plan.

## Version 0.2: UCI Online Retail Dataset

**Best use:** quick real transaction-level smoke test.

The UCI Online Retail dataset is transaction-level data. Common columns include:

- `InvoiceNo`
- `StockCode`
- `Quantity`
- `InvoiceDate`
- `UnitPrice`
- `CustomerID`
- `Country`

### What It Supports

This dataset can be aggregated from transactions to customer-level features such as:

- `purchase_count`
- `total_spending`
- `average_order_value`
- product diversity
- invoice count
- return or cancellation proxy, such as canceled invoices or negative quantities
- days since last purchase

### What It Does Not Support Well

It does not directly support:

- browsing behavior
- cart behavior
- coupon usage
- discount dependency
- session-level behavior

### Role in the Roadmap

Use this dataset as **Version 0.2**, a real transaction smoke test. The goal is to prove that the pipeline can accept real public transaction data, not to fully represent promotion-period browsing behavior.

## Version 0.3: Kaggle Multi-Category E-commerce Behavior Dataset

**Best use:** closest match to the current research question.

This dataset is event-level behavior data. It may include:

- view events
- cart events
- purchase events
- `user_id`
- `user_session`
- `product_id`
- `event_time`
- `price`

### What It Supports

This dataset can generate features that are close to the current synthetic schema:

- `pages_viewed`
- `cart_additions`
- `purchase_count`
- `conversion_rate`
- `cart_to_purchase_rate`
- `session_count`
- `total_spending`
- product diversity
- event timing features

### Practical Note

The dataset can be large, so the first real-data version should sample events or use a limited time window before scaling up.

### What It Does Not Support Well

It may not directly support:

- return behavior
- coupon usage
- discount ratio
- discount dependency
- confirmed anomaly or fraud labels

### Role in the Roadmap

Use this dataset as **Version 0.3**, the event-level behavior version. It is the best match for studying view-cart-purchase behavior and promotion-period user activity.

## Version 0.4: Olist Brazilian E-Commerce Dataset

**Best use:** future graph extension.

The Olist dataset is a multi-table e-commerce dataset. It may include:

- orders
- customers
- products
- sellers
- payments
- reviews

### What It Supports

This dataset is useful for graph-style analysis because it naturally links multiple entity types:

- customer-order-product graph
- customer-product-seller graph
- order-payment-review graph
- seller-product relationships
- review and payment behavior analysis

### What It Does Not Support Well

It does not directly support:

- browsing behavior
- cart behavior
- coupon usage
- user sessions
- event-level promotion browsing paths

### Role in the Roadmap

Use this dataset as **Version 0.4**, the graph extension stage. It is useful for moving from user-level tabular anomaly screening toward customer-product-seller graph analysis.

## Recommended Roadmap

| Version | Dataset | Purpose |
|:--------|:--------|:--------|
| 0.1 | Synthetic promotion user behavior data | Controlled MVP for pipeline validation |
| 0.2 | UCI Online Retail | Real transaction-level smoke test |
| 0.3 | Kaggle Multi-Category E-commerce Behavior Dataset | Event-level view/cart/purchase behavior modeling |
| 0.4 | Olist Brazilian E-Commerce Dataset or event-level graph data | Graph anomaly detection and matrix/tensor representation |

## Long-Term Direction

The long-term direction is to move from tabular anomaly screening to richer representations:

- user-level tabular behavior features
- event-level behavior sequences
- user-product-coupon graphs
- user-product-time-behavior tensors

This progression keeps the current project beginner-friendly while creating a clear path toward graph learning, matrix/tensor methods, and anomaly detection research.
