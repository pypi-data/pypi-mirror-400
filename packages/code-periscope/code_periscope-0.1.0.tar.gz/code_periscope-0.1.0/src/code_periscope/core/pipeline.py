from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
from rich.console import Console

from code_periscope.core.classify.commit_type import classify_commit_message
from code_periscope.core.classify.overlay_tags import add_overlay_tags, merge_classifier_tags
from code_periscope.core.signals import humanize_signals
from code_periscope.core.cluster.kmeans import confidence_bucket, kmeans_cluster
from code_periscope.core.cluster.labeling import label_clusters_from_centroids
from code_periscope.core.features.metrics import (
    compute_file_metrics,
    compute_file_metrics_daily,
    compute_commit_cochange_pairs,
    compute_entity_coupling_summary,
    compute_revert_metrics,
    compute_fix_follow_metrics,
    compute_ownership_churn_metrics,
    compute_module_metrics,
    compute_module_metrics_daily,
)
from code_periscope.core.features.trends import (
    TrendConfig,
    compute_entity_trend_features,
    forecast_entity_series_growth_aware,
)
from code_periscope.core.ingest.git_history import (
    commits_to_df,
    file_changes_to_df,
    iter_commit_and_file_changes,
)
from code_periscope.core.repo import detect_repo_url, resolve_repository
from code_periscope.core.report_model import (
    ReportMeta,
    ReportModel,
    RiskCluster,
    RiskClustersOverview,
    ScoringWeightsModel,
    TopRiskCluster,
    TopRiskClusterMember,
    TopRiskRow,
    UpcomingPainRow,
)
from code_periscope.core.risk.explanations import add_explanations
from code_periscope.core.risk.scoring import RiskWeights, score_risk


def _as_str_list(value: object) -> List[str]:
    """Coerce pipeline values into list[str] for report model fields.

    The pipeline historically produced concatenated explanation strings.
    The report model now expects arrays to support richer rendering.
    """

    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    s = str(value).strip()
    if not s:
        return []
    # Explanations are currently concatenated with "; ". Preserve prior ordering.
    if ";" in s:
        return [p.strip() for p in s.split(";") if p.strip()]
    if "," in s:
        return [p.strip() for p in s.split(",") if p.strip()]
    return [s]


def analyze_repository(
    *,
    repo: Optional[Path],
    git_url: Optional[str],
    refresh: bool,
    max_commits: Optional[int],
    out_dir: Path,
    k: int,
    seed: int,
    top_n: int,
    console: Optional[Console] = None,
) -> ReportModel:
    """Run the full analysis pipeline and write CSV artifacts.

    Returns a structured ReportModel that can be serialized to JSON and rendered
    into multiple report formats (Markdown now, HTML later).
    """

    console = console or Console()

    def log(msg: str) -> None:
        # Centralize logging so we can later swap in verbosity levels.
        console.print(f"[dim]• {msg}[/dim]")

    repo_path = resolve_repository(repo=repo, git_url=git_url, refresh=refresh)
    console.print(f"Repository: [bold]{repo_path}[/bold]")
    console.print(f"Output dir: [bold]{out_dir}[/bold]")
    log(f"Params: max_commits={max_commits}, k={k}, seed={seed}, top_n={top_n}")

    # Prefer explicit --git-url, otherwise best-effort detect remote from local repo.
    repo_url = git_url or detect_repo_url(repo_path)

    with console.status("Scanning commit history..."):
        commits, changes = iter_commit_and_file_changes(repo_path, max_commits=max_commits)

    commits_df = commits_to_df(commits)
    changes_df = file_changes_to_df(changes)

    log(
        f"Ingested: commits={len(commits_df)}, file_changes={len(changes_df)}, "
        f"unique_files={changes_df['path'].nunique(dropna=False) if 'path' in changes_df.columns else 'n/a'}"
    )

    if len(commits_df) and "committed_datetime" in commits_df.columns:
        dt = pd.to_datetime(commits_df["committed_datetime"], errors="coerce")
        if dt.notna().any():
            log(f"Commit time span: {dt.min()} → {dt.max()}")

    commits_df["commit_type"] = commits_df["message"].map(lambda m: classify_commit_message(m).label)
    if "commit_type" in commits_df.columns and len(commits_df):
        top_types = commits_df["commit_type"].value_counts().head(5).to_dict()
        log(f"Commit types (top): {top_types}")

    commits_csv = out_dir / "commits.csv"
    file_changes_csv = out_dir / "file_changes.csv"
    commits_df.to_csv(commits_csv, index=False)
    changes_df.to_csv(file_changes_csv, index=False)
    console.print(f"Wrote {commits_csv} ({len(commits_df)} rows)")
    console.print(f"Wrote {file_changes_csv} ({len(changes_df)} rows)")

    with console.status("Computing file/module metrics..."):
        file_metrics = compute_file_metrics(commits_df, changes_df)
        module_metrics = compute_module_metrics(commits_df, changes_df)
        file_metrics_daily = compute_file_metrics_daily(commits_df, changes_df)
        module_metrics_daily = compute_module_metrics_daily(commits_df, changes_df)

        # The root module "." is mainly a catch-all for files in the repo root,
        # and tends to dominate module risk rankings without being actionable.
        # We exclude it from module-level analysis.
        if "module" in module_metrics.columns:
            module_metrics = module_metrics[module_metrics["module"].astype(str) != "."].copy()
        if "module" in module_metrics_daily.columns:
            module_metrics_daily = module_metrics_daily[module_metrics_daily["module"].astype(str) != "."].copy()

        # Coupling (co-change) analysis.
        file_pairs = compute_commit_cochange_pairs(changes_df, entity_col="path")
        module_pairs = compute_commit_cochange_pairs(
            changes_df.assign(module=changes_df["path"].map(lambda p: str(p).split("/", 1)[0] if "/" in str(p) else ".")),
            entity_col="module",
        )
        file_coupling = compute_entity_coupling_summary(file_pairs, entity_col="path")
        module_coupling = compute_entity_coupling_summary(module_pairs, entity_col="module")

        file_reverts, module_reverts = compute_revert_metrics(commits_df, changes_df)

        file_fix_follow, module_fix_follow = compute_fix_follow_metrics(commits_df, changes_df, follow_days=7)

        file_owner_churn, module_owner_churn = compute_ownership_churn_metrics(
            commits_df, changes_df, recent_days=28, baseline_days=90
        )

    log(
        "Metrics: "
        f"file_entities={len(file_metrics)}, module_entities={len(module_metrics)}, "
        f"file_daily_rows={len(file_metrics_daily)}, module_daily_rows={len(module_metrics_daily)}"
    )

    if len(file_metrics_daily) and "day_start" in file_metrics_daily.columns:
        d = pd.to_datetime(file_metrics_daily["day_start"], errors="coerce")
        if d.notna().any():
            log(f"Daily series span: {d.min()} → {d.max()}")

    file_metrics.to_csv(out_dir / "file_metrics.csv", index=False)
    module_metrics.to_csv(out_dir / "module_metrics.csv", index=False)
    file_metrics_daily.to_csv(out_dir / "file_metrics_daily.csv", index=False)
    module_metrics_daily.to_csv(out_dir / "module_metrics_daily.csv", index=False)

    file_pairs.to_csv(out_dir / "file_cochange_pairs.csv", index=False)
    module_pairs.to_csv(out_dir / "module_cochange_pairs.csv", index=False)
    file_coupling.to_csv(out_dir / "file_coupling.csv", index=False)
    module_coupling.to_csv(out_dir / "module_coupling.csv", index=False)

    file_reverts.to_csv(out_dir / "file_reverts.csv", index=False)
    module_reverts.to_csv(out_dir / "module_reverts.csv", index=False)

    file_fix_follow.to_csv(out_dir / "file_fix_follow.csv", index=False)
    module_fix_follow.to_csv(out_dir / "module_fix_follow.csv", index=False)

    file_owner_churn.to_csv(out_dir / "file_ownership_churn.csv", index=False)
    module_owner_churn.to_csv(out_dir / "module_ownership_churn.csv", index=False)

    trend_cfg = TrendConfig()
    log(
        "Trend config: "
        f"recent_days={trend_cfg.recent_days}, baseline_days={trend_cfg.baseline_days}, "
        f"forecast_days={trend_cfg.forecast_days}, spike_q={trend_cfg.spike_quantile}"
    )
    with console.status("Computing trend features and forecasts..."):
        file_trends = compute_entity_trend_features(file_metrics_daily, entity_col="path", config=trend_cfg)
        module_trends = compute_entity_trend_features(module_metrics_daily, entity_col="module", config=trend_cfg)

        file_churn_fc = forecast_entity_series_growth_aware(
            file_metrics_daily, entity_col="path", value_col="churn", config=trend_cfg
        )
        file_commits_fc = forecast_entity_series_growth_aware(
            file_metrics_daily, entity_col="path", value_col="commits", config=trend_cfg
        )
        module_churn_fc = forecast_entity_series_growth_aware(
            module_metrics_daily, entity_col="module", value_col="churn", config=trend_cfg
        )
        module_commits_fc = forecast_entity_series_growth_aware(
            module_metrics_daily, entity_col="module", value_col="commits", config=trend_cfg
        )

    log(
        "Trends/forecast: "
        f"file_trends_rows={len(file_trends)}, module_trends_rows={len(module_trends)}, "
        f"file_churn_fc_rows={len(file_churn_fc)}, module_churn_fc_rows={len(module_churn_fc)}"
    )

    file_trends.to_csv(out_dir / "file_trends.csv", index=False)
    module_trends.to_csv(out_dir / "module_trends.csv", index=False)

    (out_dir / "forecasts").mkdir(parents=True, exist_ok=True)
    file_churn_fc.to_csv(out_dir / "forecasts" / "file_churn_forecast.csv", index=False)
    file_commits_fc.to_csv(out_dir / "forecasts" / "file_commits_forecast.csv", index=False)
    module_churn_fc.to_csv(out_dir / "forecasts" / "module_churn_forecast.csv", index=False)
    module_commits_fc.to_csv(out_dir / "forecasts" / "module_commits_forecast.csv", index=False)

    file_feature_cols = ["commits", "contributors", "churn", "fix_ratio"]
    module_feature_cols = ["commits", "contributors", "files_touched", "churn", "fix_ratio"]
    log(f"Clustering feature cols: file={file_feature_cols}, module={module_feature_cols}")

    with console.status("Clustering files/modules..."):
        if len(file_metrics) < 2:
            # Too few samples for KMeans (k>=2). Create a trivial single-cluster assignment.
            file_clusters_df = file_metrics[["path"]].copy()
            file_clusters_df["cluster"] = 0
            file_clusters_df["distance"] = 0.0
            file_clusters_df["confidence"] = "high"
            file_clusters_df["cluster_label"] = "singleton"
        else:
            file_k = max(2, min(int(k), int(len(file_metrics))))
            log(f"Clustering files: n={len(file_metrics)}, requested_k={k}, using_k={file_k}")
            file_cluster = kmeans_cluster(file_metrics, feature_cols=file_feature_cols, k=file_k, seed=seed)
            file_cluster_labels = label_clusters_from_centroids(
                centroids_z=file_cluster.model.cluster_centers_, feature_cols=file_feature_cols
            )
            file_clusters_df = file_metrics[["path"]].copy()
            file_clusters_df["cluster"] = file_cluster.labels
            file_clusters_df["distance"] = file_cluster.distances
            file_clusters_df["confidence"] = confidence_bucket(file_cluster.distances)
            file_clusters_df["cluster_label"] = file_clusters_df["cluster"].map(file_cluster_labels)

        if len(module_metrics) < 2:
            module_clusters_df = module_metrics[["module"]].copy()
            module_clusters_df["cluster"] = 0
            module_clusters_df["distance"] = 0.0
            module_clusters_df["confidence"] = "high"
            module_clusters_df["cluster_label"] = "singleton"
        else:
            module_k = max(2, min(int(k), int(len(module_metrics))))
            log(f"Clustering modules: n={len(module_metrics)}, requested_k={k}, using_k={module_k}")
            module_cluster = kmeans_cluster(module_metrics, feature_cols=module_feature_cols, k=module_k, seed=seed)
            module_cluster_labels = label_clusters_from_centroids(
                centroids_z=module_cluster.model.cluster_centers_, feature_cols=module_feature_cols
            )
            module_clusters_df = module_metrics[["module"]].copy()
            module_clusters_df["cluster"] = module_cluster.labels
            module_clusters_df["distance"] = module_cluster.distances
            module_clusters_df["confidence"] = confidence_bucket(module_cluster.distances)
            module_clusters_df["cluster_label"] = module_clusters_df["cluster"].map(module_cluster_labels)

    file_clusters_df.to_csv(out_dir / "file_clusters.csv", index=False)
    module_clusters_df.to_csv(out_dir / "module_clusters.csv", index=False)

    weights = RiskWeights()
    log(
        "Risk weights: "
        f"churn={weights.churn}, contributors={weights.contributors}, fix_ratio={weights.fix_ratio}, "
        f"commits={weights.commits}, churn_acceleration={weights.churn_acceleration}"
    )

    file_risk_input = file_metrics.merge(file_clusters_df, on="path", how="left")
    module_risk_input = module_metrics.merge(module_clusters_df, on="module", how="left")

    # Compute true recent-window totals (28d) from the daily time series.
    #
    # Why this lives in the pipeline (vs trends): the report and explanations
    # want explicit, interpretable "last 4 weeks" numbers. Trend features like
    # recent_*_mean are *not* totals and can be 0.0 in truncated/partial runs,
    # which previously produced misleading strings like:
    #   "0 contributors in the last 4 weeks" alongside non-zero commits/churn.
    #
    # Here we compute totals over the recent window so downstream consumers can
    # rely on {metric}_28d fields being coherent.
    def _aggregate_last_nd(
        daily_df: pd.DataFrame, *, entity_col: str, metrics: list[str], window_days: int
    ) -> pd.DataFrame:
        if not len(daily_df):
            return pd.DataFrame(columns=[entity_col] + [f"{m}_{window_days}d" for m in metrics])

        if "day_start" not in daily_df.columns or entity_col not in daily_df.columns:
            return pd.DataFrame(columns=[entity_col] + [f"{m}_{window_days}d" for m in metrics])

        d = pd.to_datetime(daily_df["day_start"], errors="coerce")
        if not d.notna().any():
            return pd.DataFrame(columns=[entity_col] + [f"{m}_{window_days}d" for m in metrics])

        end_day = d.max().normalize()
        start_day = end_day - pd.Timedelta(days=window_days - 1)

        recent = daily_df.copy()
        recent["_day"] = d.dt.normalize()
        recent = recent[(recent["_day"] >= start_day) & (recent["_day"] <= end_day)].copy()

        if not len(recent):
            return pd.DataFrame(columns=[entity_col] + [f"{m}_{window_days}d" for m in metrics])

        agg = {m: "sum" for m in metrics if m in recent.columns}
        out = recent.groupby(entity_col, dropna=False).agg(agg).reset_index()
        suffix = "28d" if int(window_days) == 28 else f"{int(window_days)}d"
        out = out.rename(columns={m: f"{m}_{suffix}" for m in agg.keys()})
        # Always return numeric totals (NaN -> 0) for downstream formatting.
        for m in metrics:
            col = f"{m}_{suffix}"
            if col in out.columns:
                out[col] = pd.to_numeric(out[col], errors="coerce").fillna(0.0)
        return out

    file_recent_28d = _aggregate_last_nd(
        file_metrics_daily, entity_col="path", metrics=["commits", "churn", "contributors"], window_days=28
    )
    module_recent_28d = _aggregate_last_nd(
        module_metrics_daily, entity_col="module", metrics=["commits", "churn", "contributors"], window_days=28
    )

    # Column names already normalized to "*_28d" when window_days==28.

    if len(file_recent_28d):
        file_risk_input = file_risk_input.merge(file_recent_28d, on="path", how="left")
    if len(module_recent_28d):
        module_risk_input = module_risk_input.merge(module_recent_28d, on="module", how="left")

    # Add coupling summaries as potential risk drivers / explanation evidence.
    if len(file_coupling):
        file_risk_input = file_risk_input.merge(file_coupling, on="path", how="left")
    if len(module_coupling):
        module_risk_input = module_risk_input.merge(module_coupling, on="module", how="left")

    if len(file_reverts):
        file_risk_input = file_risk_input.merge(file_reverts, on="path", how="left")
    if len(module_reverts):
        module_risk_input = module_risk_input.merge(module_reverts, on="module", how="left")

    if len(file_fix_follow):
        file_risk_input = file_risk_input.merge(file_fix_follow, on="path", how="left")
    if len(module_fix_follow):
        module_risk_input = module_risk_input.merge(module_fix_follow, on="module", how="left")

    if len(file_owner_churn):
        file_risk_input = file_risk_input.merge(file_owner_churn, on="path", how="left")
    if len(module_owner_churn):
        module_risk_input = module_risk_input.merge(module_owner_churn, on="module", how="left")

    # Overlay tags: rule-based near-term risk hints (coupling/ownership/reverts/fix-follow).
    file_risk_input = add_overlay_tags(file_risk_input, entity_col="path")
    module_risk_input = add_overlay_tags(module_risk_input, entity_col="module")

    file_trend_cols = [
        c for c in ["churn_acceleration", "recent_churn_slope", "churn_spike_score"] if c in file_trends.columns
    ]
    if file_trend_cols:
        file_risk_input = file_risk_input.merge(file_trends[["path"] + file_trend_cols], on="path", how="left")

    module_trend_cols = [
        c
        for c in ["churn_acceleration", "recent_churn_slope", "churn_spike_score"]
        if c in module_trends.columns
    ]
    if module_trend_cols:
        module_risk_input = module_risk_input.merge(
            module_trends[["module"] + module_trend_cols], on="module", how="left"
        )

    if len(file_churn_fc):
        file_fc_sum = file_churn_fc.groupby("path", dropna=False)["churn_yhat"].sum().reset_index(name="churn_yhat_sum_28d")
        file_risk_input = file_risk_input.merge(file_fc_sum, on="path", how="left")
        file_risk_input["churn_yhat_sum_56d"] = file_risk_input["churn_yhat_sum_28d"].astype(float) * 2.0

        accel = file_risk_input.get("churn_acceleration", 0.0)
        forecast_8w = file_risk_input["churn_yhat_sum_56d"].fillna(0.0)
        file_risk_input["state_after_4w"] = np.select(
            [
                (forecast_8w >= 2000) & (pd.to_numeric(accel, errors="coerce").fillna(0.0) > 0),
                (forecast_8w >= 2000),
                (forecast_8w >= 500) & (pd.to_numeric(accel, errors="coerce").fillna(0.0) > 0),
                (forecast_8w >= 500),
            ],
            ["hot spot", "high churn", "warming up", "active"],
            default="stable",
        )

    if len(module_churn_fc):
        mod_fc_sum = module_churn_fc.groupby("module", dropna=False)["churn_yhat"].sum().reset_index(name="churn_yhat_sum_28d")
        module_risk_input = module_risk_input.merge(mod_fc_sum, on="module", how="left")
        module_risk_input["churn_yhat_sum_56d"] = module_risk_input["churn_yhat_sum_28d"].astype(float) * 2.0

        accel = module_risk_input.get("churn_acceleration", 0.0)
        forecast_8w = module_risk_input["churn_yhat_sum_56d"].fillna(0.0)
        module_risk_input["state_after_4w"] = np.select(
            [
                (forecast_8w >= 2000) & (pd.to_numeric(accel, errors="coerce").fillna(0.0) > 0),
                (forecast_8w >= 2000),
                (forecast_8w >= 500) & (pd.to_numeric(accel, errors="coerce").fillna(0.0) > 0),
                (forecast_8w >= 500),
            ],
            ["hot spot", "high churn", "warming up", "active"],
            default="stable",
        )

    file_risk = score_risk(file_risk_input, weights=weights)
    module_risk = score_risk(module_risk_input, weights=weights)

    file_risk = add_explanations(file_risk)
    module_risk = add_explanations(module_risk)

    # Overlay tags are stored on the risk input frames; carry them into a
    # classifier list for report consumption.
    file_risk["classifier"] = file_risk.apply(
        lambda r: merge_classifier_tags(str(r.get("cluster_label", "") or ""), r.get("overlay_tags", []) or []),
        axis=1,
    )
    module_risk["classifier"] = module_risk.apply(
        lambda r: merge_classifier_tags(str(r.get("cluster_label", "") or ""), r.get("overlay_tags", []) or []),
        axis=1,
    )

    # Make signal labels friendlier for both the report AND the exported model.
    file_risk["classifier"] = file_risk["classifier"].apply(humanize_signals)
    module_risk["classifier"] = module_risk["classifier"].apply(humanize_signals)

    file_risk = file_risk.sort_values("risk_score", ascending=False).reset_index(drop=True)
    module_risk = module_risk.sort_values("risk_score", ascending=False).reset_index(drop=True)

    if len(file_risk) and "risk_score" in file_risk.columns:
        log(
            "File risk score range: "
            f"min={float(pd.to_numeric(file_risk['risk_score'], errors='coerce').min()):.3f}, "
            f"max={float(pd.to_numeric(file_risk['risk_score'], errors='coerce').max()):.3f}"
        )
    if len(module_risk) and "risk_score" in module_risk.columns:
        log(
            "Module risk score range: "
            f"min={float(pd.to_numeric(module_risk['risk_score'], errors='coerce').min()):.3f}, "
            f"max={float(pd.to_numeric(module_risk['risk_score'], errors='coerce').max()):.3f}"
        )

    file_risk.to_csv(out_dir / "file_risk.csv", index=False)
    module_risk.to_csv(out_dir / "module_risk.csv", index=False)

    _write_snapshots(out_dir=out_dir, file_risk=file_risk, module_risk=module_risk, file_metrics=file_metrics, module_metrics=module_metrics)
    log("Wrote snapshot CSVs: file_snapshot.csv + module_snapshot.csv")

    report = _build_report_model(
        repo_path=repo_path,
        repo_url=repo_url,
        commits_df=commits_df,
        file_metrics=file_metrics,
        module_metrics=module_metrics,
        file_trends=file_trends,
        module_trends=module_trends,
        file_churn_fc=file_churn_fc,
        module_churn_fc=module_churn_fc,
        file_risk=file_risk,
        module_risk=module_risk,
        weights=weights,
        max_commits_arg=max_commits,
        k=k,
        seed=seed,
        top_n=top_n,
    )

    log(
        "Built report model: "
        f"upcoming_pain_rows={len(report.upcoming_pain)}, top_hotspots_rows={len(report.top_hotspots)}"
    )

    return report


def _write_snapshots(*, out_dir: Path, file_risk: pd.DataFrame, module_risk: pd.DataFrame, file_metrics: pd.DataFrame, module_metrics: pd.DataFrame) -> None:
    file_snapshot = file_risk.copy()
    module_snapshot = module_risk.copy()

    snapshot_as_of_day = None
    if len(module_metrics) and "as_of_day" in module_metrics.columns:
        snapshot_as_of_day = module_metrics["as_of_day"].iloc[0]
    elif len(file_metrics) and "as_of_day" in file_metrics.columns:
        snapshot_as_of_day = file_metrics["as_of_day"].iloc[0]

    if snapshot_as_of_day is not None and "as_of_day" not in file_snapshot.columns:
        file_snapshot["as_of_day"] = snapshot_as_of_day
    if snapshot_as_of_day is not None and "as_of_day" not in module_snapshot.columns:
        module_snapshot["as_of_day"] = snapshot_as_of_day

    def _reorder_snapshot(df: pd.DataFrame, key_cols: list[str]) -> pd.DataFrame:
        preferred = (
            key_cols
            + ["as_of_day", "first_seen_day", "last_seen_day", "first_commit", "last_commit"]
            + ["why_risky_now", "why_risky_soon"]
            + ["risk_score", "cluster", "confidence", "cluster_label"]
            + [
                "churn",
                "commits",
                "contributors",
                "files_touched",
                "fix_commits",
                "fix_ratio",
                "additions",
                "deletions",
            ]
        )
        cols = [c for c in preferred if c in df.columns] + [c for c in df.columns if c not in preferred]
        return df[cols]

    file_snapshot = _reorder_snapshot(file_snapshot, ["path"])
    module_snapshot = _reorder_snapshot(module_snapshot, ["module"])

    file_snapshot.to_csv(out_dir / "file_snapshot.csv", index=False)
    module_snapshot.to_csv(out_dir / "module_snapshot.csv", index=False)


def _build_report_model(
    *,
    repo_path: Path,
    repo_url: Optional[str],
    commits_df: pd.DataFrame,
    file_metrics: pd.DataFrame,
    module_metrics: pd.DataFrame,
    file_trends: pd.DataFrame,
    module_trends: pd.DataFrame,
    file_churn_fc: pd.DataFrame,
    module_churn_fc: pd.DataFrame,
    file_risk: pd.DataFrame,
    module_risk: pd.DataFrame,
    weights: RiskWeights,
    max_commits_arg: Optional[int],
    k: int,
    seed: int,
    top_n: int,
) -> ReportModel:
    as_of_day = None
    if len(module_metrics) and "as_of_day" in module_metrics.columns:
        as_of_day = module_metrics["as_of_day"].iloc[0]
    elif len(file_metrics) and "as_of_day" in file_metrics.columns:
        as_of_day = file_metrics["as_of_day"].iloc[0]

    as_of_day_str = None
    if as_of_day is not None and str(as_of_day) != "NaT":
        as_of_day_str = str(as_of_day)[:10]

    meta = ReportMeta(
        repo_path=str(repo_path),
        repo_url=repo_url,
        scanned_commits=int(len(commits_df)),
        as_of_day_utc=as_of_day_str,
        max_commits_arg=max_commits_arg,
        k=k,
        seed=seed,
    )

    scoring = ScoringWeightsModel(
        churn=float(weights.churn),
        contributors=float(weights.contributors),
        fix_ratio=float(weights.fix_ratio),
        commits=float(weights.commits),
        churn_acceleration=float(weights.churn_acceleration),
        coupling=float(weights.coupling),
        ownership_concentration=float(weights.ownership_concentration),
        revert_ratio=float(weights.revert_ratio),
        fix_follow_ratio=float(weights.fix_follow_ratio),
        ownership_churn=float(weights.ownership_churn),
    )

    upcoming_pain: list[UpcomingPainRow] = []

    if len(module_churn_fc):
        mod_fc_sum = module_churn_fc.groupby("module", dropna=False)["churn_yhat"].sum().reset_index(name="churn_yhat_sum")
        mod_pain = mod_fc_sum.merge(
            module_trends[
                [
                    "module",
                    "recent_churn_slope",
                    "churn_spike_score",
                    "churn_acceleration",
                    "recent_churn_mean",
                    "baseline_churn_mean",
                    "recent_commits_mean",
                    "baseline_commits_mean",
                    "recent_contributors_mean",
                    "baseline_contributors_mean",
                ]
            ],
            on="module",
            how="left",
        )

        mod_pain = mod_pain.rename(
            columns={
                "recent_churn_mean": "recent_churn",
                "baseline_churn_mean": "baseline_churn",
                "recent_commits_mean": "recent_commits",
                "baseline_commits_mean": "baseline_commits",
                "recent_contributors_mean": "recent_contributors",
                "baseline_contributors_mean": "baseline_contributors",
            }
        )
        for metric in ["churn", "commits", "contributors"]:
            col = f"recent_{metric}"
            if col in mod_pain.columns:
                mod_pain[f"{metric}_28d"] = pd.to_numeric(mod_pain[col], errors="coerce").fillna(0.0) * 28.0

    mod_pain = mod_pain.merge(module_risk[["module", "cluster_label", "classifier", "risk_score"]], on="module", how="left")
    mod_pain = add_explanations(mod_pain.rename(columns={"churn_yhat_sum": "churn_yhat_sum_28d"}))
    mod_pain = mod_pain.rename(columns={"churn_yhat_sum_28d": "churn_yhat_sum"})

    mod_pain["forecast_56d_churn"] = mod_pain["churn_yhat_sum"].fillna(0.0) * 2.0
    accel = pd.to_numeric(mod_pain.get("churn_acceleration", 0.0), errors="coerce").fillna(0.0)
    forecast_8w = mod_pain["forecast_56d_churn"].fillna(0.0)
    mod_pain["state_after_4w"] = np.select(
        [
            (forecast_8w >= 2000) & (accel > 0),
            (forecast_8w >= 2000),
            (forecast_8w >= 500) & (accel > 0),
            (forecast_8w >= 500) & (accel < 0),
            (forecast_8w >= 500),
        ],
        ["hot spot", "high churn", "warming up", "cooling down", "active"],
        default="stable",
    )
    mod_pain["pain_score"] = (
        mod_pain["churn_yhat_sum"].fillna(0.0)
        + 7.0 * mod_pain["recent_churn_slope"].fillna(0.0)
        + 14.0 * mod_pain["churn_acceleration"].clip(lower=0.0).fillna(0.0)
        + 100.0 * mod_pain["churn_spike_score"].fillna(0.0)
    )

    mod_pain = mod_pain[mod_pain["state_after_4w"].fillna("") != "stable"]
    mod_pain = mod_pain.sort_values("pain_score", ascending=False).head(top_n)

    for _, r in mod_pain.iterrows():
        upcoming_pain.append(
                UpcomingPainRow(
                    kind="module",
                    name=str(r.get("module", "") or ""),
                    classifier=_as_str_list(r.get("classifier", r.get("cluster_label", ""))),
                    risk=float(r["risk_score"]) if pd.notna(r.get("risk_score")) else None,
                    state_after_4w=str(r.get("state_after_4w", "") or ""),
                    why_soon=_as_str_list(r.get("why_risky_soon", "")),
                )
            )

    if len(file_churn_fc):
        file_fc_sum = file_churn_fc.groupby("path", dropna=False)["churn_yhat"].sum().reset_index(name="churn_yhat_sum")
        file_pain = file_fc_sum.merge(
            file_trends[
                [
                    "path",
                    "recent_churn_slope",
                    "churn_spike_score",
                    "churn_acceleration",
                    "recent_churn_mean",
                    "baseline_churn_mean",
                    "recent_commits_mean",
                    "baseline_commits_mean",
                    "recent_contributors_mean",
                    "baseline_contributors_mean",
                ]
            ],
            on="path",
            how="left",
        )

        file_pain = file_pain.rename(
            columns={
                "recent_churn_mean": "recent_churn",
                "baseline_churn_mean": "baseline_churn",
                "recent_commits_mean": "recent_commits",
                "baseline_commits_mean": "baseline_commits",
                "recent_contributors_mean": "recent_contributors",
                "baseline_contributors_mean": "baseline_contributors",
            }
        )
        for metric in ["churn", "commits", "contributors"]:
            col = f"recent_{metric}"
            if col in file_pain.columns:
                file_pain[f"{metric}_28d"] = pd.to_numeric(file_pain[col], errors="coerce").fillna(0.0) * 28.0

    file_pain = file_pain.merge(file_risk[["path", "cluster_label", "classifier", "risk_score"]], on="path", how="left")
    file_pain = add_explanations(file_pain.rename(columns={"churn_yhat_sum": "churn_yhat_sum_28d"}))
    file_pain = file_pain.rename(columns={"churn_yhat_sum_28d": "churn_yhat_sum"})

    file_pain["forecast_56d_churn"] = file_pain["churn_yhat_sum"].fillna(0.0) * 2.0
    accel = pd.to_numeric(file_pain.get("churn_acceleration", 0.0), errors="coerce").fillna(0.0)
    forecast_8w = file_pain["forecast_56d_churn"].fillna(0.0)
    file_pain["state_after_4w"] = np.select(
        [
            (forecast_8w >= 2000) & (accel > 0),
            (forecast_8w >= 2000),
            (forecast_8w >= 500) & (accel > 0),
            (forecast_8w >= 500) & (accel < 0),
            (forecast_8w >= 500),
        ],
        ["hot spot", "high churn", "warming up", "cooling down", "active"],
        default="stable",
    )
    file_pain["pain_score"] = (
        file_pain["churn_yhat_sum"].fillna(0.0)
        + 7.0 * file_pain["recent_churn_slope"].fillna(0.0)
        + 14.0 * file_pain["churn_acceleration"].clip(lower=0.0).fillna(0.0)
        + 100.0 * file_pain["churn_spike_score"].fillna(0.0)
    )

    file_pain = file_pain[file_pain["state_after_4w"].fillna("") != "stable"]
    file_pain = file_pain.sort_values("pain_score", ascending=False).head(top_n)

    for _, r in file_pain.iterrows():
        upcoming_pain.append(
                UpcomingPainRow(
                    kind="file",
                    name=str(r.get("path", "") or ""),
                    classifier=_as_str_list(r.get("classifier", r.get("cluster_label", ""))),
                    risk=float(r["risk_score"]) if pd.notna(r.get("risk_score")) else None,
                    state_after_4w=str(r.get("state_after_4w", "") or ""),
                    why_soon=_as_str_list(r.get("why_risky_soon", "")),
                )
            )

    top_risky: list[TopRiskRow] = []
    for _, r in module_risk.head(top_n).iterrows():
        top_risky.append(
            TopRiskRow(
                kind="module",
                name=str(r.get("module", "") or ""),
                classifier=_as_str_list(r.get("classifier", r.get("cluster_label", ""))),
                risk=float(r["risk_score"]),
                why_now=_as_str_list(r.get("why_risky_now", "")),
            )
        )

    for _, r in file_risk.head(top_n).iterrows():
        top_risky.append(
            TopRiskRow(
                kind="file",
                name=str(r.get("path", "") or ""),
                classifier=_as_str_list(r.get("classifier", r.get("cluster_label", ""))),
                risk=float(r["risk_score"]),
                why_now=_as_str_list(r.get("why_risky_now", "")),
            )
        )

    # Big-picture grouping: cluster top risky items by signal.
    # This is intentionally lightweight (no ML dependency) and deterministic.
    def _clusters_for(kind: str) -> list[RiskCluster]:
        rows = [r for r in top_risky if r.kind == kind]
        if not rows:
            return []

        # Title-case group labels are already applied later in renderers.
        # Here we keep the raw signal strings to be renderer-agnostic.
        counts: dict[str, int] = {}
        examples: dict[str, list[str]] = {}
        for r in rows:
            sigs = list(r.classifier or [])
            if not sigs:
                sigs = ["unclassified"]
            for s in sigs:
                key = str(s).strip() or "unclassified"
                counts[key] = counts.get(key, 0) + 1
                examples.setdefault(key, [])
                if len(examples[key]) < 3:
                    examples[key].append(r.name)

        ordered = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0].lower()))
        return [RiskCluster(signal=signal, count=n, examples=examples.get(signal, [])) for signal, n in ordered]

    risk_clusters = RiskClustersOverview(modules=_clusters_for("module"), files=_clusters_for("file"))

    # Clustered view of `top_risky`: clusters with members inside.
    #
    # Design goals:
    # - Stable cluster ids between runs (for the same inputs)
    # - Preserve the global top_risky ranking order inside each cluster
    # - Avoid hard ML deps for now; treat clusters as 'primary signal buckets'
    def _primary_signal(classifier: list[str]) -> str:
        sigs = [str(s).strip() for s in (classifier or []) if str(s).strip()]
        # Deterministic: prefer earliest signal in the classifier list.
        return sigs[0] if sigs else "unclassified"

    def _compute_top_risky_clustered() -> list[TopRiskCluster]:
        # rank is 1-based within the global list; we keep this around for display.
        indexed = [(i + 1, r) for i, r in enumerate(top_risky)]

        # kind -> primary_signal -> members
        buckets: dict[tuple[str, str], list[TopRiskClusterMember]] = {}
        for rank, r in indexed:
            key = (r.kind, _primary_signal(r.classifier))
            buckets.setdefault(key, []).append(
                TopRiskClusterMember(
                    rank=rank,
                    kind=r.kind,
                    name=r.name,
                    classifier=list(r.classifier or []),
                    risk=float(r.risk),
                    why_now=list(r.why_now or []),
                )
            )

        # Stable-ish ids: "{kind}:{signal}" (slugged)
        def _slug(s: str) -> str:
            out = []
            for ch in str(s).strip().lower():
                if ch.isalnum():
                    out.append(ch)
                elif ch in [" ", "-", "_", ".", "/", ":"]:
                    out.append("-")
            slug = "".join(out)
            while "--" in slug:
                slug = slug.replace("--", "-")
            return slug.strip("-") or "unclassified"

        clusters: list[TopRiskCluster] = []
        for (kind, signal), members in buckets.items():
            # Members are already in global rank order due to iteration order.
            cid = f"{kind}:{_slug(signal)}"
            clusters.append(
                TopRiskCluster(
                    cluster_id=cid,
                    kind=kind,  # type: ignore[arg-type]
                    label=signal,
                    count=len(members),
                    members=members,
                )
            )

        # Order clusters by: severity proxy (min rank), then size desc, then label.
        def _cluster_sort_key(c: TopRiskCluster) -> tuple[int, int, str]:
            min_rank = min((m.rank for m in c.members), default=10**9)
            return (min_rank, -int(c.count), str(c.label).lower())

        clusters.sort(key=_cluster_sort_key)
        return clusters

    top_risky_clustered = _compute_top_risky_clustered()

    return ReportModel(
        meta=meta,
        scoring_weights=scoring,
        upcoming_pain=upcoming_pain,
        top_hotspots=top_risky,
        risk_clusters=risk_clusters,
        top_risky_clustered=top_risky_clustered,
    )
