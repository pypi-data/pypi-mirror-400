from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class ExplanationConfig:
    """Configuration for explanation generation.

    The intent is to keep logic deterministic and dependency-light.

    Thresholds are in *normalized* 0..1 component space (after weighting), not raw units.
    """

    # Emit at most this many bullets in the short explanation.
    max_reasons: int = 3

    # Minimum component contribution to be considered a "top driver".
    min_component: float = 0.06

    # If churn acceleration is positive and above this, call it out.
    accel_callout: float = 0.05

    # If spike score is above this threshold, call it out.
    spike_callout: float = 0.25

    # If present, include a short qualitative classifier (cluster label) in explanations.
    include_classifier: bool = True


def _fmt_float(x: float, *, ndigits: int = 3) -> str:
    try:
        return f"{float(x):.{ndigits}f}"
    except Exception:
        return "0.000"


def _fmt_int(x: object) -> Optional[int]:
    try:
        v = float(x)  # type: ignore[arg-type]
    except Exception:
        return None
    if not np.isfinite(v):
        return None
    return int(round(v))


def _pct_change(recent: object, baseline: object) -> Optional[float]:
    """Return percent change (e.g. 0.30 for +30%) vs baseline.

    Returns None if inputs are missing/invalid or baseline is ~0.
    """

    try:
        r = float(recent)  # type: ignore[arg-type]
        b = float(baseline)  # type: ignore[arg-type]
    except Exception:
        return None
    if not (np.isfinite(r) and np.isfinite(b)):
        return None
    if abs(b) < 1e-9:
        return None
    return (r - b) / b


def _classifier_phrase(row: pd.Series, *, cfg: ExplanationConfig) -> str:
    if not cfg.include_classifier:
        return ""
    label = str(row.get("cluster_label", "") or "").strip()
    if not label:
        return ""
    # Keep it lightweight and skimmable; this is a qualitative hint.
    return label


def _fmt_delta_paren(pct: float) -> str:
    sign = "+" if pct > 0 else "-"
    return f"({sign}{abs(pct):.0%})"


def _is_meaningful_pct(
    pct: Optional[float],
    *,
    value_28d: Optional[int] = None,
    baseline_28d: Optional[float] = None,
) -> bool:
    """Heuristics for whether to show a percent delta.

    Goal: avoid false precision for small counts (e.g. "2 commits (+2%)").

    Option A (adaptive): show the percent only when we have enough absolute
    volume or the implied *absolute* delta over 28 days is large enough.

    Rules:
      1) Always show if abs(pct) >= 20%.
      2) Otherwise, show if value_28d is reasonably large (>= 5).
      3) Otherwise, show if implied abs delta over 28d is >= 2 units.

    This keeps small/noisy values clean while still allowing meaningful small
    percentages at higher volume.
    """

    if pct is None:
        return False
    try:
        p = float(pct)
    except Exception:
        return False
    if not np.isfinite(p):
        return False

    ap = abs(p)
    if ap >= 0.20:
        return True

    if value_28d is not None and value_28d >= 5:
        return True

    if baseline_28d is not None:
        try:
            b28 = float(baseline_28d)
        except Exception:
            b28 = float("nan")
        if np.isfinite(b28) and b28 > 0:
            implied_abs_delta_28d = ap * b28
            if implied_abs_delta_28d >= 2.0:
                return True

    return False


def _combined_recent_phrase(
    *,
    value_28d: Optional[int],
    pct: Optional[float],
    unit: str,
) -> Optional[str]:
    """Combine a recent absolute count and a percent delta into a single phrase.

    Examples:
      - 10 contributors (+27%) in the last 4 weeks
      - 16 commits (-10%) in the last 4 weeks
      - ~686 lines changed (+40%) in the last 4 weeks

    If pct is ~-100% (recent ~0), return a more human phrase.
    """

    if value_28d is None and pct is None:
        return None

    if pct is not None and pct <= -0.995:
        # Avoid awkward "100% less".
        if value_28d is not None and value_28d <= 0:
            return f"very few {unit} in the last 4 weeks"
        return f"{value_28d} {unit} in the last 4 weeks (down to near zero)" if value_28d is not None else None

    baseline_28d: Optional[float] = None
    if pct is not None and value_28d is not None:
        # If pct = (recent-baseline)/baseline, then baseline = recent/(1+pct)
        # Note: this is a best-effort inversion; it becomes unstable near -100%.
        try:
            denom = 1.0 + float(pct)
            if abs(denom) > 1e-6:
                baseline_28d = float(value_28d) / denom
        except Exception:
            baseline_28d = None

    if value_28d is None:
        # Percent only.
        return f"{_fmt_delta_paren(pct)} {unit} in the last 4 weeks" if _is_meaningful_pct(pct) else None

    if pct is None or not _is_meaningful_pct(pct, value_28d=value_28d, baseline_28d=baseline_28d):
        return f"{value_28d} {unit} in the last 4 weeks"

    return f"{value_28d} {unit} {_fmt_delta_paren(pct)} in the last 4 weeks"


def _top_component_drivers(row: pd.Series, *, cfg: ExplanationConfig) -> List[str]:
    components = {
        "lots of recent code churn": float(row.get("risk_churn", 0.0) or 0.0),
        "many people are touching it": float(row.get("risk_contributors", 0.0) or 0.0),
        "a large share of changes are bug fixes": float(row.get("risk_fix_ratio", 0.0) or 0.0),
        "it changes very often": float(row.get("risk_commits", 0.0) or 0.0),
        "changes are speeding up": float(row.get("risk_churn_acceleration", 0.0) or 0.0),
        "wide blast radius (coupled changes)": float(row.get("risk_coupling", 0.0) or 0.0),
        "high ownership concentration": float(row.get("risk_ownership_concentration", 0.0) or 0.0),
        "elevated revert rate": float(row.get("risk_revert_ratio", 0.0) or 0.0),
        "fixes often follow recent changes": float(row.get("risk_fix_follow_ratio", 0.0) or 0.0),
        "ownership is changing": float(row.get("risk_ownership_churn", 0.0) or 0.0),
    }

    drivers = [(k, v) for k, v in components.items() if v >= cfg.min_component]
    drivers.sort(key=lambda kv: kv[1], reverse=True)

    # We intentionally *don't* expose internal normalized component values ("signal strength")
    # because they're hard to interpret at a glance. Instead, we convert top drivers into
    # more concrete phrasing using absolute counts and percent deltas when available.

    def _recent_pct(metric: str) -> Optional[float]:
        recent = row.get(f"recent_{metric}", None)
        baseline = row.get(f"baseline_{metric}", None)
        return _pct_change(recent, baseline)

    out: List[str] = []
    for k, _v in drivers[: cfg.max_reasons]:
        if k == "many people are touching it":
            # Prefer absolute recent contributor count if present.
            c = _fmt_int(row.get("contributors_28d", row.get("recent_contributors", row.get("contributors", None))))
            pct = _recent_pct("contributors")
            phrase = _combined_recent_phrase(value_28d=c, pct=pct, unit="contributors")
            out.append(phrase or "many people touched it recently")
            continue

        if k == "it changes very often":
            commits = _fmt_int(row.get("commits_28d", row.get("recent_commits", row.get("commits", None))))
            pct = _recent_pct("commits")
            phrase = _combined_recent_phrase(value_28d=commits, pct=pct, unit="commits")
            out.append(phrase or "it changes frequently")
            continue

        if k == "lots of recent code churn":
            churn = _fmt_int(row.get("churn_28d", row.get("recent_churn", row.get("churn", None))))
            pct = _recent_pct("churn")
            if churn is not None:
                churn_display = int(round(churn))
                phrase = _combined_recent_phrase(value_28d=churn_display, pct=pct, unit="lines changed")
                if phrase:
                    # Keep the '~' feel for churn since it's often derived/estimated.
                    out.append(phrase.replace(f"{churn_display} lines changed", f"~{churn_display} lines changed"))
                else:
                    out.append("lots of recent code changes")
            else:
                phrase = _combined_recent_phrase(value_28d=None, pct=pct, unit="code changes")
                out.append(phrase or "lots of recent code changes")
            continue

        if k == "a large share of changes are bug fixes":
            fix_ratio = row.get("fix_ratio", None)
            try:
                fr = float(fix_ratio) if fix_ratio is not None else 0.0
                if np.isfinite(fr) and fr > 0:
                    out.append(f"{fr:.0%} of commits look like fixes")
                else:
                    out.append("many changes are fixes")
            except Exception:
                out.append("many changes are fixes")
            continue

        if k == "changes are speeding up":
            accel = float(row.get("churn_acceleration", 0.0) or 0.0)
            if accel != 0:
                direction = "speeding up" if accel > 0 else "slowing down"
                out.append(f"changes are {direction} ({_fmt_float(abs(accel))} lines/day²)")
            else:
                out.append("changes are speeding up")
            continue

        if k == "wide blast radius (coupled changes)":
            deg = _fmt_int(row.get("coupling_degree", None))
            top = str(row.get("top_coupled_entities", "") or "").strip()
            if deg is not None and deg > 0:
                if top:
                    out.append(f"coupled to {deg} other areas (often with: {top})")
                else:
                    out.append(f"coupled to {deg} other areas")
            else:
                out.append("changes tend to have a wide blast radius")
            continue

        if k == "high ownership concentration":
            share = row.get("top_author_share", None)
            try:
                s = float(share) if share is not None else float("nan")
            except Exception:
                s = float("nan")
            if np.isfinite(s) and s > 0:
                out.append(f"top contributor authored ~{s:.0%} of commits")
            else:
                out.append("owned by a small set of people")
            continue

        if k == "elevated revert rate":
            rr = row.get("revert_ratio", None)
            try:
                v = float(rr) if rr is not None else float("nan")
            except Exception:
                v = float("nan")
            if np.isfinite(v) and v > 0:
                out.append(f"{v:.0%} of commits are reverts")
            else:
                out.append("reverts have been happening")
            continue

        if k == "fixes often follow recent changes":
            ratio = row.get("fix_follow_ratio", None)
            days = _fmt_int(row.get("fix_follow_days", None))
            try:
                v = float(ratio) if ratio is not None else float("nan")
            except Exception:
                v = float("nan")
            if np.isfinite(v) and v > 0:
                if days:
                    out.append(f"{v:.0%} of fixes land within ~{days}d of prior changes")
                else:
                    out.append(f"{v:.0%} of fixes land soon after prior changes")
            else:
                out.append("fixes often land soon after changes")
            continue

        if k == "ownership is changing":
            new_c = _fmt_int(row.get("new_contributors", None))
            lost_c = _fmt_int(row.get("lost_contributors", None))
            delta = row.get("delta_top_author_share", None)
            try:
                d = float(delta) if delta is not None else float("nan")
            except Exception:
                d = float("nan")

            bits = []
            if new_c is not None and new_c > 0:
                bits.append(f"{new_c} new contributors in the last 4 weeks")
            if lost_c is not None and lost_c > 0:
                bits.append(f"{lost_c} contributors stopped touching it")
            if np.isfinite(d) and abs(d) >= 0.10:
                direction = "decreased" if d < 0 else "increased"
                bits.append(f"top-author share {direction} by ~{abs(d):.0%}")

            if bits:
                out.append(", ".join(bits))
            else:
                out.append("ownership is changing")
            continue

        out.append(k)

    # Add simple percent comparisons as extra context if we still have room.
    if len(out) < cfg.max_reasons:
        for metric, unit in [("contributors", "contributors"), ("commits", "commits"), ("churn", "lines changed")]:
            v = _fmt_int(row.get(f"{metric}_28d", row.get(f"recent_{metric}", None)))
            pct = _recent_pct(metric)
            bit = _combined_recent_phrase(value_28d=v, pct=pct, unit=unit)
            if bit and bit not in out:
                out.append(bit)
            if len(out) >= cfg.max_reasons:
                break

    return out


def build_why_risky_now(row: pd.Series, *, cfg: ExplanationConfig = ExplanationConfig()) -> str:
    """Explain why this entity is considered risky *now*.

    Uses explainable risk components already computed by `score_risk`.
    """

    drivers = _top_component_drivers(row, cfg=cfg)
    if drivers:
        # Add a tiny amount of "glue" so combinations read naturally.
        # Example: very high churn + very few commits => likely few, large commits.
        dset = set(drivers)
        if any("churn" in d and "very high" in d for d in dset) and any("very few commits" in d for d in dset):
            drivers = list(drivers) + ["(few, large changes)"]

        return "; ".join(drivers)

    # If minmax normalization collapses to zeros (common for tiny synthetic frames),
    # fall back to raw metrics so we still provide a human hint.
    churn = float(row.get("churn", 0.0) or 0.0)
    commits = float(row.get("commits", 0.0) or 0.0)
    contributors = float(row.get("contributors", 0.0) or 0.0)
    fix_ratio = float(row.get("fix_ratio", 0.0) or 0.0)
    accel = float(row.get("churn_acceleration", 0.0) or 0.0)

    raw_bits: List[str] = []
    if churn > 0:
        raw_bits.append(f"{int(churn)} lines changed")
    if commits > 0:
        raw_bits.append(f"{int(commits)} commits")
    if contributors > 0:
        raw_bits.append(f"{int(contributors)} contributors")
    if fix_ratio > 0:
        raw_bits.append(f"{fix_ratio:.0%} of commits look like fixes")
    if accel != 0:
        direction = "increasing" if accel > 0 else "slowing"
        raw_bits.append(f"churn is {direction} ({_fmt_float(abs(accel))} lines/day²)")

    if raw_bits:
        return "Based on recent activity: " + ", ".join(raw_bits[: cfg.max_reasons])

    # Final fallback: cluster + confidence
    label = str(row.get("cluster_label", "") or "")
    conf = str(row.get("confidence", "") or "")
    bits = ", ".join([b for b in [label, conf] if b])
    return f"cluster profile: {bits}" if bits else ""


def build_why_risky_soon(
    row: pd.Series,
    *,
    cfg: ExplanationConfig = ExplanationConfig(),
) -> str:
    """Explain why this entity might become a problem in the near future.

    Uses trend/forecast-related columns *if present*:
      - churn_acceleration
      - recent_churn_slope
      - churn_spike_score
      - churn_yhat_sum_28d (added by CLI when available)

    The CLI can be extended to add more forecast-derived summaries.
    """

    reasons: List[str] = []

    # Note: classifier/cluster label is now expected to be displayed as a separate
    # report column (e.g. "classifier"), not repeated inside the explanation.
    classifier = ""

    def _recent_pct(metric: str) -> Optional[float]:
        recent = row.get(f"recent_{metric}", None)
        baseline = row.get(f"baseline_{metric}", None)
        return _pct_change(recent, baseline)

    def _recent_28d(metric: str) -> Optional[int]:
        """Return an integer "last 28d" value for metric.

        We only trust explicit `{metric}_28d` fields here.

        Why: other fields like `recent_contributors` are often *means* derived from
        daily series with missing-day zeros, and can be 0 even when there were real
        commits/churn in the recent window (e.g. when running with `--max-commits`
        truncation causing incomplete daily coverage).

        Using `recent_*` here can lead to misleading phrases like
        "0 contributors in the last 4 weeks".
        """

        if f"{metric}_28d" not in row:
            return None
        v = row.get(f"{metric}_28d")
        if v is None:
            return None
        return _fmt_int(v)

    accel = float(row.get("churn_acceleration", 0.0) or 0.0)
    recent_slope = float(row.get("recent_churn_slope", 0.0) or 0.0)
    spike = float(row.get("churn_spike_score", 0.0) or 0.0)
    fc_sum = row.get("churn_yhat_sum_28d", None)
    fc_sum_56 = row.get("churn_yhat_sum_56d", None)
    state_after_4w = str(row.get("state_after_4w", "") or "")

    # Combined metric phrasing. We try to avoid repeating "in the last 4 weeks"
    # for each metric: "16 contributors (...) and 26 commits (...) in the last 4 weeks".
    def _strip_last_4w_suffix(s: str) -> str:
        return s.replace(" in the last 4 weeks", "")

    contrib_phrase = None
    commits_phrase = None
    churn_phrase = None

    v = _recent_28d("contributors")
    pct = _recent_pct("contributors")
    contrib_phrase = _combined_recent_phrase(value_28d=v, pct=pct, unit="contributors")

    v = _recent_28d("commits")
    pct = _recent_pct("commits")
    commits_phrase = _combined_recent_phrase(value_28d=v, pct=pct, unit="commits")

    v = _recent_28d("churn")
    pct = _recent_pct("churn")
    churn_phrase = _combined_recent_phrase(value_28d=v, pct=pct, unit="lines changed")
    if churn_phrase and v is not None:
        churn_phrase = churn_phrase.replace(f"{v} lines changed", f"~{v} lines changed")

    joined: List[str] = []
    for p in [contrib_phrase, commits_phrase, churn_phrase]:
        if p:
            joined.append(_strip_last_4w_suffix(p))

    # Only use the "in the last 4 weeks" suffix if at least one of these values
    # came from an explicit recent/28d field.
    has_any_recent_values = any(
        row.get(k) is not None
        for k in [
            "contributors_28d",
            "commits_28d",
            "churn_28d",
            "recent_contributors",
            "recent_commits",
            "recent_churn",
        ]
    )

    if joined:
        suffix = " in the last 4 weeks" if has_any_recent_values else ""
        if len(joined) == 1:
            reasons.append(joined[0] + suffix)
        elif len(joined) == 2:
            reasons.append(joined[0] + " and " + joined[1] + suffix)
        else:
            # Oxford comma style: a; b; and c (optional suffix)
            reasons.append("; ".join(joined[:-1]) + "; and " + joined[-1] + suffix)

    # Small glue phrases for common "this looks weird" combos.
    # These need to end up in the top `max_reasons`, so we insert them early.
    def _insert_glue(glue: str) -> None:
        if glue in reasons:
            return
        # Prefer to keep the classifier (index 0) if present.
        insert_at = 1 if classifier else 0
        reasons.insert(insert_at, glue)

    # If churn is high but commits are very few, hint that commits are probably large.
    if any("churn" in r and "very high" in r for r in reasons) and any("very few commits" in r for r in reasons):
        _insert_glue("(few, large changes)")
    # If churn is high but contributors are very few, hint at bottleneck/single-owner.
    if any("churn" in r and "very high" in r for r in reasons) and any("very few contributors" in r for r in reasons):
        _insert_glue("(concentrated in one/few people)")

    if accel > 0:
        reasons.append(f"changes are speeding up ({_fmt_float(accel)} more lines/day²)")
    elif accel < 0:
        reasons.append(f"changes are slowing down ({_fmt_float(abs(accel))} fewer lines/day²)")

    if recent_slope > 0:
        reasons.append(f"more changes each day lately (~{_fmt_float(recent_slope)} extra lines/day)")
    elif recent_slope < 0:
        reasons.append(f"fewer changes each day lately (~{_fmt_float(abs(recent_slope))} fewer lines/day)")

    if spike >= cfg.spike_callout:
        reasons.append("there was a recent spike in changes")

    if fc_sum is not None:
        try:
            fc = float(fc_sum)
            if fc > 0:
                reasons.append(f"expected change volume over the next 4 weeks: ~{fc:.0f} lines")
        except Exception:
            pass

    if fc_sum_56 is not None:
        try:
            fc8 = float(fc_sum_56)
            if fc8 > 0:
                reasons.append(f"looking 8 weeks out: ~{fc8:.0f} lines")
        except Exception:
            pass

    if state_after_4w:
        reasons.append(f"likely state in about a month: {state_after_4w}")

    # De-dupe and truncate.
    reasons = [r for i, r in enumerate(reasons) if r and r not in reasons[:i]]
    if not reasons:
        return ""

    return "; ".join(reasons[: cfg.max_reasons])


def add_explanations(
    df: pd.DataFrame,
    *,
    cfg: ExplanationConfig = ExplanationConfig(),
) -> pd.DataFrame:
    """Add human-readable explanation columns to a risk dataframe."""

    out = df.copy()

    out["why_risky_now"] = out.apply(lambda r: build_why_risky_now(r, cfg=cfg), axis=1)
    out["why_risky_soon"] = out.apply(lambda r: build_why_risky_soon(r, cfg=cfg), axis=1)

    return out
