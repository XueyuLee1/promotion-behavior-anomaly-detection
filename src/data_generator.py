"""Synthetic promotion-period user behavior data generator."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


USER_TYPE_CONFIG = {
    "normal": 0.70,
    "high_value": 0.08,
    "low_conversion": 0.10,
    "promotion_abuse_like": 0.07,
    "high_activity_anomaly": 0.05,
}


def _positive_normal(rng: np.random.Generator, mean: float, std: float, size: int) -> np.ndarray:
    return np.maximum(rng.normal(mean, std, size), 0)


def _generate_type_block(
    rng: np.random.Generator,
    user_type: str,
    size: int,
    start_id: int,
) -> pd.DataFrame:
    if user_type == "normal":
        pages_viewed = rng.poisson(35, size) + 1
        browsing_time = _positive_normal(rng, 55, 18, size)
        cart_additions = rng.poisson(4, size)
        purchase_count = rng.poisson(2, size)
        average_order_value = _positive_normal(rng, 120, 35, size)
        discount_usage_count = rng.poisson(1, size)
        discount_ratio = np.clip(rng.normal(0.18, 0.08, size), 0, 0.65)
        return_count = rng.poisson(0.15, size)
        session_count = rng.poisson(5, size) + 1
        days_since_last_purchase = rng.integers(1, 60, size)
    elif user_type == "high_value":
        pages_viewed = rng.poisson(60, size) + 1
        browsing_time = _positive_normal(rng, 95, 25, size)
        cart_additions = rng.poisson(10, size)
        purchase_count = rng.poisson(8, size) + 2
        average_order_value = _positive_normal(rng, 260, 70, size)
        discount_usage_count = rng.poisson(2, size)
        discount_ratio = np.clip(rng.normal(0.14, 0.06, size), 0, 0.50)
        return_count = rng.poisson(0.25, size)
        session_count = rng.poisson(9, size) + 1
        days_since_last_purchase = rng.integers(1, 25, size)
    elif user_type == "low_conversion":
        pages_viewed = rng.poisson(120, size) + 1
        browsing_time = _positive_normal(rng, 160, 45, size)
        cart_additions = rng.poisson(16, size)
        purchase_count = rng.binomial(2, 0.25, size)
        average_order_value = _positive_normal(rng, 95, 30, size)
        discount_usage_count = rng.poisson(1, size)
        discount_ratio = np.clip(rng.normal(0.22, 0.10, size), 0, 0.75)
        return_count = rng.poisson(0.10, size)
        session_count = rng.poisson(13, size) + 1
        days_since_last_purchase = rng.integers(20, 120, size)
    elif user_type == "promotion_abuse_like":
        pages_viewed = rng.poisson(70, size) + 1
        browsing_time = _positive_normal(rng, 85, 28, size)
        cart_additions = rng.poisson(8, size)
        purchase_count = rng.poisson(4, size) + 1
        average_order_value = _positive_normal(rng, 105, 40, size)
        discount_usage_count = rng.poisson(6, size) + 2
        discount_ratio = np.clip(rng.normal(0.58, 0.15, size), 0.15, 0.95)
        return_count = rng.poisson(2, size)
        session_count = rng.poisson(8, size) + 1
        days_since_last_purchase = rng.integers(1, 45, size)
    elif user_type == "high_activity_anomaly":
        pages_viewed = rng.poisson(240, size) + 20
        browsing_time = _positive_normal(rng, 260, 65, size)
        cart_additions = rng.poisson(11, size)
        purchase_count = rng.poisson(2, size)
        average_order_value = _positive_normal(rng, 110, 35, size)
        discount_usage_count = rng.poisson(2, size)
        discount_ratio = np.clip(rng.normal(0.25, 0.12, size), 0, 0.80)
        return_count = rng.poisson(0.25, size)
        session_count = rng.poisson(35, size) + 5
        days_since_last_purchase = rng.integers(1, 90, size)
    else:
        raise ValueError(f"Unknown user type: {user_type}")

    purchase_count = np.minimum(purchase_count, np.maximum(cart_additions, 1))
    total_spending = purchase_count * average_order_value * rng.normal(1.0, 0.08, size)
    total_spending = np.maximum(total_spending, 0)

    return pd.DataFrame(
        {
            "user_id": [f"U{idx:05d}" for idx in range(start_id, start_id + size)],
            "browsing_time": browsing_time.round(2),
            "pages_viewed": pages_viewed.astype(int),
            "cart_additions": cart_additions.astype(int),
            "purchase_count": purchase_count.astype(int),
            "total_spending": total_spending.round(2),
            "average_order_value": average_order_value.round(2),
            "discount_usage_count": discount_usage_count.astype(float),
            "discount_ratio": discount_ratio.round(3),
            "return_count": return_count.astype(float),
            "days_since_last_purchase": days_since_last_purchase.astype(int),
            "session_count": session_count.astype(int),
            "user_type": user_type,
        }
    )


def generate_synthetic_data(
    n_users: int = 1000,
    random_state: int = 42,
    output_path: str | Path | None = None,
) -> pd.DataFrame:
    """Generate a synthetic unlabeled-style dataset with hidden demo user types."""

    rng = np.random.default_rng(random_state)
    counts = {name: int(n_users * share) for name, share in USER_TYPE_CONFIG.items()}
    counts["normal"] += n_users - sum(counts.values())

    frames = []
    start_id = 1
    for user_type, count in counts.items():
        frame = _generate_type_block(rng, user_type, count, start_id)
        frames.append(frame)
        start_id += count

    data = pd.concat(frames, ignore_index=True)
    data = data.sample(frac=1, random_state=random_state).reset_index(drop=True)

    low_purchase_mask = rng.random(len(data)) < 0.18
    data.loc[low_purchase_mask, "purchase_count"] = 0
    data.loc[low_purchase_mask, "total_spending"] = 0
    data.loc[low_purchase_mask, "return_count"] = 0

    zero_return_mask = rng.random(len(data)) < 0.70
    data.loc[zero_return_mask, "return_count"] = 0

    discount_missing_mask = rng.random(len(data)) < 0.16
    return_missing_mask = rng.random(len(data)) < 0.12
    data.loc[discount_missing_mask, "discount_usage_count"] = np.nan
    data.loc[return_missing_mask, "return_count"] = np.nan

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        data.to_csv(output_path, index=False)

    return data


if __name__ == "__main__":
    generate_synthetic_data(output_path="data/synthetic_promotion_user_behavior.csv")
