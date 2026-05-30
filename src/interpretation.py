"""Actionable interpretation layer for detected anomalies."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ANOMALY_ACTIONS = {
    "high_value_anomaly": {
        "meaning": "Valuable customer whose behavior is unusual because spending and purchase activity are very high.",
        "action": "Review for retention, VIP analysis, and personalized recommendation opportunities.",
    },
    "low_conversion_anomaly": {
        "meaning": "User shows interest through browsing or cart activity but does not convert strongly.",
        "action": "Investigate price, inventory, page experience, recommendation quality, and coupon design.",
    },
    "promotion_abuse_like_anomaly": {
        "meaning": "Promotion-abuse-like behavior may be present, but this is not confirmed fraud.",
        "action": "Send to manual review or a downstream risk-scoring process; do not directly label as fraud.",
    },
    "high_activity_anomaly": {
        "meaning": "User shows very high activity that could reflect a power user, automation, or abnormal traffic.",
        "action": "Check device, IP, session, and timing patterns when real event-level data is available.",
    },
    "data_quality_anomaly": {
        "meaning": "The anomaly is strongly related to missing behavior signals.",
        "action": "Check data collection, logging coverage, delayed records, and the missingness mechanism.",
    },
    "mixed_anomaly": {
        "meaning": "Multiple unusual behavior patterns appear at the same time.",
        "action": "Prioritize for analyst review and inspect user-level behavior history in more detail.",
    },
    "not_flagged": {
        "meaning": "User was not flagged by the anomaly detector.",
        "action": "No anomaly-specific action suggested by this prototype.",
    },
}


def _evidence_text(evidence: list[str]) -> str:
    return "; ".join(evidence) if evidence else "No strong rule-based evidence."


def interpret_anomaly_row(row: pd.Series, thresholds: dict[str, float]) -> tuple[str, str, str]:
    """Assign an interpretable anomaly type, evidence, and suggested action."""

    if row["is_anomaly"] != 1:
        item = ANOMALY_ACTIONS["not_flagged"]
        return "not_flagged", "User was not flagged as anomalous.", item["action"]

    evidence_by_type = {
        "high_value_anomaly": [],
        "low_conversion_anomaly": [],
        "promotion_abuse_like_anomaly": [],
        "high_activity_anomaly": [],
        "data_quality_anomaly": [],
    }

    if row["total_spending"] >= thresholds["high_total_spending"]:
        evidence_by_type["high_value_anomaly"].append("high total_spending")
    if row["purchase_count"] >= thresholds["high_purchase_count"]:
        evidence_by_type["high_value_anomaly"].append("high purchase_count")
    if row["return_rate"] <= thresholds["low_return_rate"]:
        evidence_by_type["high_value_anomaly"].append("low return_rate")

    if row["pages_viewed"] >= thresholds["high_pages_viewed"]:
        evidence_by_type["low_conversion_anomaly"].append("high pages_viewed")
    if row["cart_additions"] >= thresholds["high_cart_additions"]:
        evidence_by_type["low_conversion_anomaly"].append("high cart_additions")
    if row["purchase_count"] <= thresholds["low_purchase_count"]:
        evidence_by_type["low_conversion_anomaly"].append("low purchase_count")
    if row["conversion_rate"] <= thresholds["low_conversion_rate"]:
        evidence_by_type["low_conversion_anomaly"].append("low conversion_rate")

    if row["discount_dependency"] >= thresholds["high_discount_dependency"]:
        evidence_by_type["promotion_abuse_like_anomaly"].append("high discount_dependency")
    if row["discount_ratio"] >= thresholds["high_discount_ratio"]:
        evidence_by_type["promotion_abuse_like_anomaly"].append("high discount_ratio")
    if row["return_rate"] >= thresholds["high_return_rate"]:
        evidence_by_type["promotion_abuse_like_anomaly"].append("high return_rate")

    if row["session_count"] >= thresholds["very_high_session_count"]:
        evidence_by_type["high_activity_anomaly"].append("very high session_count")
    if row["pages_viewed"] >= thresholds["very_high_pages_viewed"]:
        evidence_by_type["high_activity_anomaly"].append("very high pages_viewed")

    if row["discount_missing"] == 1:
        evidence_by_type["data_quality_anomaly"].append("discount_usage_count is missing")
    if row["return_missing"] == 1:
        evidence_by_type["data_quality_anomaly"].append("return_count is missing")

    matched = {key: value for key, value in evidence_by_type.items() if len(value) >= 2}
    if not matched and evidence_by_type["data_quality_anomaly"]:
        matched = {"data_quality_anomaly": evidence_by_type["data_quality_anomaly"]}

    if len(matched) > 1:
        anomaly_type = "mixed_anomaly"
        evidence = []
        for key, values in matched.items():
            evidence.append(f"{key}: {', '.join(values)}")
    elif len(matched) == 1:
        anomaly_type = next(iter(matched))
        evidence = matched[anomaly_type]
    else:
        anomaly_type = "mixed_anomaly"
        evidence = ["anomaly score is high, but no single rule explains the pattern strongly"]

    action = ANOMALY_ACTIONS[anomaly_type]["action"]
    return anomaly_type, _evidence_text(evidence), action


def add_actionable_interpretation(data: pd.DataFrame) -> pd.DataFrame:
    """Add anomaly_type, anomaly_evidence, and suggested_action columns."""

    df = data.copy()
    thresholds = {
        "high_total_spending": df["total_spending"].quantile(0.90),
        "high_purchase_count": df["purchase_count"].quantile(0.85),
        "low_return_rate": df["return_rate"].quantile(0.60),
        "high_pages_viewed": df["pages_viewed"].quantile(0.85),
        "very_high_pages_viewed": df["pages_viewed"].quantile(0.95),
        "high_cart_additions": df["cart_additions"].quantile(0.85),
        "low_purchase_count": df["purchase_count"].quantile(0.35),
        "low_conversion_rate": df["conversion_rate"].quantile(0.25),
        "high_discount_dependency": df["discount_dependency"].quantile(0.85),
        "high_discount_ratio": df["discount_ratio"].quantile(0.85),
        "high_return_rate": df["return_rate"].quantile(0.85),
        "very_high_session_count": df["session_count"].quantile(0.95),
    }

    interpreted = df.apply(lambda row: interpret_anomaly_row(row, thresholds), axis=1, result_type="expand")
    interpreted.columns = ["anomaly_type", "anomaly_evidence", "suggested_action"]
    return pd.concat([df, interpreted], axis=1)


def build_actionable_anomaly_report(data: pd.DataFrame) -> str:
    """Create a concise analyst-facing report for anomaly follow-up."""

    anomalies = data[data["is_anomaly"] == 1].copy()
    anomaly_count = len(anomalies)
    anomaly_rate = anomaly_count / len(data) if len(data) else 0
    type_counts = anomalies["anomaly_type"].value_counts().rename_axis("anomaly_type").to_frame("count")

    profile_columns = [
        "pages_viewed",
        "cart_additions",
        "purchase_count",
        "total_spending",
        "discount_ratio",
        "discount_dependency",
        "return_rate",
        "session_count",
        "discount_missing",
        "return_missing",
    ]
    type_profiles = anomalies.groupby("anomaly_type")[profile_columns].mean().round(3)

    action_table = (
        pd.DataFrame.from_dict(ANOMALY_ACTIONS, orient="index")
        .drop(index="not_flagged")
        .rename_axis("anomaly_type")
        .reset_index()
    )

    examples = anomalies[
        [
            "user_id",
            "anomaly_type",
            "anomaly_score",
            "anomaly_evidence",
            "suggested_action",
        ]
    ].sort_values("anomaly_score", ascending=False).head(12)

    return f"""# Actionable Anomaly Report

## What Happens After Anomaly Detection?

The anomaly detector produces a review list, not a final fraud decision. This report translates detected anomalies into interpretable behavior types, supporting evidence, and suggested follow-up actions.

The purpose is to help analysts decide what to inspect next during an e-commerce promotion period.

## Detected Anomalies

- Total users: {len(data)}
- Detected anomalies: {anomaly_count}
- Anomaly rate: {anomaly_rate:.1%}

## Interpretable Anomaly Types

{type_counts.to_markdown()}

## Typical Feature Patterns by Type

{type_profiles.to_markdown()}

## Suggested Analyst Follow-up Actions

{action_table.to_markdown(index=False)}

## Example Review List

{examples.to_markdown(index=False)}

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
"""


def save_actionable_anomaly_report(data: pd.DataFrame, output_path: str | Path) -> None:
    Path(output_path).write_text(build_actionable_anomaly_report(data), encoding="utf-8")
