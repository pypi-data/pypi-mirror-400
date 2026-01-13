from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class OverlayTagConfig:
    """Rule-based overlay tags for near-term maintainability/delivery risk.

    These tags are meant to complement (not replace) KMeans cluster labels.
    They intentionally use lightweight, deterministic heuristics.

    Tagging philosophy:
      - Prefer percentiles over hard-coded numbers when possible.
      - Avoid tagging tiny/noisy entities: require minimum activity.
    """

    # Minimum 4-week churn (if available) or total churn to consider tagging.
    min_churn_28d: int = 50
    min_commits_28d: int = 3

    # Percentile thresholds within the population being tagged.
    high_percentile: float = 0.90

    # Absolute thresholds for ratio metrics.
    revert_ratio_high: float = 0.10
    fix_follow_ratio_high: float = 0.50

    # Ownership signals.
    top_author_share_high: float = 0.70
    delta_top_author_share_abs_high: float = 0.20


def _safe_series(df: pd.DataFrame, col: str, default: float = 0.0) -> pd.Series:
    if col not in df.columns:
        return pd.Series(default, index=df.index, dtype=float)
    return pd.to_numeric(df[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(default)


def add_overlay_tags(
    df: pd.DataFrame,
    *,
    entity_col: str,
    config: OverlayTagConfig = OverlayTagConfig(),
    existing_tags_col: str = "overlay_tags",
) -> pd.DataFrame:
    """Add `overlay_tags` column containing list[str] tags.

    Input:
      - df: per-entity table (file/module snapshot/risk input)
      - entity_col: "path" or "module"

    Output:
      - same df + `overlay_tags` list[str]

    This function does not mutate other columns, making it safe to call before
    report model projection.
    """

    if df.empty:
        out = df.copy()
        out[existing_tags_col] = [[] for _ in range(len(out))]
        return out

    out = df.copy()

    # Prefer 28d measures when present (they map better to 1–2 sprint prediction).
    # Use scalar fallbacks here  `default` must be a scalar, not a Series.
    churn_total = _safe_series(out, "churn", default=0.0)
    commits_total = _safe_series(out, "commits", default=0.0)
    churn_28d = _safe_series(out, "churn_28d", default=0.0)
    commits_28d = _safe_series(out, "commits_28d", default=0.0)

    # Backwards compatibility: if 28d columns are missing, approximate from totals.
    if "churn_28d" not in out.columns:
        churn_28d = churn_total
    if "commits_28d" not in out.columns:
        commits_28d = commits_total

    coupling_degree = _safe_series(out, "coupling_degree", default=0.0)
    coupling_strength = _safe_series(out, "coupling_strength_sum", default=0.0)

    top_author_share = _safe_series(out, "top_author_share", default=0.0)
    delta_share = _safe_series(out, "delta_top_author_share", default=0.0).abs()

    revert_ratio = _safe_series(out, "revert_ratio", default=0.0)
    fix_follow_ratio = _safe_series(out, "fix_follow_ratio", default=0.0)

    new_contrib = _safe_series(out, "new_contributors", default=0.0)

    # Activity gate: avoid tagging tiny entities.
    active = (churn_28d >= float(config.min_churn_28d)) | (commits_28d >= float(config.min_commits_28d))

    # Percentile-based thresholds for coupling.
    # We compute percentiles over active entities only, so a repo with lots of tiny
    # files doesn't skew thresholds.
    def pct(series: pd.Series, q: float) -> float:
        s = series[active]
        if len(s) < 3:
            return float(series.max())
        return float(s.quantile(q))

    coupling_degree_hi = pct(coupling_degree, config.high_percentile)
    coupling_strength_hi = pct(coupling_strength, config.high_percentile)

    tags: List[List[str]] = []
    for i in range(len(out)):
        if not bool(active.iloc[i]):
            tags.append([])
            continue

        row_tags: List[str] = []

        # Blast radius / coupling.
        if coupling_degree.iloc[i] >= coupling_degree_hi and coupling_degree.iloc[i] > 0:
            row_tags.append("high coupling")
        elif coupling_strength.iloc[i] >= coupling_strength_hi and coupling_strength.iloc[i] > 0:
            row_tags.append("high coupling")

        # Ownership concentration.
        if top_author_share.iloc[i] >= config.top_author_share_high:
            row_tags.append("high ownership concentration")

        # Ownership churn / turnover.
        if new_contrib.iloc[i] >= 2 or delta_share.iloc[i] >= config.delta_top_author_share_abs_high:
            row_tags.append("ownership churn")

        # Instability.
        if revert_ratio.iloc[i] >= config.revert_ratio_high:
            row_tags.append("elevated reverts")

        # Follow-up fixes.
        if fix_follow_ratio.iloc[i] >= config.fix_follow_ratio_high:
            row_tags.append("fix-follow hotspot")

        tags.append(row_tags)

    out[existing_tags_col] = tags
    return out


def merge_classifier_tags(cluster_label: str, overlay_tags: List[str]) -> List[str]:
    """Merge cluster label + overlay tags into classifier list[str] for the report model."""

    merged: List[str] = []
    label = (cluster_label or "").strip()
    if label and label != "nan":
        # Existing cluster labels are already semi-colon delimited phrases.
        merged.extend([p.strip() for p in label.split(";") if p.strip()])

    for t in overlay_tags or []:
        tt = str(t).strip()
        if tt and tt not in merged:
            merged.append(tt)

    return merged
