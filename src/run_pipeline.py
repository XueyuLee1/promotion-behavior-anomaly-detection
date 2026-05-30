"""Run the end-to-end MVP pipeline."""

from __future__ import annotations

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(PROJECT_ROOT / ".matplotlib-cache"))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "4")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from anomaly_detection import anomaly_profile, categorize_anomalies, run_isolation_forest
from clustering import cluster_profile, run_kmeans, run_pca
from data_generator import generate_synthetic_data
from experiments import (
    run_missingness_sensitivity,
    run_pseudo_anomaly_check,
    save_missingness_comparison_figure,
)
from interpretation import add_actionable_interpretation, save_actionable_anomaly_report
from preprocessing import prepare_feature_matrix


DATA_PATH = PROJECT_ROOT / "data" / "synthetic_promotion_user_behavior.csv"
RESULTS_PATH = PROJECT_ROOT / "results" / "user_behavior_with_clusters_and_anomalies.csv"
SUMMARY_PATH = PROJECT_ROOT / "results" / "summary.md"
MISSINGNESS_SENSITIVITY_PATH = PROJECT_ROOT / "results" / "missingness_sensitivity.md"
PSEUDO_ANOMALY_PATH = PROJECT_ROOT / "results" / "pseudo_anomaly_check.md"
ACTIONABLE_REPORT_PATH = PROJECT_ROOT / "results" / "actionable_anomaly_report.md"
FIGURES_DIR = PROJECT_ROOT / "figures"


def save_cluster_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 6))
    sns.scatterplot(data=df, x="pca_1", y="pca_2", hue="cluster", palette="tab10", s=45, alpha=0.80)
    plt.title("PCA Visualization of K-means User Segments")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "pca_clusters.png", dpi=180)
    plt.close()


def save_anomaly_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 6))
    sns.scatterplot(data=df, x="pca_1", y="pca_2", hue="is_anomaly", palette={0: "#4C78A8", 1: "#E45756"}, s=45, alpha=0.80)
    plt.title("PCA Visualization of Isolation Forest Anomalies")
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "anomaly_pca.png", dpi=180)
    plt.close()


def save_feature_distributions(df: pd.DataFrame) -> None:
    features = ["purchase_count", "total_spending", "conversion_rate", "discount_dependency", "return_rate", "session_count"]
    fig, axes = plt.subplots(2, 3, figsize=(14, 8))
    for ax, feature in zip(axes.ravel(), features):
        sns.histplot(data=df, x=feature, hue="is_anomaly", bins=30, kde=False, ax=ax, element="step")
        ax.set_title(feature)
    plt.tight_layout()
    plt.savefig(FIGURES_DIR / "feature_distributions.png", dpi=180)
    plt.close()


def describe_cluster(row: pd.Series, global_means: pd.Series) -> tuple[str, str]:
    traits = []
    if row["total_spending"] > global_means["total_spending"] * 1.8:
        traits.append("high spending")
    if row["purchase_count"] > global_means["purchase_count"] * 1.8:
        traits.append("high purchase count")
    if row["pages_viewed"] > global_means["pages_viewed"] * 1.8:
        traits.append("high browsing volume")
    if row["session_count"] > global_means["session_count"] * 1.8:
        traits.append("high session activity")
    if row["conversion_rate"] < global_means["conversion_rate"] * 0.55:
        traits.append("low conversion")
    if row["discount_dependency"] > global_means["discount_dependency"] * 1.3:
        traits.append("high discount dependency")
    if row["return_rate"] > global_means["return_rate"] * 2.0 and row["return_rate"] > 0:
        traits.append("higher return rate")

    if not traits:
        traits.append("moderate behavior profile")

    trait_text = ", ".join(traits)
    if "high spending" in traits or "high purchase count" in traits:
        interpretation = "possible high-value segment; anomalies may be valuable users"
    elif "low conversion" in traits and "high browsing volume" in traits:
        interpretation = "possible low-conversion segment with heavy browsing"
    elif "high discount dependency" in traits or "higher return rate" in traits:
        interpretation = "possible promotion-sensitive or return-heavy segment"
    elif "high session activity" in traits or "high browsing volume" in traits:
        interpretation = "possible high-activity segment"
    else:
        interpretation = "mostly ordinary behavioral segment"

    return trait_text, interpretation


def build_cluster_anomaly_interpretation(df: pd.DataFrame) -> pd.DataFrame:
    profile_columns = [
        "pages_viewed",
        "session_count",
        "purchase_count",
        "total_spending",
        "conversion_rate",
        "discount_dependency",
        "return_rate",
    ]
    global_means = df[profile_columns].mean()
    rows = []
    for cluster_id, group in df.groupby("cluster"):
        means = group[profile_columns].mean()
        traits, interpretation = describe_cluster(means, global_means)
        rows.append(
            {
                "cluster_id": cluster_id,
                "cluster_size": len(group),
                "anomaly_rate": round(group["is_anomaly"].mean(), 4),
                "key_behavior_characteristics": traits,
                "possible_interpretation": interpretation,
            }
        )
    return pd.DataFrame(rows).sort_values("cluster_id")


def build_summary(
    df: pd.DataFrame,
    user_type_counts: pd.Series,
    cluster_summary: pd.DataFrame,
    cluster_interpretation: pd.DataFrame,
    normal_vs_anomaly: pd.DataFrame,
    missingness_comparison: pd.DataFrame,
    missingness_sensitivity: pd.DataFrame,
    silhouette_score: float,
) -> str:
    anomaly_rate = df["is_anomaly"].mean()
    anomaly_categories = df.loc[df["is_anomaly"] == 1, "anomaly_category"].value_counts()

    return f"""# Promotion Behavior Anomaly Detection MVP Summary

## Dataset Size

- Number of users: {len(df)}
- Number of raw behavior features: 11
- Number of engineered behavior features: 5
- Missingness indicators: discount_missing, return_missing

## Synthetic User Type Distribution

{user_type_counts.to_markdown()}

## Cluster Profile Interpretation

K-means was used as a first segmentation method. The silhouette score is **{silhouette_score:.3f}**, which gives a rough indication of how separated the clusters are in the scaled feature space.

{cluster_summary.to_markdown()}

## Cluster-wise Anomaly Interpretation

This table connects user segmentation with anomaly detection. It describes which clusters contain more anomalous users and gives cautious business interpretations.

{cluster_interpretation.to_markdown(index=False)}

These interpretations are descriptive only. **Anomaly does not mean fraud.** A cluster with a high anomaly rate may contain valuable users, low-conversion users, promotion-sensitive users, high-return users, or unusually active users.

## Anomaly Rate

- Isolation Forest anomaly rate: **{anomaly_rate:.1%}**

Anomaly category counts:

{anomaly_categories.to_markdown()}

## Normal vs Anomalous User Comparison

{normal_vs_anomaly.to_markdown()}

## Missingness Comparison

The MVP compares an imputation-only representation with a missingness-aware representation that adds explicit indicators for missing discount and return signals.

{missingness_comparison.to_markdown()}

Sensitivity summary:

{missingness_sensitivity.to_markdown(index=False)}

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
"""


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)

    raw_data = generate_synthetic_data(n_users=1000, random_state=42, output_path=DATA_PATH)

    features, featured_data, feature_columns, _, _ = prepare_feature_matrix(raw_data, include_missing_indicators=True)
    features_without_missingness, _, _, _, _ = prepare_feature_matrix(raw_data, include_missing_indicators=False)

    _, cluster_labels, silhouette = run_kmeans(features, n_clusters=5, random_state=42)
    _, is_anomaly, anomaly_score = run_isolation_forest(features, contamination=0.08, random_state=42)
    _, is_anomaly_without_missingness, anomaly_score_without_missingness = run_isolation_forest(
        features_without_missingness,
        contamination=0.08,
        random_state=42,
    )

    pca_df = run_pca(features, random_state=42)
    output = pd.concat([featured_data.reset_index(drop=True), pca_df[["pca_1", "pca_2"]]], axis=1)
    output["cluster"] = cluster_labels
    output["is_anomaly"] = is_anomaly
    output["anomaly_score"] = anomaly_score.round(5)
    output["is_anomaly_without_missingness"] = is_anomaly_without_missingness
    output["anomaly_score_without_missingness"] = anomaly_score_without_missingness.round(5)
    output["anomaly_category"] = categorize_anomalies(output)
    output = add_actionable_interpretation(output)

    cluster_summary = cluster_profile(output)
    cluster_interpretation = build_cluster_anomaly_interpretation(output)
    normal_vs_anomaly = anomaly_profile(output)
    user_type_counts = output["user_type"].value_counts().rename_axis("user_type").to_frame("count")

    missingness_comparison = pd.DataFrame(
        {
            "anomaly_rate": [
                output["is_anomaly_without_missingness"].mean(),
                output["is_anomaly"].mean(),
            ],
            "mean_anomaly_score": [
                output["anomaly_score_without_missingness"].mean(),
                output["anomaly_score"].mean(),
            ],
            "discount_missing_anomaly_rate": [
                output.loc[output["discount_missing"] == 1, "is_anomaly_without_missingness"].mean(),
                output.loc[output["discount_missing"] == 1, "is_anomaly"].mean(),
            ],
            "return_missing_anomaly_rate": [
                output.loc[output["return_missing"] == 1, "is_anomaly_without_missingness"].mean(),
                output.loc[output["return_missing"] == 1, "is_anomaly"].mean(),
            ],
        },
        index=["imputation_only", "missingness_aware"],
    ).round(4)
    missingness_comparison.index.name = "model"

    missingness_sensitivity, affected_by_type, missingness_report = run_missingness_sensitivity(output)
    MISSINGNESS_SENSITIVITY_PATH.write_text(missingness_report, encoding="utf-8")
    run_pseudo_anomaly_check(
        raw_data,
        output_path=PSEUDO_ANOMALY_PATH,
        figure_path=FIGURES_DIR / "pseudo_anomaly_scores.png",
    )
    save_actionable_anomaly_report(output, ACTIONABLE_REPORT_PATH)

    output.to_csv(RESULTS_PATH, index=False)
    save_cluster_plot(output)
    save_anomaly_plot(output)
    save_feature_distributions(output)
    save_missingness_comparison_figure(
        missingness_sensitivity,
        affected_by_type,
        FIGURES_DIR / "missingness_comparison.png",
    )

    summary = build_summary(
        output,
        user_type_counts,
        cluster_summary,
        cluster_interpretation,
        normal_vs_anomaly,
        missingness_comparison,
        missingness_sensitivity,
        silhouette,
    )
    SUMMARY_PATH.write_text(summary, encoding="utf-8")

    print("Pipeline finished successfully.")
    print(f"Data saved to: {DATA_PATH}")
    print(f"Results saved to: {RESULTS_PATH}")
    print(f"Summary saved to: {SUMMARY_PATH}")
    print(f"Missingness sensitivity saved to: {MISSINGNESS_SENSITIVITY_PATH}")
    print(f"Pseudo-anomaly check saved to: {PSEUDO_ANOMALY_PATH}")
    print(f"Actionable anomaly report saved to: {ACTIONABLE_REPORT_PATH}")
    print(f"Figures saved to: {FIGURES_DIR}")


if __name__ == "__main__":
    main()
