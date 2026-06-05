# Real Event Data Validation Summary

## Purpose

This report checks whether the synthetic-data anomaly screening workflow can run on real event-level e-commerce behavior logs after aggregating events into user-level features.

This is not a fraud detection benchmark. The dataset does not provide confirmed anomaly labels, so the results should be interpreted as behaviorally unusual users that require further validation.

## Input Data

- Input path: `data/raw/synerise`
- Sample rows requested: 300000
- Events after loading/filtering: 300000
- Aggregated users: 40536
- Event types observed: ['cart', 'purchase', 'remove_from_cart', 'search', 'view']
- Sampling note: For the Synerise multi-file loader, sample_n_rows is split approximately evenly across event files. This is useful for workflow validation, but it should not be interpreted as the natural traffic distribution of the full dataset.
- Timestamp available: True
- Price available: True
- Price note: Price may be anonymized or bucketed depending on the public dataset; interpret it as a price signal unless the dataset documentation says otherwise.
- Session id available: False

Unavailable fields are documented instead of being faked: coupon_usage, discount_ratio, return_count, session_id, confirmed_fraud_label.

## Feature Columns Used

| feature                       |
|:------------------------------|
| event_count                   |
| view_count                    |
| cart_count                    |
| remove_from_cart_count        |
| purchase_count                |
| search_count                  |
| unique_items                  |
| active_days                   |
| days_since_last_purchase      |
| price_signal_total            |
| average_purchase_price_signal |
| conversion_rate               |
| cart_to_purchase_rate         |
| purchase_per_active_day       |
| actions_per_active_day        |
| item_diversity_ratio          |
| action_diversity              |
| zero_purchase_indicator       |
| low_activity_indicator        |
| behavior_sparsity             |

## Clustering and Anomaly Screening

- K-means clusters: 5
- Silhouette score: 0.315
- Isolation Forest anomaly rate: 8.0%

## Key Takeaways

- The sampled real event logs were successfully converted into user-level behavior features.
- The existing unsupervised workflow ran end-to-end on real event data without using anomaly labels.
- The most common flagged patterns are summarized below as review categories, not confirmed fraud labels.
- Because the Synerise sample is balanced across event files for workflow validation, behavior ratios should not be interpreted as full-site business conversion rates.

## Interpretable Anomaly Types

| anomaly_type                 |   count |
|:-----------------------------|--------:|
| not_flagged                  |   37293 |
| low_conversion_anomaly       |    1609 |
| high_purchase_signal_anomaly |    1475 |
| high_activity_anomaly        |     134 |
| remove_from_cart_anomaly     |      25 |

## Normal vs Anomalous User Profile

| is_anomaly   |   event_count |   view_count |   cart_count |   remove_from_cart_count |   purchase_count |   search_count |   unique_items |   active_days |   days_since_last_purchase |   price_signal_total |   average_purchase_price_signal |   conversion_rate |   cart_to_purchase_rate |   purchase_per_active_day |   actions_per_active_day |   item_diversity_ratio |   action_diversity |   zero_purchase_indicator |   low_activity_indicator |   behavior_sparsity |
|:-------------|--------------:|-------------:|-------------:|-------------------------:|-----------------:|---------------:|---------------:|--------------:|---------------------------:|---------------------:|--------------------------------:|------------------:|------------------------:|--------------------------:|-------------------------:|-----------------------:|-------------------:|--------------------------:|-------------------------:|--------------------:|
| normal       |         2.989 |        0.137 |        0.619 |                    0.811 |            1.046 |          0.375 |          1.713 |         1.436 |                     76.968 |               58.161 |                          31.353 |             0     |                   0.072 |                     0.75  |                    1.99  |                  0.75  |              1.289 |                     0.456 |                    0.443 |               0.742 |
| anomalous    |        58.133 |       16.925 |       11.383 |                    9.171 |            6.47  |         14.185 |         13.623 |         7.948 |                     52.452 |              265.053 |                          39.93  |             0.006 |                   0.45  |                     1.636 |                    8.885 |                  0.357 |              2.99  |                     0.207 |                    0     |               0.402 |

## Cluster Profile

|   cluster |   event_count |   view_count |   cart_count |   remove_from_cart_count |   purchase_count |   search_count |   unique_items |   active_days |   days_since_last_purchase |   price_signal_total |   average_purchase_price_signal |   conversion_rate |   cart_to_purchase_rate |   purchase_per_active_day |   actions_per_active_day |   item_diversity_ratio |   action_diversity |   zero_purchase_indicator |   low_activity_indicator |   behavior_sparsity |
|----------:|--------------:|-------------:|-------------:|-------------------------:|-----------------:|---------------:|---------------:|--------------:|---------------------------:|---------------------:|--------------------------------:|------------------:|------------------------:|--------------------------:|-------------------------:|-----------------------:|-------------------:|--------------------------:|-------------------------:|--------------------:|
|         0 |         2.645 |        0     |        0.022 |                    0.537 |            2.075 |          0.011 |          1.969 |         1.419 |                     77.283 |              111.687 |                          57.359 |             0     |                   0.004 |                     1.496 |                    1.791 |                  0.825 |              1.194 |                     0     |                    0.45  |               0.761 |
|         1 |       112.943 |       25.501 |       23.259 |                   20.87  |           15.386 |         27.927 |         29.685 |        15.227 |                     30.863 |              572.004 |                          39.957 |             0.002 |                   0.319 |                     2.374 |                   10.408 |                  0.407 |              3.069 |                     0.083 |                    0     |               0.386 |
|         2 |         3.291 |        0.495 |        0.926 |                    1.176 |            0     |          0.694 |          1.569 |         1.426 |                     26.6   |                0.001 |                           0.001 |             0     |                   0     |                     0     |                    2.117 |                  0.726 |              1.151 |                     1     |                    0.502 |               0.77  |
|         3 |        16.762 |        2.777 |        4.428 |                    2.529 |            2.227 |          4.801 |          4.267 |         3.427 |                     68.184 |              119.306 |                          47.997 |             0.005 |                   0.757 |                     0.945 |                    5.395 |                  0.364 |              2.905 |                     0.157 |                    0     |               0.419 |
|         4 |      1215.62  |      744.885 |      190.423 |                  110.154 |           22.654 |        147.5   |        137.538 |        63.962 |                     40.944 |              648.577 |                          28.215 |             0.003 |                   0.169 |                     0.471 |                   22.571 |                  0.168 |              3.692 |                     0.308 |                    0     |               0.262 |

## Interpretation

The real-data pipeline validates transferability at the workflow level: event logs can be converted into user-level behavior features, the unsupervised pipeline can run, and detected anomalies can be summarized with transparent evidence and suggested analyst actions.

Anomaly still does not mean fraud. It means the user is behaviorally unusual relative to the sampled event log.

## Limitations

- The result depends on the sampled time window and rows.
- The Synerise multi-file sample is approximately balanced across event files, so it is not a natural traffic-distribution sample.
- No confirmed anomaly or fraud labels are available.
- Coupon usage, real discount dependency, and return behavior may be unavailable.
- If price or session fields are missing, price-signal and session features are omitted or imputed from available fields.
- For Synerise, price should be interpreted as a dataset-provided price signal, not verified real revenue.
- Further validation should inspect raw event histories and domain context.
