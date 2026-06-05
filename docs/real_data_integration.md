# Real-Data Integration

## Purpose

The synthetic MVP validates the project structure in a controlled setting. Real-data integration is added to test whether the same anomaly screening workflow can transfer to public event-level e-commerce behavior logs.

This step is not meant to prove high fraud detection accuracy. Real public datasets usually do not include confirmed anomaly or fraud labels. Instead, this step checks whether:

- raw event logs can be converted into user-level features
- the existing clustering and anomaly screening workflow can still run
- anomaly profiles are interpretable on real behavior data
- synthetic assumptions fail or need adjustment on real data
- event logs can later support user-product graph or tensor representations

## Synthetic MVP vs Real-Data Validation

The synthetic MVP uses generated user-level rows so that the full pipeline is easy to run and inspect. Real-data validation starts from raw event-level logs, where each row is one behavior event such as a page visit, add-to-cart action, remove-from-cart action, search query, or purchase.

The real-data pipeline is a transfer test. It asks whether the existing workflow still works when the data is noisy, sparse, long-tailed, partially missing, and unlabeled.

## Primary and Fallback Datasets

The recommended primary dataset is the RecSys Challenge 2025 / Synerise dataset because it contains real online retailer website interactions. Relevant event types include product buy, add to cart, remove from cart, page visit, and search query.

The fallback dataset is RetailRocket because it has a simpler event log with view, add-to-cart, and transaction events.

Raw datasets should be downloaded manually and placed under `data/raw/`. Raw data should not be uploaded to GitHub.

For Synerise, the expected local directory is `data/raw/synerise/` with the official parquet files:

- `product_buy.parquet`
- `add_to_cart.parquet`
- `remove_from_cart.parquet`
- `page_visit.parquet`
- `search_query.parquet`
- `product_properties.parquet`

## Why Aggregate Event-Level Data to User-Level Features?

The current workflow is a user-level tabular anomaly screening pipeline. To reuse it, real event logs must first be summarized into one row per user. This keeps the real-data validation beginner-friendly while still using real behavior logs.

Later, the same event logs can be used directly for user-product graph or tensor representations.

## Event-Level to User-Level Mapping

The real-data loader normalizes event logs into this common schema when the fields are available:

| Common field | Examples from datasets |
|:-------------|:-----------------------|
| `user_id` | `client_id`, `visitorid`, `customer_id` |
| `item_id` | `sku`, `product_id`, `itemid` |
| `timestamp` | `timestamp`, `event_time` |
| `event_type` | `event`, `event_type`, `action` |
| `price` | `price`, `unit_price` |
| `session_id` | `user_session`, `session_id` |

For the official Synerise schema, event type is inferred from the source parquet file name. Product events use `sku` as the item identifier. Page visits use `url` as the visited page identifier. Search queries do not directly map to a product item. The Synerise `price` field is treated as a dataset-provided price signal from product properties, not verified real revenue.

After normalization, event logs are aggregated into user-level features such as:

- `event_count`
- `view_count`
- `cart_count`
- `remove_from_cart_count`
- `purchase_count`
- `search_count`
- `unique_items`
- `session_count`, if available
- `active_days`, if timestamp is available
- `price_signal_total`, if price is available
- `average_purchase_price_signal`, if price is available
- `conversion_rate`
- `cart_to_purchase_rate`
- `purchase_per_active_day`
- `actions_per_active_day`
- `item_diversity_ratio`
- `action_diversity`
- `behavior_sparsity`

## Unavailable Fields

The real-data pipeline does not fake unavailable fields.

For many public event logs, the following fields may be unavailable:

- coupon usage
- real discount ratio
- return count
- confirmed fraud or abuse labels
- device or IP information

If these fields are missing, they are documented as dataset limitations rather than filled with artificial values.

## How to Run

Run a loader-only format smoke test with the small fixture. This fixture is not a real experiment dataset and should not be used as evidence of real-data performance:

```bash
python src/run_real_data_pipeline.py \
  --input-file data/fixtures/mini_event_log.csv \
  --dataset-type synerise \
  --loader-smoke-test
```

Run on a real CSV or parquet event log after downloading it into `data/raw/`:

```bash
python src/run_real_data_pipeline.py \
  --dataset-type synerise \
  --input-file data/raw/synerise \
  --sample-n-rows 100000
```

For the Synerise multi-file loader, `sample_n_rows` is split approximately evenly across the event files. This is useful for checking whether the workflow runs on real event logs, but it should not be interpreted as the natural traffic distribution of the full dataset.

Run on RetailRocket fallback data:

```bash
python src/run_real_data_pipeline.py \
  --dataset-type retailrocket \
  --input-file data/raw/events.csv \
  --sample-n-rows 100000 \
  --chunksize 50000
```

If timestamps are available, a time window can be selected:

```bash
python src/run_real_data_pipeline.py \
  --dataset-type synerise \
  --input-file data/raw/synerise \
  --sample-n-rows 100000 \
  --start-date 2024-01-01 \
  --end-date 2024-01-31
```

## Outputs

The real-data pipeline saves:

- `data/processed/real_user_features.csv`
- `results/real_user_behavior_with_anomalies.csv`
- `results/real_data_summary.md`
- `figures/real_data_pca_anomalies.png`

The output is a review list, not a fraud decision. Each anomaly should be interpreted as behaviorally unusual and requiring further validation.

## How to Interpret Outputs

The real-data output should be read as a workflow validation report:

- Did event logs successfully convert into user-level features?
- Which features were available or unavailable?
- Which users were behaviorally unusual in the sampled logs?
- Are anomaly profiles explainable using view, cart, purchase, search, activity, or sparsity patterns?
- Which synthetic assumptions fail on real data?

The output should not be reported as fraud detection accuracy.

## Limitations

- Public event logs may not include coupon usage, return behavior, device information, IP addresses, or confirmed anomaly labels.
- Sampling can change the anomaly profile.
- For Synerise, balanced sampling across event files can change behavior ratios such as conversion rate and cart-to-purchase rate.
- Sparse users and long-tail products may dominate the data.
- Rule-based interpretation thresholds should be recalibrated for each real dataset.
- Without labels, results require domain validation rather than accuracy claims.

## Connection to Graph Extension

Event-level logs naturally support a future user-product graph:

- nodes: users and products
- edges: view, cart, remove-from-cart, purchase, search-related interactions
- edge attributes: timestamp, price, session id, event type

This prepares the project to move from user-level tabular anomaly screening toward graph-based and tensor-based anomaly detection.
