# Promotion Behavior Anomaly Detection MVP Summary

## Dataset Size

- Number of users: 1000
- Number of raw behavior features: 11
- Number of engineered behavior features: 5
- Missingness indicators: discount_missing, return_missing

## Synthetic User Type Distribution

| user_type             |   count |
|:----------------------|--------:|
| normal                |     700 |
| low_conversion        |     100 |
| high_value            |      80 |
| promotion_abuse_like  |      70 |
| high_activity_anomaly |      50 |

## Cluster Profile Interpretation

K-means was used as a first segmentation method. The silhouette score is **0.198**, which gives a rough indication of how separated the clusters are in the scaled feature space.

|   cluster |   browsing_time |   pages_viewed |   cart_additions |   purchase_count |   total_spending |   discount_usage_count |   discount_ratio |   return_count |   session_count |   conversion_rate |   discount_dependency |   return_rate |
|----------:|----------------:|---------------:|-----------------:|-----------------:|-----------------:|-----------------------:|-----------------:|---------------:|----------------:|------------------:|----------------------:|--------------:|
|         0 |          57.746 |         39.269 |            4.283 |            2.87  |          350.934 |                  1.613 |            0.212 |          0.013 |           6.457 |             0.074 |                 0.514 |         0.003 |
|         1 |          57.917 |         40.164 |            4.708 |            0.447 |           51.802 |                  1.413 |            0.204 |          0     |           6.506 |             0.012 |                 1.186 |         0     |
|         2 |         195.28  |        167.196 |           14.957 |            0.768 |           82.544 |                  1.304 |            0.238 |          0     |          23.384 |             0.004 |                 0.981 |         0     |
|         3 |          98.185 |         62.462 |           10.673 |            9.25  |         2424.13  |                  2.043 |            0.156 |          0     |           9.5   |             0.151 |                 0.201 |         0     |
|         4 |         111.512 |         91.321 |            7.25  |            2.5   |          294.73  |                  3.826 |            0.361 |          1.429 |          12.536 |             0.044 |                 1.24  |         0.688 |

## Cluster-wise Anomaly Interpretation

This table connects user segmentation with anomaly detection. It describes which clusters contain more anomalous users and gives cautious business interpretations.

|   cluster_id |   cluster_size |   anomaly_rate | key_behavior_characteristics                                | possible_interpretation                                      |
|-------------:|---------------:|---------------:|:------------------------------------------------------------|:-------------------------------------------------------------|
|            0 |            361 |         0.0194 | moderate behavior profile                                   | mostly ordinary behavioral segment                           |
|            1 |            421 |         0.0071 | low conversion, high discount dependency                    | possible promotion-sensitive or return-heavy segment         |
|            2 |            138 |         0.1522 | high browsing volume, high session activity, low conversion | possible low-conversion segment with heavy browsing          |
|            3 |             52 |         0.5577 | high spending, high purchase count                          | possible high-value segment; anomalies may be valuable users |
|            4 |             28 |         0.7143 | high discount dependency, higher return rate                | possible promotion-sensitive or return-heavy segment         |

These interpretations are descriptive only. **Anomaly does not mean fraud.** A cluster with a high anomaly rate may contain valuable users, low-conversion users, promotion-sensitive users, high-return users, or unusually active users.

## Anomaly Rate

- Isolation Forest anomaly rate: **8.0%**

Anomaly category counts:

| anomaly_category             |   count |
|:-----------------------------|--------:|
| high_value_anomaly           |      38 |
| high_activity_anomaly        |      25 |
| other_behavioral_anomaly     |       9 |
| promotion_abuse_like_anomaly |       7 |
| low_conversion_anomaly       |       1 |

## Normal vs Anomalous User Comparison

| is_anomaly   |   browsing_time |   pages_viewed |   cart_additions |   purchase_count |   total_spending |   discount_usage_count |   discount_ratio |   return_count |   session_count |   conversion_rate |   discount_dependency |   return_rate |
|:-------------|----------------:|---------------:|-----------------:|-----------------:|-----------------:|-----------------------:|-----------------:|---------------:|----------------:|------------------:|----------------------:|--------------:|
| normal       |          73.778 |         54.088 |            6.024 |            1.555 |          208.523 |                  1.427 |            0.206 |          0.012 |           8.251 |             0.037 |                 0.852 |         0.004 |
| anomalous    |         156.63  |        127.525 |           10.1   |            5.625 |         1279.41  |                  3.467 |            0.301 |          0.486 |          19.388 |             0.084 |                 1.017 |         0.204 |

## Missingness Comparison

The MVP compares an imputation-only representation with a missingness-aware representation that adds explicit indicators for missing discount and return signals.

| model             |   anomaly_rate |   mean_anomaly_score |   discount_missing_anomaly_rate |   return_missing_anomaly_rate |
|:------------------|---------------:|---------------------:|--------------------------------:|------------------------------:|
| imputation_only   |           0.08 |              -0.1112 |                          0.0949 |                        0.0645 |
| missingness_aware |           0.08 |              -0.1051 |                          0.146  |                        0.0806 |

Sensitivity summary:

| metric                      |   value |
|:----------------------------|--------:|
| anomaly_overlap_rate        |  0.7582 |
| changed_user_count          | 22      |
| imputation_only_anomalies   | 80      |
| missingness_aware_anomalies | 80      |

See `results/missingness_sensitivity.md` for user-type-level details.

## Pseudo-Anomaly Sanity Check

The pipeline also creates perturbed pseudo-anomalies from normal users and checks whether Isolation Forest gives them stronger anomaly scores. This is only a sanity check for the direction of model behavior, not a real benchmark.

See `results/pseudo_anomaly_check.md` and `figures/pseudo_anomaly_scores.png`.

## Business Interpretation

An anomaly in this project means that a user's behavior differs from the majority pattern. It does not mean fraud. Some anomalous users may be valuable customers with unusually high spending, while others may show low conversion, promotion dependency, high return behavior, or very high activity.

## Research Connection

This MVP connects to clustering and anomaly detection on sparse and partially missing tabular user behavior. The added missingness sensitivity experiment is related to missing/tabular data analysis, and the pseudo-anomaly check is a beginner-friendly way to validate model behavior when real labels are unavailable. The project is also a starting point for graph learning, matrix/tensor representations, and recommender-system-style user-item behavior modeling.

## Limitations and Next Steps

- The dataset is synthetic and designed for demonstration.
- There are no real ground-truth fraud or abuse labels.
- Unsupervised anomaly results require business validation.
- The current version uses aggregated tabular features only.
- Next steps include using real 618 or public e-commerce data, building a user-product-coupon graph, testing graph-based anomaly detection, modeling temporal behavior, and representing user-product-time-behavior as a tensor.
