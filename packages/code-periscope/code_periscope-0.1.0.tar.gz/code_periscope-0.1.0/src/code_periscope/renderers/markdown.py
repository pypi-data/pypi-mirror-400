from __future__ import annotations

from typing import List, Sequence

from code_periscope.core.report_model import ReportModel
from code_periscope.core.signals import render_signals_glossary_markdown, signals_display_titles


def _attention_level(risk: object) -> str:
    """Map the numeric 0..1 risk score into a qualitative attention label."""

    try:
        x = float(risk) if risk is not None else 0.0
    except Exception:
        x = 0.0

    if x >= 0.70:
        return "High"
    if x >= 0.35:
        return "Medium"
    return "Low"


def _md_escape_cell(value: str) -> str:
    # Basic table-safety: avoid breaking the pipe-separated table.
    return (value or "").replace("|", "\\|").strip()


def _md_join_cell(values: Sequence[str]) -> str:
    """Join a list of phrases into a single Markdown-table-safe cell."""

    cleaned = [v.strip() for v in values if v and v.strip()]
    return _md_escape_cell("; ".join(cleaned))


def _render_state_and_attention_glossary_markdown() -> str:
    """Glossary for non-signal report fields.

    Keep this short and user-facing (similar to the Signals glossary).
    """

    lines: list[str] = []
    lines.append("## State & attention glossary\n")

    lines.append("### State in ~4 weeks\n")
    lines.append(
        "A qualitative summary of where the module/file may be headed based on recent trend features and a short-horizon forecast. "
        "It’s an *early warning* label, not a guarantee.\n"
    )
    lines.append("Common states:")
    lines.append("- **Cooling down**: Activity looks like it’s decreasing vs the recent baseline.")
    lines.append("- **Stable**: No clear acceleration/deceleration signal; activity is steady.")
    lines.append("- **Warming up**: Activity is increasing and may require attention soon.")
    lines.append("- **High churn**: Sustained high change volume; expect coordination/review load.")
    lines.append("")

    lines.append("### Attention level\n")
    lines.append(
        "A simple 3-level bucket derived from the 0–1 scoring output for each item. "
        "Use it to triage what to look at first (it’s not a probability of failure).\n"
    )
    lines.append("- **High**: score ≥ 0.70")
    lines.append("- **Medium**: 0.35 ≤ score < 0.70")
    lines.append("- **Low**: score < 0.35")
    lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _render_current_hotspots(*, lines: List[str], report: ReportModel) -> None:
    """A focused, high-signal subset of the clustered view.

    We treat "hot spots" as clusters/items whose (primary) label suggests intense
    activity (e.g. very high churn / very high commits / hot spot).
    """

    clustered = getattr(report, "top_risky_clustered", None)

    # Backward compatible rendering:
    # - Some tests / stubs construct ReportModel with only `top_hotspots` (or legacy `top_risky`)
    # - Older report_model.json might not include `top_risky_clustered`
    if not clustered:
        top = getattr(report, "top_hotspots", None) or getattr(report, "top_risky", None) or []
        if not top:
            return

        # Build a minimal grouped view on the fly (presentation fallback only).
        # Prefer kind+primary signal (first classifier entry) as the stable key.
        buckets: dict[tuple[str, str], list] = {}
        for r in top:
            sigs = list(r.classifier or [])
            primary = sigs[0] if sigs else "unclassified"
            buckets.setdefault((r.kind, primary), []).append(r)

        clustered = []
        for (kind, label), rows in sorted(buckets.items(), key=lambda kv: (-len(kv[1]), str(kv[0][1]).lower())):
            clustered.append(
                type(
                    "_C",
                    (),
                    {
                        "kind": kind,
                        "label": label,
                        "count": len(rows),
                        "members": [
                            type(
                                "_M",
                                (),
                                {
                                    "name": rr.name,
                                    "why_now": rr.why_now,
                                    "classifier": rr.classifier,
                                },
                            )
                            for rr in rows
                        ],
                    },
                )()
            )

    clustered = clustered or []
    if not clustered:
        return

    def _is_hot_label(label: str) -> bool:
        s = str(label or "").strip().lower()
        return (
            "hot spot" in s
            or "hotspot" in s
            or s.startswith("very high ")
            or s.startswith("high ")
        )

    hot_clusters = [c for c in clustered if _is_hot_label(getattr(c, "label", ""))]
    if not hot_clusters:
        return

    lines.append("## Current hotspots\n")
    lines.append(
        "Areas with the strongest current activity signals (grouped by primary signal). Use this as the first place to look for current churn / coordination risk.\n"
    )

    for c in hot_clusters:
        heading = "Modules" if c.kind == "module" else "Files"
        if str(c.label).strip().lower() == "unclassified":
            label = "Unclassified"
        else:
            label = _md_join_cell(signals_display_titles([c.label])) or _md_escape_cell(str(c.label))

        lines.append(f"### {heading}: {label} ({int(c.count)})\n")

        # Signals (titles) for the cluster: union of member classifiers.
        raw_signals: list[str] = []
        seen_lower: set[str] = set()
        for m in c.members:
            for s in (m.classifier or []):
                ss = str(s).strip()
                low = ss.lower()
                if ss and low not in seen_lower:
                    raw_signals.append(ss)
                    seen_lower.add(low)
        titles = signals_display_titles(raw_signals)
        if not titles:
            titles = ["Unclassified"]

        lines.append("Signals:")
        for t in titles:
            lines.append(f"- {t}")
        lines.append("")

        lines.append("| Name | Attention level | Why now |")
        lines.append("|---|---:|---|")
        for m in c.members:
            lines.append(
                f"| `{_md_escape_cell(m.name)}` | {_md_escape_cell(_attention_level(getattr(m, 'risk', None)))} | {_md_join_cell(m.why_now)} |"
            )
        lines.append("")


def render_markdown(report: ReportModel) -> str:
    lines: List[str] = []

    lines.append("# Code Periscope Risk Report\n")
    repo_ref = report.meta.repo_url or report.meta.repo_path
    # If it's a URL, don't wrap it in backticks so it auto-links in Markdown.
    if report.meta.repo_url:
        lines.append(f"Repository: {repo_ref}\n")
    else:
        lines.append(f"Repository: `{repo_ref}`\n")
    lines.append(f"Scanned commits: **{report.meta.scanned_commits}**\n")
    if report.meta.as_of_day_utc:
        lines.append(f"As of day (UTC): **{report.meta.as_of_day_utc}**\n")

    lines.append("## Upcoming pain areas (next 2–4 weeks)\n")
    lines.append(
        "Heuristics: recent 28-day slope + spike score + 28-day linear forecast on daily churn/commits. "
        "Use this as an early-warning signal, not a guarantee.\n"
    )

    modules = [r for r in report.upcoming_pain if r.kind == "module"]
    files = [r for r in report.upcoming_pain if r.kind == "file"]

    if modules:
        lines.append("### Modules\n")
        lines.append("| Module | Signals | State in ~4 weeks | Why soon |")
        lines.append("|---|---|---|---|")
        for r in modules:
            lines.append(
                f"| `{_md_escape_cell(r.name)}` | {_md_join_cell(signals_display_titles(r.classifier))} | {_md_escape_cell(r.state_after_4w)} | {_md_join_cell(r.why_soon)} |"
            )
        lines.append("")

    if files:
        lines.append("### Files\n")
        lines.append("| File | Signals | State in ~4 weeks | Why soon |")
        lines.append("|---|---|---|---|")
        for r in files:
            lines.append(
                f"| `{_md_escape_cell(r.name)}` | {_md_join_cell(signals_display_titles(r.classifier))} | {_md_escape_cell(r.state_after_4w)} | {_md_join_cell(r.why_soon)} |"
            )
        lines.append("")

    _render_current_hotspots(lines=lines, report=report)

    lines.append("\n")
    lines.append(_render_state_and_attention_glossary_markdown().rstrip())
    lines.append("\n")
    lines.append(render_signals_glossary_markdown().rstrip())

    return "\n".join(lines).rstrip() + "\n"
