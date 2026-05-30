"""Isolation Forest anomaly detection and simple anomaly interpretation."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def run_isolation_forest(features, contamination: float = 0.08, random_state: int = 42):
    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=random_state,
    )
    raw_labels = model.fit_predict(features)
    anomaly_score = -model.decision_function(features)
    is_anomaly = (raw_labels == -1).astype(int)
    return model, is_anomaly, anomaly_score


def categorize_anomalies(data: pd.DataFrame) -> pd.Series:
    """Assign a readable anomaly category using transparent rule-based thresholds."""

    df = data.copy()
    categories = np.full(len(df), "normal_or_not_flagged", dtype=object)
    anomaly_mask = df["is_anomaly"] == 1

    high_value = (
        anomaly_mask
        & (df["total_spending"] >= df["total_spending"].quantile(0.90))
        & (df["purchase_count"] >= df["purchase_count"].quantile(0.85))
    )
    low_conversion = (
        anomaly_mask
        & (df["pages_viewed"] >= df["pages_viewed"].quantile(0.85))
        & (df["conversion_rate"] <= df["conversion_rate"].quantile(0.25))
    )
    promotion_abuse_like = (
        anomaly_mask
        & (df["discount_dependency"] >= df["discount_dependency"].quantile(0.85))
        & (df["return_rate"] >= df["return_rate"].quantile(0.75))
    )
    high_activity = (
        anomaly_mask
        & (
            (df["session_count"] >= df["session_count"].quantile(0.95))
            | (df["pages_viewed"] >= df["pages_viewed"].quantile(0.95))
        )
    )

    categories[anomaly_mask] = "other_behavioral_anomaly"
    categories[high_value] = "high_value_anomaly"
    categories[low_conversion] = "low_conversion_anomaly"
    categories[promotion_abuse_like] = "promotion_abuse_like_anomaly"
    categories[high_activity] = "high_activity_anomaly"
    return pd.Series(categories, index=df.index)


def anomaly_profile(data: pd.DataFrame) -> pd.DataFrame:
    profile_columns = [
        "browsing_time",
        "pages_viewed",
        "cart_additions",
        "purchase_count",
        "total_spending",
        "discount_usage_count",
        "discount_ratio",
        "return_count",
        "session_count",
        "conversion_rate",
        "discount_dependency",
        "return_rate",
    ]
    return data.groupby("is_anomaly")[profile_columns].mean().rename(index={0: "normal", 1: "anomalous"}).round(3)
