# Promotion Behavior Anomaly Detection under Missing and Sparse User Signals

An interpretable e-commerce user behavior anomaly screening workflow for promotion-period behavior analysis.

This project is **not a fraud detector**. It identifies behaviorally unusual users and turns unsupervised anomaly detection output into a prioritized analyst review list with:

- anomaly label
- anomaly type
- evidence
- suggested analyst action

## Current Status

The project includes two validation paths:

1. **Synthetic controlled MVP:** validates the full workflow under sparse and partially missing user behavior signals.
2. **Real event-log validation:** runs the workflow on a 300k-event sample from the RecSys Challenge 2025 / Synerise dataset.

Raw real datasets and full generated real-user review lists are not uploaded to GitHub. The repository includes code, documentation, figures, and summary reports.

Recommended reading order:

`README.md` -> `results/real_data_summary.md` -> `docs/real_data_integration.md` -> `results/actionable_anomaly_report.md` -> `docs/research_notes.md`

## Problem

Promotion-period e-commerce behavior can be sparse, partially missing, and unlabeled. Many users have few purchases, missing return/coupon signals, or incomplete behavioral histories.

The project asks:

> Can we screen users whose promotion-period behavior deviates from the majority and explain why they should be reviewed?

The goal is to support analyst triage, not to make final risk or fraud decisions.

## Portfolio Highlights

- Built an end-to-end unsupervised ML workflow, not just a model demo.
- Generated synthetic promotion-period user behavior with sparse and missing signals.
- Added a real-data adapter for Synerise event-level parquet logs.
- Aggregated event logs into user-level features from page visit, search, cart, remove-from-cart, and purchase events.
- Applied K-means clustering, PCA visualization, and Isolation Forest anomaly detection.
- Added missingness sensitivity analysis and a pseudo-anomaly sanity check.
- Produced actionable anomaly interpretation with type, evidence, and suggested next action.
- Saved a small real-data anomaly review sample for GitHub inspection while ignoring full generated review lists.
- Added a lightweight unit test for the real event-log loader.
- Kept raw data, processed data, and full real-user review lists out of GitHub.

## Data

### Synthetic Data

The synthetic pipeline generates about 1,000 user-level records with behavior types such as:

- `normal`
- `high_value`
- `low_conversion`
- `promotion_abuse_like`
- `high_activity_anomaly`

It includes sparse and missing behavior signals such as missing `discount_usage_count` and `return_count`.

### Real Event Data

The real-data path supports RecSys Challenge 2025 / Synerise event logs. The expected local files are:

- `product_buy.parquet`
- `add_to_cart.parquet`
- `remove_from_cart.parquet`
- `page_visit.parquet`
- `search_query.parquet`
- `product_properties.parquet`

Place them under:

```text
data/raw/synerise/
```

For Synerise, `sample_n_rows` is split approximately evenly across event files. This is useful for workflow validation, but it should not be interpreted as the natural traffic distribution of the full site.

## Methods

The workflow uses:

- **Feature engineering:** conversion rate, cart-to-purchase rate, behavior sparsity, activity counts, product diversity, and price-signal features.
- **Imputation and scaling:** handles missing numeric values and standardizes features.
- **K-means clustering:** segments users into rough behavior groups.
- **PCA:** visualizes high-dimensional user behavior features in 2D.
- **Isolation Forest:** detects behaviorally unusual users without anomaly labels.
- **Rule-based interpretation:** assigns anomaly type, evidence, and suggested action.

## Outputs

Synthetic pipeline outputs:

- `results/summary.md`
- `results/actionable_anomaly_report.md`
- `results/missingness_sensitivity.md`
- `results/pseudo_anomaly_check.md`
- `figures/pca_clusters.png`
- `figures/anomaly_pca.png`
- `figures/feature_distributions.png`
- `figures/missingness_comparison.png`
- `figures/pseudo_anomaly_scores.png`

Real-data validation outputs:

- `results/real_data_summary.md`
- `results/real_anomaly_review_sample.csv`
- `figures/real_data_pca_anomalies.png`

The full real-user review list is generated locally as `results/real_user_behavior_with_anomalies.csv`, but it is ignored by Git. The small review sample is safe to inspect on GitHub.

## Real-Data Validation Result

The current real-data validation uses a 300k-event Synerise sample.

Summary:

- Events loaded: `300000`
- Aggregated users: `40536`
- Observed event types: `cart`, `purchase`, `remove_from_cart`, `search`, `view`
- Isolation Forest anomaly rate: `8.0%`

Top anomaly review categories:

- `low_conversion_anomaly`
- `high_purchase_signal_anomaly`
- `high_activity_anomaly`
- `remove_from_cart_anomaly`

These are review categories, not confirmed fraud labels.

See `results/real_data_summary.md` for details.
See `results/real_anomaly_review_sample.csv` for a compact, anonymized example of the generated analyst review queue.

## What Happens After Anomaly Detection?

The project outputs a review queue. Each flagged user receives:

- `anomaly_type`
- `anomaly_evidence`
- `suggested_action`

Examples:

- high activity users may require traffic/session inspection
- low conversion users may require page, pricing, or recommendation analysis
- high purchase signal users may be useful for retention or recommendation analysis
- remove-from-cart anomalies may suggest product availability, pricing, or checkout issues

Anomaly means behaviorally unusual. It does **not** mean fraud.

## Project Structure

```text
.
├── README.md
├── requirements.txt
├── data/
│   ├── fixtures/
│   └── synthetic_promotion_user_behavior.csv
├── docs/
│   ├── graph_extension.md
│   ├── real_data_integration.md
│   ├── real_data_roadmap.md
│   └── research_notes.md
├── figures/
├── results/
└── src/
    ├── data_generator.py
    ├── preprocessing.py
    ├── clustering.py
    ├── anomaly_detection.py
    ├── experiments.py
    ├── interpretation.py
    ├── real_data_loader.py
    ├── run_pipeline.py
    └── run_real_data_pipeline.py
```

## How to Run

Create and activate a Python environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the synthetic pipeline:

```bash
python src/run_pipeline.py
```

Run a loader smoke test:

```bash
python src/run_real_data_pipeline.py \
  --input-file data/fixtures/mini_event_log.csv \
  --dataset-type synerise \
  --loader-smoke-test
```

Run the real-data pipeline after placing Synerise files under `data/raw/synerise/`:

```bash
python src/run_real_data_pipeline.py \
  --dataset-type synerise \
  --input-file data/raw/synerise \
  --sample-n-rows 300000
```

To keep multiple experiment outputs, add an optional tag such as `--output-tag 300k`.

Run the loader unit test:

```bash
python -m unittest tests/test_real_data_loader.py
```

## Limitations

- Synthetic data is used for controlled workflow validation.
- The Synerise validation uses a sampled event-log workflow, not the full natural traffic distribution.
- There are no confirmed ground-truth anomaly labels.
- The project does not claim to detect fraud.
- Anomaly categories are rule-based interpretations, not verified business labels.
- Current modeling uses aggregated tabular features rather than sequence, graph, or tensor models.

## Future Work

- Improve real-data sampling strategies and raw event-history inspection.
- Calibrate interpretation thresholds on larger real-data samples.
- Add more real event fields when available.
- Build user-product interaction graph features from event logs.
- Explore graph-based and tensor-based anomaly detection as later extensions.

## Documentation

- `docs/real_data_integration.md`: how real event logs are loaded and mapped to user-level features
- `docs/research_notes.md`: research motivation and methodological notes
- `docs/real_data_roadmap.md`: dataset strategy and real-data extension plan
- `docs/graph_extension.md`: graph and tensor extension blueprint
