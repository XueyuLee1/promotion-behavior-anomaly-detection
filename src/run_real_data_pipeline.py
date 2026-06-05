"""Run the real event-level data validation pipeline."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib-cache"))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

from anomaly_detection import run_isolation_forest
from clustering import run_kmeans, run_pca
from real_data_loader import load_real_user_features


DEFAULT_INPUT = PROJECT_ROOT / "data" / "raw" / "synerise"
PROCESSED_PATH = PROJECT_ROOT / "data" / "processed" / "real_user_features.csv"
RESULTS_PATH = PROJECT_ROOT / "results" / "real_user_behavior_with_anomalies.csv"
SUMMARY_PATH = PROJECT_ROOT / "results" / "real_data_summary.md"
FIGURE_PATH = PROJECT_ROOT / "figures" / "real_data_pca_anomalies.png"


REAL_FEATURE_COLUMNS = [
    "event_count",
    "view_count",
    "cart_count",
    "remove_from_cart_count",
    "purchase_count",
    "search_count",
    "unique_items",
    "session_count",
    "active_days",
    "days_since_last_purchase",
    "price_signal_total",
    "average_purchase_price_signal",
    "conversion_rate",
    "cart_to_purchase_rate",
    "purchase_per_active_day",
    "actions_per_active_day",
    "item_diversity_ratio",
    "action_diversity",
    "zero_purchase_indicator",
    "low_activity_indicator",
    "behavior_sparsity",
]


def prepare_real_feature_matrix(data: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    available = [column for column in REAL_FEATURE_COLUMNS if column in data.columns]
    usable = [column for column in available if data[column].notna().any()]
    if not usable:
        raise ValueError("No usable numeric feature columns are available for the real-data pipeline.")

    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    matrix = scaler.fit_transform(imputer.fit_transform(data[usable]))
    return matrix, usable


def interpret_real_anomaly_row(row: pd.Series, thresholds: dict[str, float]) -> tuple[str, str, str]:
    if row["is_anomaly"] != 1:
        return "not_flagged", "User was not flagged as anomalous.", "No anomaly-specific action suggested."

    evidence = []
    anomaly_type = "mixed_behavior_anomaly"
    action = "Prioritize for analyst review and inspect event history in the raw logs."

    if row["purchase_count"] >= thresholds["high_purchase_count"] and row.get("price_signal_total", 0) >= thresholds["high_price_signal_total"]:
        anomaly_type = "high_purchase_signal_anomaly"
        evidence.extend(["high purchase_count", "high price_signal_total"])
        action = "Review high-purchase and high-price-signal behavior for retention and recommendation opportunities."
    elif row["view_count"] >= thresholds["high_view_count"] and row["conversion_rate"] <= thresholds["low_conversion_rate"]:
        anomaly_type = "low_conversion_anomaly"
        evidence.extend(["high view_count", "low conversion_rate"])
        action = "Investigate product pages, price, inventory, recommendation quality, and checkout funnel."
    elif row["cart_count"] >= thresholds["high_cart_count"] and row["cart_to_purchase_rate"] <= thresholds["low_cart_to_purchase_rate"]:
        anomaly_type = "cart_without_purchase_anomaly"
        evidence.extend(["high cart_count", "low cart_to_purchase_rate"])
        action = "Review cart abandonment patterns and promotion or checkout design."
    elif row["remove_from_cart_count"] >= thresholds["high_remove_from_cart_count"] and row["cart_count"] > 0:
        anomaly_type = "remove_from_cart_anomaly"
        evidence.extend(["high remove_from_cart_count"])
        action = "Inspect product availability, pricing changes, and session-level shopping path."
    elif row["event_count"] >= thresholds["very_high_event_count"] or row["view_count"] >= thresholds["very_high_view_count"]:
        anomaly_type = "high_activity_anomaly"
        evidence.extend(["very high event_count or view_count"])
        action = "Check timing, device, IP, and session patterns if available in future data."
    elif row["behavior_sparsity"] >= thresholds["high_behavior_sparsity"]:
        anomaly_type = "sparse_behavior_anomaly"
        evidence.extend(["high behavior_sparsity"])
        action = "Check whether sparse behavior reflects true inactivity, sampling, or logging limitations."

    if not evidence:
        evidence.append("high anomaly score without one dominant rule-based explanation")

    return anomaly_type, "; ".join(evidence), action


def add_real_actionable_interpretation(data: pd.DataFrame) -> pd.DataFrame:
    df = data.copy()
    thresholds = {
        "high_purchase_count": df["purchase_count"].quantile(0.90),
        "high_price_signal_total": df["price_signal_total"].fillna(0).quantile(0.90),
        "high_view_count": df["view_count"].quantile(0.90),
        "very_high_view_count": df["view_count"].quantile(0.97),
        "high_cart_count": df["cart_count"].quantile(0.90),
        "high_remove_from_cart_count": df["remove_from_cart_count"].quantile(0.90),
        "very_high_event_count": df["event_count"].quantile(0.97),
        "low_conversion_rate": df["conversion_rate"].quantile(0.25),
        "low_cart_to_purchase_rate": df["cart_to_purchase_rate"].quantile(0.25),
        "high_behavior_sparsity": df["behavior_sparsity"].quantile(0.90),
    }
    interpreted = df.apply(lambda row: interpret_real_anomaly_row(row, thresholds), axis=1, result_type="expand")
    interpreted.columns = ["anomaly_type", "anomaly_evidence", "suggested_action"]
    return pd.concat([df, interpreted], axis=1)


def save_real_anomaly_plot(data: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 6))
    sns.scatterplot(
        data=data,
        x="pca_1",
        y="pca_2",
        hue="is_anomaly",
        palette={0: "#4C78A8", 1: "#E45756"},
        s=45,
        alpha=0.80,
    )
    plt.title("Real Event Data PCA Visualization of Anomalies")
    plt.tight_layout()
    FIGURE_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(FIGURE_PATH, dpi=180)
    plt.close()


def build_real_summary(
    data: pd.DataFrame,
    metadata: dict[str, object],
    feature_columns: list[str],
    silhouette_score: float,
) -> str:
    anomaly_rate = data["is_anomaly"].mean()
    anomaly_counts = data["anomaly_type"].value_counts().rename_axis("anomaly_type").to_frame("count")
    normal_vs_anomaly = (
        data.groupby("is_anomaly")[feature_columns]
        .mean()
        .rename(index={0: "normal", 1: "anomalous"})
        .round(3)
    )
    cluster_profile = (
        data.groupby("cluster")[feature_columns]
        .mean()
        .round(3)
    )
    unavailable = ", ".join(metadata.get("unavailable_fields", []))

    return f"""# Real Event Data Validation Summary

## Purpose

This report checks whether the synthetic-data anomaly screening workflow can run on real event-level e-commerce behavior logs after aggregating events into user-level features.

This is not a fraud detection benchmark. The dataset does not provide confirmed anomaly labels, so the results should be interpreted as behaviorally unusual users that require further validation.

## Input Data

- Input path: `{metadata.get("input_path")}`
- Sample rows requested: {metadata.get("sample_n_rows")}
- Events after loading/filtering: {metadata.get("event_count")}
- Aggregated users: {metadata.get("user_count")}
- Event types observed: {metadata.get("event_types")}
- Sampling note: {metadata.get("sampling_note")}
- Timestamp available: {metadata.get("has_timestamp")}
- Price available: {metadata.get("has_price")}
- Price note: {metadata.get("price_note")}
- Session id available: {metadata.get("has_session_id")}

Unavailable fields are documented instead of being faked: {unavailable}.

## Feature Columns Used

{pd.Series(feature_columns, name="feature").to_markdown(index=False)}

## Clustering and Anomaly Screening

- K-means clusters: {data["cluster"].nunique()}
- Silhouette score: {silhouette_score:.3f}
- Isolation Forest anomaly rate: {anomaly_rate:.1%}

## Key Takeaways

- The sampled real event logs were successfully converted into user-level behavior features.
- The existing unsupervised workflow ran end-to-end on real event data without using anomaly labels.
- The most common flagged patterns are summarized below as review categories, not confirmed fraud labels.
- Because the Synerise sample is balanced across event files for workflow validation, behavior ratios should not be interpreted as full-site business conversion rates.

## Interpretable Anomaly Types

{anomaly_counts.to_markdown()}

## Normal vs Anomalous User Profile

{normal_vs_anomaly.to_markdown()}

## Cluster Profile

{cluster_profile.to_markdown()}

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
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run real event-level data anomaly screening.")
    parser.add_argument("--input-file", type=Path, default=DEFAULT_INPUT, help="CSV or parquet event log file.")
    parser.add_argument("--dataset-type", choices=["synerise", "retailrocket", "generic"], default="synerise", help="Schema preset for common datasets.")
    parser.add_argument("--sample-n-rows", type=int, default=None, help="Optional number of rows to read.")
    parser.add_argument("--chunksize", type=int, default=None, help="Optional CSV chunksize for large files.")
    parser.add_argument("--start-date", default=None, help="Optional inclusive start date if timestamp exists.")
    parser.add_argument("--end-date", default=None, help="Optional inclusive end date if timestamp exists.")
    parser.add_argument("--user-col", default=None, help="Override user id column.")
    parser.add_argument("--item-col", default=None, help="Override item/product id column.")
    parser.add_argument("--timestamp-col", default=None, help="Override timestamp column.")
    parser.add_argument("--event-col", default=None, help="Override event type column.")
    parser.add_argument("--price-col", default=None, help="Override price column.")
    parser.add_argument("--session-col", default=None, help="Override session id column.")
    parser.add_argument("--loader-smoke-test", action="store_true", help="Only test loading and aggregation; do not save model results.")
    parser.add_argument("--n-clusters", type=int, default=5, help="Number of K-means clusters.")
    parser.add_argument("--contamination", type=float, default=0.08, help="Isolation Forest contamination rate.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        user_features, metadata = load_real_user_features(
            args.input_file,
            dataset_type=args.dataset_type,
            sample_n_rows=args.sample_n_rows,
            chunksize=args.chunksize,
            start_date=args.start_date,
            end_date=args.end_date,
            user_col=args.user_col,
            item_col=args.item_col,
            timestamp_col=args.timestamp_col,
            event_col=args.event_col,
            price_col=args.price_col,
            session_col=args.session_col,
            output_path=None if args.loader_smoke_test else PROCESSED_PATH,
        )
    except (FileNotFoundError, ValueError, ImportError) as exc:
        print("Real-data pipeline could not start.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        print("\nSuggested next steps:", file=sys.stderr)
        print("- Download RecSys Challenge 2025 / Synerise or RetailRocket event logs.", file=sys.stderr)
        print("- Place raw files under data/raw/.", file=sys.stderr)
        print("- For Synerise, place parquet files under data/raw/synerise/ and try: python src/run_real_data_pipeline.py --dataset-type synerise --input-file data/raw/synerise --sample-n-rows 100000", file=sys.stderr)
        print("- For RetailRocket, try: python src/run_real_data_pipeline.py --dataset-type retailrocket --input-file data/raw/events.csv --sample-n-rows 100000", file=sys.stderr)
        print("- To test only the loader format, run: python src/run_real_data_pipeline.py --input-file data/fixtures/mini_event_log.csv --dataset-type synerise --loader-smoke-test", file=sys.stderr)
        return 1

    if args.loader_smoke_test:
        print("Loader smoke test finished successfully.")
        print(f"Aggregated users: {metadata.get('user_count')}")
        print(f"Events loaded: {metadata.get('event_count')}")
        print(f"Event types: {metadata.get('event_types')}")
        print("Preview:")
        print(user_features.head().to_string(index=False))
        print("No model results were saved because --loader-smoke-test was used.")
        return 0

    if len(user_features) < 3:
        print("Real-data pipeline needs at least 3 aggregated users for K-means and PCA.", file=sys.stderr)
        print("Use a larger sample or a wider time window.", file=sys.stderr)
        return 1

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    feature_matrix, feature_columns = prepare_real_feature_matrix(user_features)

    n_clusters = min(args.n_clusters, len(user_features) - 1)
    _, cluster_labels, silhouette = run_kmeans(feature_matrix, n_clusters=n_clusters, random_state=42)
    _, is_anomaly, anomaly_score = run_isolation_forest(feature_matrix, contamination=args.contamination, random_state=42)
    pca = run_pca(feature_matrix, random_state=42)

    output = pd.concat([user_features.reset_index(drop=True), pca[["pca_1", "pca_2"]]], axis=1)
    output["cluster"] = cluster_labels
    output["is_anomaly"] = is_anomaly
    output["anomaly_score"] = anomaly_score.round(5)
    output = add_real_actionable_interpretation(output)

    output.to_csv(RESULTS_PATH, index=False)
    save_real_anomaly_plot(output)
    SUMMARY_PATH.write_text(build_real_summary(output, metadata, feature_columns, silhouette), encoding="utf-8")

    print("Real-data pipeline finished successfully.")
    print(f"Processed features saved to: {PROCESSED_PATH}")
    print(f"Results saved to: {RESULTS_PATH}")
    print(f"Summary saved to: {SUMMARY_PATH}")
    print(f"Figure saved to: {FIGURE_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
