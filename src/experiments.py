"""Small research-oriented experiments for the MVP pipeline."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from anomaly_detection import run_isolation_forest
from preprocessing import prepare_feature_matrix


def run_missingness_sensitivity(output: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Compare anomaly labels with and without missingness indicators."""

    aware = output["is_anomaly"] == 1
    imputation_only = output["is_anomaly_without_missingness"] == 1
    overlap = (aware & imputation_only).sum()
    union = (aware | imputation_only).sum()
    overlap_rate = overlap / union if union else 0
    changed = output[aware != imputation_only].copy()

    affected_by_type = (
        output.assign(label_changed=(aware != imputation_only).astype(int))
        .groupby("user_type")
        .agg(
            user_count=("user_id", "count"),
            changed_users=("label_changed", "sum"),
            change_rate=("label_changed", "mean"),
            imputation_only_anomaly_rate=("is_anomaly_without_missingness", "mean"),
            missingness_aware_anomaly_rate=("is_anomaly", "mean"),
        )
        .sort_values("change_rate", ascending=False)
        .round(4)
    )

    comparison = pd.DataFrame(
        {
            "metric": [
                "anomaly_overlap_rate",
                "changed_user_count",
                "imputation_only_anomalies",
                "missingness_aware_anomalies",
            ],
            "value": [
                round(overlap_rate, 4),
                int(len(changed)),
                int(imputation_only.sum()),
                int(aware.sum()),
            ],
        }
    )

    changed_preview = changed[
        [
            "user_id",
            "user_type",
            "discount_missing",
            "return_missing",
            "is_anomaly_without_missingness",
            "is_anomaly",
            "anomaly_score_without_missingness",
            "anomaly_score",
        ]
    ].head(12)

    report = f"""# Missingness Sensitivity Experiment

## Purpose

This experiment compares two feature representations:

- **A. Imputation-only features:** missing values are filled, but the model is not told which values were missing.
- **B. Imputation + missingness indicators:** missing values are filled and the model also receives `discount_missing` and `return_missing`.

The goal is to check whether missing behavior signals influence unsupervised anomaly detection. This is a sensitivity analysis, not a proof of real-world anomaly labels.

## Main Results

{comparison.to_markdown(index=False)}

## Synthetic User Types Most Affected

{affected_by_type.to_markdown()}

## Example Users Whose Labels Changed

{changed_preview.to_markdown(index=False)}

## Interpretation

If many labels change after adding missingness indicators, it suggests that missing values themselves may carry behavioral information. In promotion-period data, missing discount or return records may reflect data collection gaps, delayed return updates, or user behavior patterns that should not be silently treated as ordinary numeric values.

This does not mean the changed users are fraudulent. It only means their anomaly status is sensitive to how missing behavior signals are represented.
"""
    return comparison, affected_by_type, report


def save_missingness_comparison_figure(
    comparison: pd.DataFrame,
    affected_by_type: pd.DataFrame,
    output_path: str | Path,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    plot_data = comparison.copy()
    sns.barplot(data=plot_data, x="metric", y="value", ax=axes[0], color="#4C78A8")
    axes[0].set_title("Missingness Sensitivity Metrics")
    axes[0].tick_params(axis="x", rotation=30)
    axes[0].set_xlabel("")

    affected_plot = affected_by_type.reset_index()
    sns.barplot(data=affected_plot, x="user_type", y="change_rate", ax=axes[1], color="#F58518")
    axes[1].set_title("Anomaly Label Change Rate by User Type")
    axes[1].tick_params(axis="x", rotation=30)
    axes[1].set_xlabel("")
    axes[1].set_ylabel("change_rate")

    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def create_pseudo_anomalies(data: pd.DataFrame, n_pseudo: int = 160, random_state: int = 42) -> pd.DataFrame:
    """Create perturbed normal users for a simple sanity check."""

    rng = np.random.default_rng(random_state)
    normal_pool = data[data["user_type"] == "normal"].dropna(subset=["discount_usage_count", "return_count"])
    sampled = normal_pool.sample(n=min(n_pseudo, len(normal_pool)), random_state=random_state).copy()
    sampled["user_id"] = [f"PSEUDO_{idx:04d}" for idx in range(len(sampled))]
    sampled["user_type"] = "pseudo_anomaly"

    sampled["pages_viewed"] = (sampled["pages_viewed"] * rng.uniform(2.2, 4.0, len(sampled))).round().astype(int)
    sampled["session_count"] = (sampled["session_count"] * rng.uniform(2.0, 3.5, len(sampled))).round().astype(int) + 1
    sampled["browsing_time"] = (sampled["browsing_time"] * rng.uniform(1.7, 3.0, len(sampled))).round(2)
    sampled["discount_usage_count"] = sampled["discount_usage_count"].fillna(0) + rng.integers(3, 8, len(sampled))
    sampled["discount_ratio"] = np.clip(sampled["discount_ratio"] + rng.uniform(0.25, 0.55, len(sampled)), 0, 0.95).round(3)
    sampled["return_count"] = sampled["return_count"].fillna(0) + rng.integers(1, 4, len(sampled))

    low_purchase_mask = rng.random(len(sampled)) < 0.55
    sampled.loc[low_purchase_mask, "purchase_count"] = rng.integers(0, 2, low_purchase_mask.sum())
    sampled["purchase_count"] = np.minimum(sampled["purchase_count"], np.maximum(sampled["cart_additions"], 1))
    sampled["average_order_value"] = sampled["average_order_value"].clip(lower=1)
    sampled["total_spending"] = (sampled["purchase_count"] * sampled["average_order_value"]).round(2)
    return sampled


def run_pseudo_anomaly_check(raw_data: pd.DataFrame, output_path: str | Path, figure_path: str | Path) -> str:
    """Run a pseudo-anomaly sanity check and save a report plus score figure."""

    normal_reference = raw_data[raw_data["user_type"] == "normal"].copy()
    pseudo = create_pseudo_anomalies(raw_data)
    normal_reference["evaluation_group"] = "normal_reference"
    pseudo["evaluation_group"] = "pseudo_anomaly"
    combined = pd.concat([normal_reference, pseudo], ignore_index=True)

    features, featured, _, _, _ = prepare_feature_matrix(combined, include_missing_indicators=True)
    _, labels, scores = run_isolation_forest(features, contamination=0.12, random_state=99)
    featured["evaluation_group"] = combined["evaluation_group"].values
    featured["is_anomaly"] = labels
    featured["anomaly_score"] = scores

    score_summary = (
        featured.groupby("evaluation_group")
        .agg(
            user_count=("user_id", "count"),
            mean_anomaly_score=("anomaly_score", "mean"),
            median_anomaly_score=("anomaly_score", "median"),
            anomaly_rate=("is_anomaly", "mean"),
            mean_pages_viewed=("pages_viewed", "mean"),
            mean_session_count=("session_count", "mean"),
            mean_discount_dependency=("discount_dependency", "mean"),
            mean_return_rate=("return_rate", "mean"),
        )
        .round(4)
    )

    plt.figure(figsize=(8, 5))
    sns.boxplot(data=featured, x="evaluation_group", y="anomaly_score", hue="evaluation_group", palette=["#4C78A8", "#E45756"], legend=False)
    sns.stripplot(data=featured.sample(min(300, len(featured)), random_state=2), x="evaluation_group", y="anomaly_score", color="black", alpha=0.25, size=2)
    plt.title("Isolation Forest Scores for Normal vs Pseudo-Anomaly Users")
    plt.xlabel("")
    plt.tight_layout()
    plt.savefig(figure_path, dpi=180)
    plt.close()

    report = f"""# Pseudo-Anomaly / Noise Perturbation Baseline

## Purpose

Real anomaly labels are usually unavailable in unsupervised promotion-behavior analysis. This experiment creates simple pseudo-anomalies by perturbing normal users and checks whether Isolation Forest gives them stronger anomaly scores than unmodified normal users.

Pseudo-anomalies are created by increasing activity, discount dependency, and return behavior. Some pseudo-anomalies keep purchase counts low to imitate high-browsing or high-promotion-dependency behavior.

This is only a sanity check. It is not a real benchmark and does not prove real fraud detection ability.

## Score Summary

{score_summary.to_markdown()}

## Interpretation

If pseudo-anomalies have higher average anomaly scores or higher anomaly rates than normal reference users, the model is reacting in the expected direction to controlled behavioral perturbations.

The result should still be interpreted carefully because pseudo-anomalies are manually constructed and may be easier to detect than real-world anomalous behavior.
"""
    Path(output_path).write_text(report, encoding="utf-8")
    return report
