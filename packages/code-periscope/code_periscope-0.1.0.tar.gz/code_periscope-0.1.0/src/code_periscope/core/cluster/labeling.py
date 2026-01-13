from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence

import numpy as np


@dataclass(frozen=True)
class LabelingConfig:
    # Minimum absolute z-score to consider a feature meaningful for naming.
    strong_threshold: float = 0.75
    # How many features to mention at most.
    max_features: int = 3


def label_clusters_from_centroids(
    *,
    centroids_z: np.ndarray,
    feature_cols: Sequence[str],
    config: LabelingConfig = LabelingConfig(),
) -> Dict[int, str]:
    """Generate deterministic human-readable labels from cluster centroids.

    Inputs:
      - centroids_z: array shape (k, n_features) in *standardized* (z-score) space.
      - feature_cols: names for each feature.

    Output:
      Mapping cluster_id -> label string.

    Heuristic:
      - pick up to `max_features` features with largest |z|
      - map sign/magnitude to terms: low/medium/high
      - join into a short phrase

    Example:
      "high churn, high contributors, high fix_ratio"
    """

    if len(feature_cols) == 0:
        raise ValueError("feature_cols must not be empty")

    centroids = np.asarray(centroids_z, dtype=float)
    if centroids.ndim != 2 or centroids.shape[1] != len(feature_cols):
        raise ValueError("centroids_z must be (k, n_features) matching feature_cols")

    labels: Dict[int, str] = {}

    for cluster_id, row in enumerate(centroids):
        abs_row = np.abs(row)
        order = np.argsort(abs_row)[::-1]

        parts: List[str] = []
        for idx in order:
            z = float(row[idx])
            if abs(z) < config.strong_threshold:
                continue
            feat = feature_cols[int(idx)]

            if z >= 1.5:
                level = "very high"
            elif z >= config.strong_threshold:
                level = "high"
            elif z <= -1.5:
                level = "very low"
            else:
                level = "low"

            parts.append(f"{level} {feat}")
            if len(parts) >= config.max_features:
                break

        if not parts:
            labels[cluster_id] = "balanced"
        else:
            labels[cluster_id] = ", ".join(parts)

    return labels
