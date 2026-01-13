from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional


@dataclass(frozen=True)
class TopRiskRow:
    kind: Literal["module", "file"]
    name: str  # module name or file path
    classifier: List[str]
    risk: float
    why_now: List[str]


@dataclass(frozen=True)
class UpcomingPainRow:
    kind: Literal["module", "file"]
    name: str  # module name or file path
    classifier: List[str]
    risk: Optional[float]
    state_after_4w: str
    why_soon: List[str]


@dataclass(frozen=True)
class RiskCluster:
    """Grouped view for top risky items.

    This powers 'big picture' sections in renderers without duplicating
    grouping logic in each presentation layer.
    """

    signal: str
    count: int
    examples: List[str]


@dataclass(frozen=True)
class RiskClustersOverview:
    modules: List[RiskCluster] = field(default_factory=list)
    files: List[RiskCluster] = field(default_factory=list)


@dataclass(frozen=True)
class TopRiskClusterMember:
    """A TopRiskRow inside a specific cluster, with rank preserved."""

    rank: int
    kind: Literal["module", "file"]
    name: str
    classifier: List[str]
    risk: float
    why_now: List[str]


@dataclass(frozen=True)
class TopRiskCluster:
    """A cluster of top risky items (usually grouped by a primary signal)."""

    cluster_id: str
    kind: Literal["module", "file"]
    label: str
    count: int
    members: List[TopRiskClusterMember] = field(default_factory=list)


@dataclass(frozen=True)
class ScoringWeightsModel:
    churn: float
    contributors: float
    fix_ratio: float
    commits: float
    churn_acceleration: float
    coupling: float = 0.0
    ownership_concentration: float = 0.0
    revert_ratio: float = 0.0
    fix_follow_ratio: float = 0.0
    ownership_churn: float = 0.0


@dataclass(frozen=True)
class ReportMeta:
    repo_path: str
    scanned_commits: int
    as_of_day_utc: Optional[str]
    max_commits_arg: Optional[int]
    k: int
    seed: int
    repo_url: Optional[str] = None


@dataclass
class ReportModel:
    meta: ReportMeta
    scoring_weights: ScoringWeightsModel
    upcoming_pain: List[UpcomingPainRow] = field(default_factory=list)
    # Renamed from `top_risky` -> `top_hotspots` (more user-facing wording).
    # Kept backwards compatible via:
    # - `from_dict()` reading either key
    # - `top_risky` property alias
    top_hotspots: List[TopRiskRow] = field(default_factory=list)
    risk_clusters: Optional[RiskClustersOverview] = None
    top_risky_clustered: List[TopRiskCluster] = field(default_factory=list)

    @property
    def top_risky(self) -> List[TopRiskRow]:
        """Deprecated alias for `top_hotspots` (kept for compatibility)."""

        return self.top_hotspots

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: Path) -> None:
        path.write_text(json.dumps(self.to_dict(), indent=2, sort_keys=True), encoding="utf-8")

    @staticmethod
    def _coerce_str_list(value: Any) -> List[str]:
        """Coerce a JSON value into a list of strings.

        Backwards compatible with older report versions where these fields
        were stored as a single concatenated string.
        """

        if value is None:
            return []
        if isinstance(value, list):
            return [str(v).strip() for v in value if str(v).strip()]
        if isinstance(value, str):
            s = value.strip()
            if not s:
                return []
            # Older reports used "; " (and sometimes ", ") as joiners.
            if ";" in s:
                parts = [p.strip() for p in s.split(";")]
                return [p for p in parts if p]
            if "," in s:
                parts = [p.strip() for p in s.split(",")]
                return [p for p in parts if p]
            return [s]

        return [str(value).strip()] if str(value).strip() else []

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "ReportModel":
        meta_raw = dict(data["meta"])
        # Backwards compatibility: older JSON reports don't include repo_url.
        meta_raw.setdefault("repo_url", None)
        meta = ReportMeta(**meta_raw)
        scoring = ScoringWeightsModel(**data["scoring_weights"])

        upcoming: List[UpcomingPainRow] = []
        for row in data.get("upcoming_pain", []):
            row = dict(row)
            row["classifier"] = ReportModel._coerce_str_list(row.get("classifier"))
            row["why_soon"] = ReportModel._coerce_str_list(row.get("why_soon"))
            upcoming.append(UpcomingPainRow(**row))

        top: List[TopRiskRow] = []
        for row in (data.get("top_hotspots") or data.get("top_risky") or []):
            row = dict(row)
            row["classifier"] = ReportModel._coerce_str_list(row.get("classifier"))
            row["why_now"] = ReportModel._coerce_str_list(row.get("why_now"))
            top.append(TopRiskRow(**row))

        clusters = None
        raw_clusters = data.get("risk_clusters")
        if isinstance(raw_clusters, dict):
            # Be forgiving: older JSON reports won't have this field.
            mods: List[RiskCluster] = []
            for c in raw_clusters.get("modules", []) or []:
                if isinstance(c, dict):
                    mods.append(
                        RiskCluster(
                            signal=str(c.get("signal", "") or ""),
                            count=int(c.get("count", 0) or 0),
                            examples=ReportModel._coerce_str_list(c.get("examples")),
                        )
                    )
            fils: List[RiskCluster] = []
            for c in raw_clusters.get("files", []) or []:
                if isinstance(c, dict):
                    fils.append(
                        RiskCluster(
                            signal=str(c.get("signal", "") or ""),
                            count=int(c.get("count", 0) or 0),
                            examples=ReportModel._coerce_str_list(c.get("examples")),
                        )
                    )
            clusters = RiskClustersOverview(modules=mods, files=fils)

        clustered: List[TopRiskCluster] = []
        raw_clustered = data.get("top_risky_clustered")
        if isinstance(raw_clustered, list):
            for c in raw_clustered:
                if not isinstance(c, dict):
                    continue
                members: List[TopRiskClusterMember] = []
                for m in c.get("members", []) or []:
                    if not isinstance(m, dict):
                        continue
                    m = dict(m)
                    m["classifier"] = ReportModel._coerce_str_list(m.get("classifier"))
                    m["why_now"] = ReportModel._coerce_str_list(m.get("why_now"))
                    # rank/risk should be numeric; tolerate strings.
                    try:
                        m["rank"] = int(m.get("rank", 0) or 0)
                    except Exception:
                        m["rank"] = 0
                    try:
                        m["risk"] = float(m.get("risk", 0.0) or 0.0)
                    except Exception:
                        m["risk"] = 0.0
                    members.append(TopRiskClusterMember(**m))

                clustered.append(
                    TopRiskCluster(
                        cluster_id=str(c.get("cluster_id", "") or ""),
                        kind=str(c.get("kind", "") or "file"),  # type: ignore[arg-type]
                        label=str(c.get("label", "") or ""),
                        count=int(c.get("count", len(members)) or len(members)),
                        members=members,
                    )
                )

        return ReportModel(
            meta=meta,
            scoring_weights=scoring,
            upcoming_pain=upcoming,
            top_hotspots=top,
            risk_clusters=clusters,
            top_risky_clustered=clustered,
        )

    @staticmethod
    def from_json(path: Path) -> "ReportModel":
        return ReportModel.from_dict(json.loads(path.read_text(encoding="utf-8")))
