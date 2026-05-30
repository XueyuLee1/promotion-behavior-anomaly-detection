"""Preprocessing and feature engineering for user behavior anomaly detection."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler


RAW_NUMERIC_FEATURES = [
    "browsing_time",
    "pages_viewed",
    "cart_additions",
    "purchase_count",
    "total_spending",
    "average_order_value",
    "discount_usage_count",
    "discount_ratio",
    "return_count",
    "days_since_last_purchase",
    "session_count",
]

ENGINEERED_FEATURES = [
    "conversion_rate",
    "cart_to_purchase_rate",
    "spending_per_session",
    "discount_dependency",
    "return_rate",
]

MISSINGNESS_FEATURES = ["discount_missing", "return_missing"]


def safe_divide(numerator: pd.Series, denominator: pd.Series | np.ndarray) -> pd.Series:
    denominator = pd.Series(denominator, index=numerator.index).replace(0, np.nan)
    return (numerator / denominator).replace([np.inf, -np.inf], np.nan).fillna(0)


def add_behavior_features(data: pd.DataFrame) -> pd.DataFrame:
    """Add missingness indicators and interpretable behavioral ratios."""

    df = data.copy()
    df["discount_missing"] = df["discount_usage_count"].isna().astype(int)
    df["return_missing"] = df["return_count"].isna().astype(int)

    discount_for_ratios = df["discount_usage_count"].fillna(0)
    return_for_ratios = df["return_count"].fillna(0)
    purchase_floor = np.maximum(df["purchase_count"], 1)

    df["conversion_rate"] = safe_divide(df["purchase_count"], df["pages_viewed"])
    df["cart_to_purchase_rate"] = safe_divide(df["purchase_count"], df["cart_additions"])
    df["spending_per_session"] = safe_divide(df["total_spending"], df["session_count"])
    df["discount_dependency"] = safe_divide(discount_for_ratios, purchase_floor)
    df["return_rate"] = safe_divide(return_for_ratios, purchase_floor)
    return df


def prepare_feature_matrix(
    data: pd.DataFrame,
    include_missing_indicators: bool = True,
) -> tuple[np.ndarray, pd.DataFrame, list[str], SimpleImputer, StandardScaler]:
    """Create an imputed and scaled feature matrix for unsupervised learning."""

    featured = add_behavior_features(data)
    feature_columns = RAW_NUMERIC_FEATURES + ENGINEERED_FEATURES
    if include_missing_indicators:
        feature_columns += MISSINGNESS_FEATURES

    imputer = SimpleImputer(strategy="median")
    scaler = StandardScaler()
    imputed = imputer.fit_transform(featured[feature_columns])
    scaled = scaler.fit_transform(imputed)

    return scaled, featured, feature_columns, imputer, scaler
