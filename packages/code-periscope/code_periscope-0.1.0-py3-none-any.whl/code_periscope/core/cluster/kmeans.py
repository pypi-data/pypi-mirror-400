from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


@dataclass(frozen=True)
class ClusterResult:
    labels: np.ndarray  # shape (n,)
    distances: np.ndarray  # shape (n,) distance to assigned centroid
    model: KMeans
    scaler: StandardScaler


def _select_numeric_features(df: pd.DataFrame, feature_cols: Sequence[str]) -> pd.DataFrame:
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")

    X = df.loc[:, list(feature_cols)].copy()
    # Ensure numeric and handle NaNs/infs
    for c in X.columns:
        X[c] = pd.to_numeric(X[c], errors="coerce")
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0.0)
    return X


def kmeans_cluster(
    df: pd.DataFrame,
    *,
    feature_cols: Sequence[str],
    k: int,
    seed: int = 42,
) -> ClusterResult:
    """Cluster rows using StandardScaler + KMeans.

    Returns labels and distance-to-assigned-centroid as a proxy for confidence.
    """

    if k < 2:
        raise ValueError("k must be >= 2")

    X = _select_numeric_features(df, feature_cols)
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X.to_numpy(dtype=float))

    model = KMeans(n_clusters=k, random_state=seed, n_init=10)
    labels = model.fit_predict(Xs)

    # Distance to assigned centroid
    centers = model.cluster_centers_
    dists = np.linalg.norm(Xs - centers[labels], axis=1)

    return ClusterResult(labels=np.asarray(labels), distances=np.asarray(dists), model=model, scaler=scaler)


def confidence_bucket(distances: np.ndarray) -> List[str]:
    """Convert distances into low/medium/high confidence by quantiles.

    Lower distance => higher confidence.
    """

    if len(distances) == 0:
        return []

    d = np.asarray(distances, dtype=float)
    q33, q66 = np.quantile(d, [0.33, 0.66])

    buckets: List[str] = []
    for x in d:
        if x <= q33:
            buckets.append("high")
        elif x <= q66:
            buckets.append("medium")
        else:
            buckets.append("low")
    return buckets
