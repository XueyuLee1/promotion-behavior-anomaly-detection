# Graph Extension Blueprint: User-Product-Coupon Promotion Behavior Graph

## Purpose

The current MVP uses aggregated tabular user behavior features. A natural research extension is to represent promotion-period behavior as a heterogeneous graph. This would better preserve relationships among users, products, coupons, and behavior events.

This document is a design blueprint only. It does not implement a graph neural network yet.

## Graph Nodes

The graph could include three main node types:

- `user`: a customer or account participating in the promotion.
- `product`: an item viewed, added to cart, purchased, or returned.
- `coupon`: a coupon, discount code, voucher, or promotion rule used during the event.

Optional future node types:

- `seller`
- `category`
- `brand`
- `promotion_campaign`

## Graph Edges

Possible edge types:

- `user -> product: view`
- `user -> product: cart`
- `user -> product: purchase`
- `user -> coupon: coupon_use`
- `user -> product: return`
- `coupon -> product: applicable_to`

These edge types make the graph heterogeneous because nodes and edges have different meanings.

## Edge Attributes

Each edge can store event-level attributes:

- `time`
- `price`
- `discount_ratio`
- `quantity`
- `device_type`
- `session_id`
- `promotion_stage`

For example, a purchase edge could store purchase time, quantity, final price, and discount ratio.

## Possible Graph Anomalies

Graph anomaly detection can search for unusual nodes, edges, or subgraphs.

Potential graph-level anomaly patterns:

- users connected to unusually many coupons
- users repeatedly connected to high-discount purchases and returns
- products linked to unusually high-return users
- dense user-coupon-product subgraphs during a short promotion window
- abnormal interaction bursts from a small group of users
- products that receive many views and carts but very few purchases
- coupons used across unusually diverse products or user groups

These patterns should be treated as behavioral anomalies, not confirmed fraud.

## Connection to Graph Learning

Graph learning methods can use both node features and graph structure. For example:

- node embeddings can represent user behavior patterns
- graph clustering can identify groups of similar users or products
- graph anomaly detection can identify unusual users, products, coupons, edges, or subgraphs
- temporal graph methods can model promotion-period behavior bursts

Possible beginner-to-advanced progression:

1. Build a simple user-product-coupon edge list.
2. Compute graph statistics such as degree, coupon-use degree, return-neighbor ratio, and product return concentration.
3. Use graph features in the current tabular anomaly pipeline.
4. Try node embedding methods such as Node2Vec.
5. Explore graph neural networks or graph autoencoders when the data and research question are clearer.

## Connection to Matrix and Tensor Methods

A user-product interaction graph can also be represented as matrices:

- user-product view matrix
- user-product purchase matrix
- user-coupon usage matrix
- product-coupon applicability matrix

Temporal promotion behavior can be represented as tensors:

- user x product x time
- user x product x behavior_type
- user x product x coupon x time

Sparse matrix and tensor representations are useful because e-commerce behavior is naturally sparse: most users interact with only a small fraction of products and coupons.

## Research Direction

This extension connects the MVP to clustering, anomaly detection, graph learning, matrix/tensor methods, and recommender-system-style user-item behavior modeling. The tabular MVP is the first step; the graph version would preserve relational information that aggregated user-level features cannot capture.
