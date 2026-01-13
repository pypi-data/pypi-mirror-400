from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class TrendConfig:
    # Recent window used for slope / forecast.
    recent_days: int = 28
    # Baseline (longer) window used for "recent vs baseline" comparisons.
    baseline_days: int = 90
    # Spike detection: compare last value to trailing window percentiles.
    spike_trailing_days: int = 56
    spike_quantile: float = 0.95

    # Forecast horizons.
    forecast_days: int = 28  # (~4 weeks)


def _ensure_utc_day(s: pd.Series) -> pd.Series:
    dt = pd.to_datetime(s, utc=True, errors="coerce")
    return dt.dt.normalize()


def _linear_slope_per_day(y: np.ndarray) -> float:
    """Return slope per day for y[0..n-1] using least squares on x=0..n-1.

    For n<2, returns 0.0.
    """

    n = int(len(y))
    if n < 2:
        return 0.0
    # x is strictly increasing in time; y is aligned with x.
    x = np.arange(n, dtype=float)
    y = y.astype(float)
    # slope = cov(x,y) / var(x)
    denom = float(np.var(x))
    if denom < 1e-12:
        return 0.0
    return float(np.cov(x, y, bias=True)[0, 1] / denom)


def _window(df: pd.DataFrame, *, end_day: pd.Timestamp, days: int) -> pd.DataFrame:
    start = end_day - pd.Timedelta(days=days - 1)
    return df[(df["day_start"] >= start) & (df["day_start"] <= end_day)]


def compute_entity_trend_features(
    daily_df: pd.DataFrame,
    *,
    entity_col: str,
    config: TrendConfig = TrendConfig(),
    as_of_day: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """Compute trend/anomaly features for each entity from daily metrics.

    Contract:
      - Input must include columns: entity_col, day_start, churn, commits, contributors
      - day_start is interpreted as UTC and normalized
      - Output is one row per entity with an `as_of_day` anchor

    Notes:
      - This is intentionally dependency-light (no statsmodels).
      - We treat missing days as 0 activity by reindexing to daily frequency.
    """

    if daily_df.empty:
        return pd.DataFrame(
            columns=[
                entity_col,
                "as_of_day",
                "days_observed",
                "baseline_churn_slope",
                "baseline_commits_slope",
                "baseline_contributors_slope",
                "recent_churn_slope",
                "recent_commits_slope",
                "recent_contributors_slope",
                "churn_acceleration",
                "commits_acceleration",
                "contributors_acceleration",
                "recent_churn_mean",
                "recent_commits_mean",
                "recent_contributors_mean",
                "baseline_churn_mean",
                "baseline_commits_mean",
                "baseline_contributors_mean",
                "delta_churn_mean",
                "delta_commits_mean",
                "delta_contributors_mean",
                "last_churn",
                "last_commits",
                "last_contributors",
                "churn_spike_score",
                "commits_spike_score",
            ]
        )

    df = daily_df.copy()
    df["day_start"] = _ensure_utc_day(df["day_start"])

    if as_of_day is None:
        as_of_day = df["day_start"].max()
    else:
        as_of_day = pd.to_datetime(as_of_day, utc=True).normalize()

    # Keep only up to as_of_day.
    df = df[df["day_start"] <= as_of_day]

    # Ensure expected value cols exist.
    for col in ["churn", "commits", "contributors"]:
        if col not in df.columns:
            df[col] = 0

    rows = []
    for entity, sub in df.groupby(entity_col, dropna=False):
        sub = sub.sort_values("day_start")

        # Reindex to daily, fill missing days with zeros.
        idx = pd.date_range(sub["day_start"].min(), as_of_day, freq="D", tz="UTC")
        sub = (
            sub.set_index("day_start")
            .reindex(idx)
            .rename_axis("day_start")
            .reset_index()
        )
        sub[entity_col] = entity
        for col in ["churn", "commits", "contributors"]:
            sub[col] = pd.to_numeric(sub[col], errors="coerce").fillna(0.0)

        days_observed = int(len(sub))

        recent = _window(sub, end_day=as_of_day, days=config.recent_days)
        baseline = _window(sub, end_day=as_of_day, days=config.baseline_days)
        trailing = _window(sub, end_day=as_of_day, days=config.spike_trailing_days)

        baseline_churn_slope = _linear_slope_per_day(baseline["churn"].to_numpy())
        baseline_commits_slope = _linear_slope_per_day(baseline["commits"].to_numpy())
        baseline_contrib_slope = _linear_slope_per_day(baseline["contributors"].to_numpy())

        # slopes
        recent_churn_slope = _linear_slope_per_day(recent["churn"].to_numpy())
        recent_commits_slope = _linear_slope_per_day(recent["commits"].to_numpy())
        recent_contrib_slope = _linear_slope_per_day(recent["contributors"].to_numpy())

        churn_acceleration = recent_churn_slope - baseline_churn_slope
        commits_acceleration = recent_commits_slope - baseline_commits_slope
        contributors_acceleration = recent_contrib_slope - baseline_contrib_slope

        # means
        recent_churn_mean = float(recent["churn"].mean()) if len(recent) else 0.0
        recent_commits_mean = float(recent["commits"].mean()) if len(recent) else 0.0
        recent_contrib_mean = float(recent["contributors"].mean()) if len(recent) else 0.0

        baseline_churn_mean = float(baseline["churn"].mean()) if len(baseline) else 0.0
        baseline_commits_mean = float(baseline["commits"].mean()) if len(baseline) else 0.0
        baseline_contrib_mean = float(baseline["contributors"].mean()) if len(baseline) else 0.0

        # deltas (recent - baseline)
        delta_churn_mean = recent_churn_mean - baseline_churn_mean
        delta_commits_mean = recent_commits_mean - baseline_commits_mean
        delta_contrib_mean = recent_contrib_mean - baseline_contrib_mean

        last_churn = float(sub["churn"].iloc[-1]) if len(sub) else 0.0
        last_commits = float(sub["commits"].iloc[-1]) if len(sub) else 0.0
        last_contrib = float(sub["contributors"].iloc[-1]) if len(sub) else 0.0

        # spike score: how far above trailing quantile the last point is.
        def spike_score(series: pd.Series) -> float:
            if len(trailing) < 7:
                return 0.0
            q = float(series.quantile(config.spike_quantile))
            if q < 1e-12:
                return float(last_churn if series.name == "churn" else last_commits)  # absolute fallback
            last_val = float(series.iloc[-1])
            return max(0.0, (last_val - q) / max(1e-12, q))

        churn_spike_score = spike_score(trailing["churn"])
        commits_spike_score = spike_score(trailing["commits"])

        rows.append(
            {
                entity_col: entity,
                "as_of_day": as_of_day,
                "days_observed": days_observed,
                "baseline_churn_slope": baseline_churn_slope,
                "baseline_commits_slope": baseline_commits_slope,
                "baseline_contributors_slope": baseline_contrib_slope,
                "recent_churn_slope": recent_churn_slope,
                "recent_commits_slope": recent_commits_slope,
                "recent_contributors_slope": recent_contrib_slope,
                "churn_acceleration": churn_acceleration,
                "commits_acceleration": commits_acceleration,
                "contributors_acceleration": contributors_acceleration,
                "recent_churn_mean": recent_churn_mean,
                "recent_commits_mean": recent_commits_mean,
                "recent_contributors_mean": recent_contrib_mean,
                "baseline_churn_mean": baseline_churn_mean,
                "baseline_commits_mean": baseline_commits_mean,
                "baseline_contributors_mean": baseline_contrib_mean,
                "delta_churn_mean": delta_churn_mean,
                "delta_commits_mean": delta_commits_mean,
                "delta_contributors_mean": delta_contrib_mean,
                "last_churn": last_churn,
                "last_commits": last_commits,
                "last_contributors": last_contrib,
                "churn_spike_score": churn_spike_score,
                "commits_spike_score": commits_spike_score,
            }
        )

    out = pd.DataFrame(rows)
    out = out.sort_values(["churn_spike_score", "recent_churn_slope"], ascending=False).reset_index(drop=True)
    return out


def forecast_entity_series_growth_aware(
    daily_df: pd.DataFrame,
    *,
    entity_col: str,
    value_col: str,
    config: TrendConfig = TrendConfig(),
    as_of_day: Optional[pd.Timestamp] = None,
    accel_multiplier: float = 1.5,
    accel_cap: float = 5.0,
) -> pd.DataFrame:
    """Growth-aware forecast for the next ~2-4 weeks.

    Motivation: if the series was roughly linear historically but recently started growing faster,
    the plain linear model underestimates near-term pain.

    Approach (piecewise linear with acceleration boost):
      - compute baseline slope over `baseline_days`
      - compute recent slope over `recent_days`
      - if recent_slope > baseline_slope, boost the forward slope by a factor derived from the ratio
        (bounded by accel_cap) and scaled by accel_multiplier.

    Output columns match `forecast_entity_series`, plus `model`.
    """

    if daily_df.empty:
        return pd.DataFrame(
            columns=[
                entity_col,
                "as_of_day",
                "forecast_day",
                f"{value_col}_yhat",
                f"{value_col}_lo",
                f"{value_col}_hi",
                "model",
            ]
        )

    df = daily_df.copy()
    df["day_start"] = _ensure_utc_day(df["day_start"])

    if as_of_day is None:
        as_of_day = df["day_start"].max()
    else:
        as_of_day = pd.to_datetime(as_of_day, utc=True).normalize()

    df = df[df["day_start"] <= as_of_day]
    if value_col not in df.columns:
        df[value_col] = 0

    rows = []
    for entity, sub in df.groupby(entity_col, dropna=False):
        sub = sub.sort_values("day_start")
        idx = pd.date_range(sub["day_start"].min(), as_of_day, freq="D", tz="UTC")
        sub = (
            sub.set_index("day_start")
            .reindex(idx)
            .rename_axis("day_start")
            .reset_index()
        )
        sub[entity_col] = entity
        y = pd.to_numeric(sub[value_col], errors="coerce").fillna(0.0).to_numpy(dtype=float)

        base = _window(
            pd.DataFrame({"day_start": sub["day_start"], value_col: y}),
            end_day=as_of_day,
            days=config.baseline_days,
        )
        rec = _window(
            pd.DataFrame({"day_start": sub["day_start"], value_col: y}),
            end_day=as_of_day,
            days=config.recent_days,
        )

        y_base = base[value_col].to_numpy(dtype=float)
        y_recent = rec[value_col].to_numpy(dtype=float)

        baseline_slope = _linear_slope_per_day(y_base)
        recent_slope = _linear_slope_per_day(y_recent)

        # Boost slope if accelerating.
        # Determine whether we're accelerating in the *same direction* as the baseline.
        # If baseline trend is decreasing (negative), a recent flat slope should not be treated as "growth".
        boost = 1.0
        base_mag = max(1e-12, abs(baseline_slope))

        # Only boost when baseline is non-negative and recent is meaningfully more positive.
        if baseline_slope >= 0 and recent_slope > baseline_slope + 1e-12:
            ratio = min(accel_cap, max(1.0, recent_slope / base_mag))
            boost = 1.0 + (ratio - 1.0) * accel_multiplier
        elif baseline_slope < 0 and recent_slope > 0:
            # Trend direction flipped from down to up => treat as a stronger signal
            boost = 1.0 + accel_multiplier

        slope = recent_slope * boost
        intercept = float(y_recent[-1]) if len(y_recent) else 0.0

        # Residual-based uncertainty from recent.
        if len(y_recent) >= 3:
            x = np.arange(len(y_recent), dtype=float)
            y_fit = (x - (len(y_recent) - 1)) * recent_slope + intercept
            resid = y_recent - y_fit
            sigma = float(np.std(resid))
        else:
            sigma = 0.0

        for h in range(1, config.forecast_days + 1):
            day = as_of_day + pd.Timedelta(days=h)
            yhat = max(0.0, intercept + slope * h)
            lo = max(0.0, yhat - 2.0 * sigma)
            hi = max(0.0, yhat + 2.0 * sigma)
            rows.append(
                {
                    entity_col: entity,
                    "as_of_day": as_of_day,
                    "forecast_day": day,
                    f"{value_col}_yhat": yhat,
                    f"{value_col}_lo": lo,
                    f"{value_col}_hi": hi,
                    "model": "growth_aware_linear",
                }
            )

    return pd.DataFrame(rows)


def forecast_entity_series(
    daily_df: pd.DataFrame,
    *,
    entity_col: str,
    value_col: str,
    config: TrendConfig = TrendConfig(),
    as_of_day: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """Forecast the next ~2-4 weeks for a value column using a simple linear trend.

    Output: one row per (entity, forecast_day) with yhat and interval-ish bounds.

    Method:
      - fill missing days with 0
      - fit slope on last `recent_days`
      - forecast forward `forecast_days`
      - bound predictions at >=0
      - estimate uncertainty from residual stddev on the recent window
    """

    if daily_df.empty:
        return pd.DataFrame(columns=[entity_col, "as_of_day", "forecast_day", f"{value_col}_yhat", f"{value_col}_lo", f"{value_col}_hi"])

    df = daily_df.copy()
    df["day_start"] = _ensure_utc_day(df["day_start"])

    if as_of_day is None:
        as_of_day = df["day_start"].max()
    else:
        as_of_day = pd.to_datetime(as_of_day, utc=True).normalize()

    df = df[df["day_start"] <= as_of_day]
    if value_col not in df.columns:
        df[value_col] = 0

    rows = []
    for entity, sub in df.groupby(entity_col, dropna=False):
        sub = sub.sort_values("day_start")
        idx = pd.date_range(sub["day_start"].min(), as_of_day, freq="D", tz="UTC")
        sub = (
            sub.set_index("day_start")
            .reindex(idx)
            .rename_axis("day_start")
            .reset_index()
        )
        sub[entity_col] = entity
        y = pd.to_numeric(sub[value_col], errors="coerce").fillna(0.0).to_numpy(dtype=float)

        recent = _window(pd.DataFrame({"day_start": sub["day_start"], value_col: y}), end_day=as_of_day, days=config.recent_days)
        y_recent = recent[value_col].to_numpy(dtype=float)
        slope = _linear_slope_per_day(y_recent)
        intercept = float(y_recent[-1]) if len(y_recent) else 0.0

        # Residual-based uncertainty
        if len(y_recent) >= 3:
            x = np.arange(len(y_recent), dtype=float)
            y_fit = (x - (len(y_recent) - 1)) * slope + intercept
            resid = y_recent - y_fit
            sigma = float(np.std(resid))
        else:
            sigma = 0.0

        for h in range(1, config.forecast_days + 1):
            day = as_of_day + pd.Timedelta(days=h)
            yhat = max(0.0, intercept + slope * h)
            lo = max(0.0, yhat - 2.0 * sigma)
            hi = max(0.0, yhat + 2.0 * sigma)
            rows.append(
                {
                    entity_col: entity,
                    "as_of_day": as_of_day,
                    "forecast_day": day,
                    f"{value_col}_yhat": yhat,
                    f"{value_col}_lo": lo,
                    f"{value_col}_hi": hi,
                }
            )

    return pd.DataFrame(rows)
