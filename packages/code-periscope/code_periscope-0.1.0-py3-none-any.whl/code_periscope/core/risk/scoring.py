from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RiskWeights:
    churn: float = 0.35
    contributors: float = 0.25
    fix_ratio: float = 0.25
    commits: float = 0.15
    churn_acceleration: float = 0.20
    coupling: float = 0.15
    ownership_concentration: float = 0.10
    revert_ratio: float = 0.10
    fix_follow_ratio: float = 0.15
    ownership_churn: float = 0.10


def _minmax(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0.0)
    lo = float(s.min()) if len(s) else 0.0
    hi = float(s.max()) if len(s) else 0.0
    if hi - lo < 1e-12:
        return s * 0.0
    return (s - lo) / (hi - lo)


def score_risk(df: pd.DataFrame, *, weights: RiskWeights) -> pd.DataFrame:
    """Compute an explainable 0..1 risk score for each row.

        Expects columns: churn, contributors, fix_ratio, commits.
    Optionally uses: churn_acceleration (positive acceleration of churn).
    Optionally uses: coupling_degree/coupling_strength_sum (blast radius proxy).
    Optionally uses: top_author_share/ownership_hhi (bus factor proxy).
    Adds:
      - risk_score
            - risk_churn, risk_contributors, risk_fix_ratio, risk_commits, risk_churn_acceleration (components)
    """

    out = df.copy()

    churn_n = _minmax(out.get("churn", 0))
    contrib_n = _minmax(out.get("contributors", 0))
    fix_ratio_n = _minmax(out.get("fix_ratio", 0))
    commits_n = _minmax(out.get("commits", 0))

    coupling_raw = (
        pd.to_numeric(
            out["coupling_degree"] if "coupling_degree" in out.columns else pd.Series(0.0, index=out.index),
            errors="coerce",
        )
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )
    coupling_n = _minmax(coupling_raw)

    # Ownership concentration: high values mean fewer people own the area.
    # Use top_author_share if present, otherwise fall back to HHI.
    own_col = "top_author_share" if "top_author_share" in out.columns else ("ownership_hhi" if "ownership_hhi" in out.columns else None)
    own_series = out[own_col] if own_col is not None else pd.Series(0.0, index=out.index)
    own_raw = (
        pd.to_numeric(own_series, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )
    own_n = _minmax(own_raw)

    revert_raw = (
        pd.to_numeric(
            out["revert_ratio"] if "revert_ratio" in out.columns else pd.Series(0.0, index=out.index),
            errors="coerce",
        )
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )
    revert_n = _minmax(revert_raw)

    fix_follow_raw = (
        pd.to_numeric(
            out["fix_follow_ratio"] if "fix_follow_ratio" in out.columns else pd.Series(0.0, index=out.index),
            errors="coerce",
        )
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )
    fix_follow_n = _minmax(fix_follow_raw)

    # Ownership churn: new contributors entering an area can predict near-term
    # delivery risk (coordination/review load), even if concentration drops.
    new_contrib_raw = (
        pd.to_numeric(
            out["new_contributors"] if "new_contributors" in out.columns else pd.Series(0.0, index=out.index),
            errors="coerce",
        )
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )
    new_contrib_n = _minmax(new_contrib_raw)

    # Absolute ownership shift (recent vs baseline top-author share).
    delta_share_raw = (
        pd.to_numeric(
            out["delta_top_author_share"] if "delta_top_author_share" in out.columns else pd.Series(0.0, index=out.index),
            errors="coerce",
        )
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
        .abs()
    )
    delta_share_n = _minmax(delta_share_raw)

    ownership_churn_n = _minmax(0.7 * new_contrib_n + 0.3 * delta_share_n)

    # Acceleration should only increase risk when it's positive (getting worse).
    accel_series = out["churn_acceleration"] if "churn_acceleration" in out.columns else pd.Series(0.0, index=out.index)
    accel_raw = (
        pd.to_numeric(accel_series, errors="coerce")
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
    )
    accel_pos = accel_raw.clip(lower=0.0)
    accel_n = _minmax(accel_pos)

    out["risk_churn"] = churn_n * weights.churn
    out["risk_contributors"] = contrib_n * weights.contributors
    out["risk_fix_ratio"] = fix_ratio_n * weights.fix_ratio
    out["risk_commits"] = commits_n * weights.commits
    out["risk_churn_acceleration"] = accel_n * weights.churn_acceleration
    out["risk_coupling"] = coupling_n * weights.coupling
    out["risk_ownership_concentration"] = own_n * weights.ownership_concentration
    out["risk_revert_ratio"] = revert_n * weights.revert_ratio
    out["risk_fix_follow_ratio"] = fix_follow_n * weights.fix_follow_ratio
    out["risk_ownership_churn"] = ownership_churn_n * weights.ownership_churn

    out["risk_score"] = (
        out["risk_churn"]
        + out["risk_contributors"]
        + out["risk_fix_ratio"]
        + out["risk_commits"]
        + out["risk_churn_acceleration"]
        + out["risk_coupling"]
        + out["risk_ownership_concentration"]
        + out["risk_revert_ratio"]
        + out["risk_fix_follow_ratio"]
        + out["risk_ownership_churn"]
    )

    return out
