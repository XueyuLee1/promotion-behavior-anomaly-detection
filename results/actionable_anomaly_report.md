# Actionable Anomaly Report

## What Happens After Anomaly Detection?

The anomaly detector produces a review list, not a final fraud decision. This report translates detected anomalies into interpretable behavior types, supporting evidence, and suggested follow-up actions.

The purpose is to help analysts decide what to inspect next during an e-commerce promotion period.

## Detected Anomalies

- Total users: 1000
- Detected anomalies: 80
- Anomaly rate: 8.0%

## Interpretable Anomaly Types

| anomaly_type                 |   count |
|:-----------------------------|--------:|
| mixed_anomaly                |      40 |
| high_value_anomaly           |      30 |
| promotion_abuse_like_anomaly |       7 |
| low_conversion_anomaly       |       3 |

## Typical Feature Patterns by Type

| anomaly_type                 |   pages_viewed |   cart_additions |   purchase_count |   total_spending |   discount_ratio |   discount_dependency |   return_rate |   session_count |   discount_missing |   return_missing |
|:-----------------------------|---------------:|-----------------:|-----------------:|-----------------:|-----------------:|----------------------:|--------------:|----------------:|-------------------:|-----------------:|
| high_value_anomaly           |         60.2   |           11.267 |            9.967 |         2802.94  |            0.163 |                 0.2   |         0.008 |           9.133 |              0.167 |            0.133 |
| low_conversion_anomaly       |        131.667 |           12.667 |            0.667 |           59.493 |            0.197 |                 0.667 |         1     |          15.333 |              0.333 |            0     |
| mixed_anomaly                |        187.55  |            9.65  |            3.3   |          404.922 |            0.344 |                 1.218 |         0.218 |          29.475 |              0.275 |            0.15  |
| promotion_abuse_like_anomaly |         71.286 |            6.571 |            2.429 |          269.906 |            0.698 |                 3.524 |         0.619 |           7.429 |              0.429 |            0     |

## Suggested Analyst Follow-up Actions

| anomaly_type                 | meaning                                                                                           | action                                                                                      |
|:-----------------------------|:--------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------|
| high_value_anomaly           | Valuable customer whose behavior is unusual because spending and purchase activity are very high. | Review for retention, VIP analysis, and personalized recommendation opportunities.          |
| low_conversion_anomaly       | User shows interest through browsing or cart activity but does not convert strongly.              | Investigate price, inventory, page experience, recommendation quality, and coupon design.   |
| promotion_abuse_like_anomaly | Promotion-abuse-like behavior may be present, but this is not confirmed fraud.                    | Send to manual review or a downstream risk-scoring process; do not directly label as fraud. |
| high_activity_anomaly        | User shows very high activity that could reflect a power user, automation, or abnormal traffic.   | Check device, IP, session, and timing patterns when real event-level data is available.     |
| data_quality_anomaly         | The anomaly is strongly related to missing behavior signals.                                      | Check data collection, logging coverage, delayed records, and the missingness mechanism.    |
| mixed_anomaly                | Multiple unusual behavior patterns appear at the same time.                                       | Prioritize for analyst review and inspect user-level behavior history in more detail.       |

## Example Review List

| user_id   | anomaly_type                 |   anomaly_score | anomaly_evidence                                                                                                                                                                                                                                          | suggested_action                                                                            |
|:----------|:-----------------------------|----------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------|
| U00997    | mixed_anomaly                |         0.13057 | low_conversion_anomaly: high pages_viewed, high cart_additions, low purchase_count; promotion_abuse_like_anomaly: high discount_dependency, high discount_ratio, high return_rate; high_activity_anomaly: very high session_count, very high pages_viewed | Prioritize for analyst review and inspect user-level behavior history in more detail.       |
| U00770    | high_value_anomaly           |         0.12922 | high total_spending; high purchase_count; low return_rate                                                                                                                                                                                                 | Review for retention, VIP analysis, and personalized recommendation opportunities.          |
| U00992    | mixed_anomaly                |         0.11032 | low_conversion_anomaly: high pages_viewed, high cart_additions, low purchase_count; promotion_abuse_like_anomaly: high discount_ratio, high return_rate; high_activity_anomaly: very high session_count, very high pages_viewed                           | Prioritize for analyst review and inspect user-level behavior history in more detail.       |
| U00974    | mixed_anomaly                |         0.11014 | low_conversion_anomaly: high pages_viewed, high cart_additions, low purchase_count, low conversion_rate; high_activity_anomaly: very high session_count, very high pages_viewed                                                                           | Prioritize for analyst review and inspect user-level behavior history in more detail.       |
| U00760    | high_value_anomaly           |         0.10045 | high total_spending; high purchase_count; low return_rate                                                                                                                                                                                                 | Review for retention, VIP analysis, and personalized recommendation opportunities.          |
| U00900    | promotion_abuse_like_anomaly |         0.10043 | high discount_ratio; high return_rate                                                                                                                                                                                                                     | Send to manual review or a downstream risk-scoring process; do not directly label as fraud. |
| U00750    | high_value_anomaly           |         0.09141 | high total_spending; high purchase_count; low return_rate                                                                                                                                                                                                 | Review for retention, VIP analysis, and personalized recommendation opportunities.          |
| U00995    | mixed_anomaly                |         0.09099 | low_conversion_anomaly: high pages_viewed, low purchase_count; promotion_abuse_like_anomaly: high discount_dependency, high return_rate; high_activity_anomaly: very high session_count, very high pages_viewed                                           | Prioritize for analyst review and inspect user-level behavior history in more detail.       |
| U00755    | high_value_anomaly           |         0.0887  | high total_spending; high purchase_count; low return_rate                                                                                                                                                                                                 | Review for retention, VIP analysis, and personalized recommendation opportunities.          |
| U00996    | mixed_anomaly                |         0.08608 | high_value_anomaly: high total_spending, high purchase_count, low return_rate; promotion_abuse_like_anomaly: high discount_ratio, high return_rate; high_activity_anomaly: very high session_count, very high pages_viewed                                | Prioritize for analyst review and inspect user-level behavior history in more detail.       |
| U00766    | high_value_anomaly           |         0.08471 | high total_spending; high purchase_count; low return_rate                                                                                                                                                                                                 | Review for retention, VIP analysis, and personalized recommendation opportunities.          |
| U00920    | mixed_anomaly                |         0.08301 | high_value_anomaly: high total_spending, high purchase_count; promotion_abuse_like_anomaly: high discount_ratio, high return_rate                                                                                                                         | Prioritize for analyst review and inspect user-level behavior history in more detail.       |

## Why This Does Not Mean Fraud

Anomaly means behaviorally unusual. It does not mean confirmed fraud. A high-value customer, a low-conversion user, a promotion-sensitive user, a high-activity user, or a data-quality issue can all appear anomalous in this prototype.

Any real business action should require validation with domain knowledge, real event-level data, and possibly manual review.

## Why This Is Useful for Promotion Analysis

Promotion campaigns create sudden changes in browsing, purchasing, discount usage, and return behavior. This report turns anomaly detection output into a prioritized starting point for follow-up analysis:

- retain or understand high-value unusual users
- inspect low-conversion behavior and promotion design
- review promotion-abuse-like patterns without directly labeling fraud
- investigate high-activity traffic with device, IP, or session data in future real datasets
- identify possible data collection or missingness issues
