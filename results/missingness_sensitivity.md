# Missingness Sensitivity Experiment

## Purpose

This experiment compares two feature representations:

- **A. Imputation-only features:** missing values are filled, but the model is not told which values were missing.
- **B. Imputation + missingness indicators:** missing values are filled and the model also receives `discount_missing` and `return_missing`.

The goal is to check whether missing behavior signals influence unsupervised anomaly detection. This is a sensitivity analysis, not a proof of real-world anomaly labels.

## Main Results

| metric                      |   value |
|:----------------------------|--------:|
| anomaly_overlap_rate        |  0.7582 |
| changed_user_count          | 22      |
| imputation_only_anomalies   | 80      |
| missingness_aware_anomalies | 80      |

## Synthetic User Types Most Affected

| user_type             |   user_count |   changed_users |   change_rate |   imputation_only_anomaly_rate |   missingness_aware_anomaly_rate |
|:----------------------|-------------:|----------------:|--------------:|-------------------------------:|---------------------------------:|
| high_activity_anomaly |           50 |              10 |        0.2    |                         0.58   |                           0.5    |
| high_value            |           80 |               5 |        0.0625 |                         0.3625 |                           0.375  |
| promotion_abuse_like  |           70 |               4 |        0.0571 |                         0.2571 |                           0.2571 |
| normal                |          700 |               3 |        0.0043 |                         0.0014 |                           0.0057 |
| low_conversion        |          100 |               0 |        0      |                         0.03   |                           0.03   |

## Example Users Whose Labels Changed

| user_id   | user_type             |   discount_missing |   return_missing |   is_anomaly_without_missingness |   is_anomaly |   anomaly_score_without_missingness |   anomaly_score |
|:----------|:----------------------|-------------------:|-----------------:|---------------------------------:|-------------:|------------------------------------:|----------------:|
| U00754    | high_value            |                  1 |                1 |                                0 |            1 |                            -0.02229 |         0.05988 |
| U00111    | normal                |                  0 |                0 |                                0 |            1 |                            -0.0099  |         0.00374 |
| U00990    | high_activity_anomaly |                  0 |                0 |                                1 |            0 |                             0.02457 |        -0.00011 |
| U00897    | promotion_abuse_like  |                  0 |                0 |                                0 |            1 |                            -0.01011 |         0.0003  |
| U00964    | high_activity_anomaly |                  0 |                0 |                                1 |            0 |                             0.00847 |        -0.00206 |
| U00732    | high_value            |                  0 |                0 |                                1 |            0 |                             0.01748 |        -0.00749 |
| U00991    | high_activity_anomaly |                  0 |                0 |                                1 |            0 |                             0.01321 |        -0.01045 |
| U00927    | promotion_abuse_like  |                  0 |                0 |                                1 |            0 |                             0.02599 |        -2e-05   |
| U00224    | normal                |                  1 |                0 |                                0 |            1 |                            -0.01196 |         0.0075  |
| U00971    | high_activity_anomaly |                  0 |                0 |                                1 |            0 |                             0.00383 |        -0.0065  |
| U00989    | high_activity_anomaly |                  1 |                0 |                                0 |            1 |                            -0.01323 |         0.01576 |
| U00913    | promotion_abuse_like  |                  1 |                1 |                                0 |            1 |                            -0.03783 |         0.02527 |

## Interpretation

If many labels change after adding missingness indicators, it suggests that missing values themselves may carry behavioral information. In promotion-period data, missing discount or return records may reflect data collection gaps, delayed return updates, or user behavior patterns that should not be silently treated as ordinary numeric values.

This does not mean the changed users are fraudulent. It only means their anomaly status is sensitive to how missing behavior signals are represented.
