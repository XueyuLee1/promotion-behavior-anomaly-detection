"""Clustering helpers for promotion-period user segmentation."""

from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score


def run_kmeans(features, n_clusters: int = 5, random_state: int = 42):
    model = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=20)
    labels = model.fit_predict(features)
    score = silhouette_score(features, labels)
    return model, labels, score


def run_pca(features, random_state: int = 42) -> pd.DataFrame:
    pca = PCA(n_components=2, random_state=random_state)
    points = pca.fit_transform(features)
    return pd.DataFrame(
        {
            "pca_1": points[:, 0],
            "pca_2": points[:, 1],
            "explained_variance_1": pca.explained_variance_ratio_[0],
            "explained_variance_2": pca.explained_variance_ratio_[1],
        }
    )


def cluster_profile(data: pd.DataFrame, cluster_column: str = "cluster") -> pd.DataFrame:
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
    return data.groupby(cluster_column)[profile_columns].mean().round(3)
