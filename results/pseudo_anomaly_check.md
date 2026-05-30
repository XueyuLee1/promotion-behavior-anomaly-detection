# Pseudo-Anomaly / Noise Perturbation Baseline

## Purpose

Real anomaly labels are usually unavailable in unsupervised promotion-behavior analysis. This experiment creates simple pseudo-anomalies by perturbing normal users and checks whether Isolation Forest gives them stronger anomaly scores than unmodified normal users.

Pseudo-anomalies are created by increasing activity, discount dependency, and return behavior. Some pseudo-anomalies keep purchase counts low to imitate high-browsing or high-promotion-dependency behavior.

This is only a sanity check. It is not a real benchmark and does not prove real fraud detection ability.

## Score Summary

| evaluation_group   |   user_count |   mean_anomaly_score |   median_anomaly_score |   anomaly_rate |   mean_pages_viewed |   mean_session_count |   mean_discount_dependency |   mean_return_rate |
|:-------------------|-------------:|---------------------:|-----------------------:|---------------:|--------------------:|---------------------:|---------------------------:|-------------------:|
| normal_reference   |          700 |              -0.0992 |                -0.1076 |         0.0214 |             35.8929 |               6.0943 |                     0.684  |             0.0096 |
| pseudo_anomaly     |          160 |               0.0067 |                 0.0037 |         0.5562 |            111.669  |              17.3938 |                     5.5302 |             1.687  |

## Interpretation

If pseudo-anomalies have higher average anomaly scores or higher anomaly rates than normal reference users, the model is reacting in the expected direction to controlled behavioral perturbations.

The result should still be interpreted carefully because pseudo-anomalies are manually constructed and may be easier to detect than real-world anomalous behavior.
