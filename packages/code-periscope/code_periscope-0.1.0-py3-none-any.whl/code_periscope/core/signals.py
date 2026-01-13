from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List


@dataclass(frozen=True)
class SignalDefinition:
    key: str
    title: str
    meaning: str


# A lightweight mapping layer to make model + report more human-readable.
#
# Notes:
# - Cluster labels come from centroid labeling and look like: "very high churn".
# - Overlay tags are fixed strings like: "high coupling".
#
# We keep this mapping intentionally conservative: we preserve the original
# numeric qualifiers (very high/high/low) but rephrase the metric names.
_SIGNAL_TOKEN_MAP: Dict[str, str] = {
    # Cluster label feature names
    "churn": "code churn (lines changed)",
    "commits": "commit count",
    "contributors": "number of contributors",
    "files_touched": "files touched",
    "fix_ratio": "fix-heavy changes",

    # Special labels
    "singleton": "small / one-off area",
    "balanced": "balanced activity",

    # Overlay tags (already close to readable, but we can polish)
    "high coupling": "high coupling (wide blast radius)",
    "high ownership concentration": "high ownership concentration (bus factor risk)",
    "ownership churn": "ownership churn (handoffs / new owners)",
    "elevated reverts": "elevated revert rate (instability)",
    "fix-follow hotspot": "fix-follow hotspot (fixes quickly follow changes)",
}


SIGNAL_DEFINITIONS: List[SignalDefinition] = [
    SignalDefinition(
        key="code churn (lines changed)",
        title="Code churn (lines changed)",
        meaning="A lot of lines are being edited. High churn often correlates with rework, refactors, or unstable requirements.",
    ),
    SignalDefinition(
        key="commit count",
        title="Commit count",
        meaning="Many commits landing in this area. Often indicates active development or repeated attempts to land changes.",
    ),
    SignalDefinition(
        key="number of contributors",
        title="Number of contributors",
        meaning="Many different authors touched this area. Can signal coordination overhead or unclear ownership.",
    ),
    SignalDefinition(
        key="files touched",
        title="Files touched",
        meaning="Changes span many files within this module. Often indicates broader scope or cross-cutting changes.",
    ),
    SignalDefinition(
        key="fix-heavy changes",
        title="Fix-heavy changes",
        meaning="A large share of commits look like fixes (based on commit message). Often correlates with defects, instability, or rushed delivery.",
    ),
    SignalDefinition(
        key="high coupling (wide blast radius)",
        title="High coupling (wide blast radius)",
        meaning="This area frequently changes together with many other areas. Changing it can trigger follow-on work elsewhere.",
    ),
    SignalDefinition(
        key="high ownership concentration (bus factor risk)",
        title="High ownership concentration (bus factor risk)",
        meaning="Most commits are authored by one person. Delivery risk increases when that person is unavailable, and review load can concentrate.",
    ),
    SignalDefinition(
        key="ownership churn (handoffs / new owners)",
        title="Ownership churn (handoffs / new owners)",
        meaning="Ownership is changing (new contributors showing up or top-author share shifting). This can look like onboarding, handoffs, or unclear ownership.",
    ),
    SignalDefinition(
        key="elevated revert rate (instability)",
        title="Elevated revert rate (instability)",
        meaning="Reverts are relatively frequent. This often indicates risky rollouts, failing changes, or unstable integration.",
    ),
    SignalDefinition(
        key="fix-follow hotspot (fixes quickly follow changes)",
        title="Fix-follow hotspot (fixes quickly follow changes)",
        meaning="A high share of fixes land shortly after other changes in the same area. This can indicate churn-driven defects or incomplete initial changes.",
    ),
    SignalDefinition(
        key="small / one-off area",
        title="Small / one-off area",
        meaning="Only a tiny amount of activity was observed here. Signal strength is low; treat as informational.",
    ),
    SignalDefinition(
        key="balanced activity",
        title="Balanced activity",
        meaning="No single metric strongly stands out vs the rest of the repo.",
    ),
]


def humanize_signals(signals: Iterable[str]) -> List[str]:
    """Convert internal signal phrases into more human-readable ones.

    This is primarily used for what we currently store in `ReportModel.classifier`.
    """

    out: List[str] = []
    for s in signals or []:
        raw = str(s or "").strip()
        if not raw:
            continue

        # Cluster labels often arrive as a single comma-separated phrase.
        # Example: "very high commits, very high files_touched".
        if "," in raw:
            expanded: List[str] = []
            for part in [p.strip() for p in raw.split(",") if p.strip()]:
                expanded.extend(humanize_signals([part]))
            for e in expanded:
                if e not in out:
                    out.append(e)
            continue

        # Direct match first.
        if raw in _SIGNAL_TOKEN_MAP:
            out.append(_SIGNAL_TOKEN_MAP[raw])
            continue

        # Cluster labels are often of the form: "very high churn".
        parts = raw.split(" ", 2)
        if len(parts) >= 2 and parts[-1] in _SIGNAL_TOKEN_MAP:
            # Handles: "high coupling" too, but those are already direct matched above.
            pass

        if raw.startswith("very high "):
            feat = raw[len("very high ") :].strip()
            repl = _SIGNAL_TOKEN_MAP.get(feat)
            out.append(f"very high {repl}" if repl else raw)
            continue
        if raw.startswith("high "):
            feat = raw[len("high ") :].strip()
            repl = _SIGNAL_TOKEN_MAP.get(feat)
            out.append(f"high {repl}" if repl else raw)
            continue
        if raw.startswith("very low "):
            feat = raw[len("very low ") :].strip()
            repl = _SIGNAL_TOKEN_MAP.get(feat)
            out.append(f"very low {repl}" if repl else raw)
            continue
        if raw.startswith("low "):
            feat = raw[len("low ") :].strip()
            repl = _SIGNAL_TOKEN_MAP.get(feat)
            out.append(f"low {repl}" if repl else raw)
            continue

        out.append(raw)

    # de-dupe while preserving order
    seen = set()
    deduped: List[str] = []
    for s in out:
        if s in seen:
            continue
        seen.add(s)
        deduped.append(s)
    return deduped


def render_signals_glossary_markdown() -> str:
    lines: List[str] = []
    lines.append("## Signals glossary\n")
    lines.append("Signals are short labels that summarize why an area is worth attention.\n")
    for d in SIGNAL_DEFINITIONS:
        lines.append(f"- **{d.title}**: {d.meaning}")
    return "\n".join(lines).rstrip() + "\n"


def signal_display_title(signal: str) -> str:
    """Convert a humanized signal string into a short display title.

    Example:
      - "high coupling (wide blast radius)" -> "high coupling"
      - "very high commit count" -> unchanged
    """

    s = str(signal or "").strip()
    if not s:
        return ""
    if "(" in s and s.endswith(")"):
        return s.split("(", 1)[0].strip()
    return s


def signals_display_titles(signals: Iterable[str]) -> List[str]:
    return [t for t in (signal_display_title(s) for s in (signals or [])) if t]
