from __future__ import annotations

from pathlib import PurePosixPath
from typing import Dict, Iterable, Tuple

import pandas as pd


def _module_of_path(path: str) -> str:
    p = PurePosixPath(path)
    if len(p.parts) <= 1:
        return "."
    return str(PurePosixPath(*p.parts[:-1]))


def add_module_column(file_changes_df: pd.DataFrame) -> pd.DataFrame:
    df = file_changes_df.copy()
    df["module"] = df["path"].map(_module_of_path)
    return df


def _herfindahl(shares: Iterable[float]) -> float:
    """Herfindahl index (0..1) used as a lightweight concentration metric."""

    s = 0.0
    for x in shares:
        try:
            v = float(x)
        except Exception:
            v = 0.0
        s += v * v
    return float(s)


def compute_file_ownership_metrics(commits_df: pd.DataFrame, file_changes_df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-file ownership concentration metrics.

    Output columns:
      - path
      - top_author_share: fraction of commits authored by top contributor (0..1)
      - ownership_hhi: Herfindahl index over author commit shares (0..1)
    """

    if commits_df.empty or file_changes_df.empty:
        return pd.DataFrame(columns=["path", "top_author_share", "ownership_hhi"])

    joined = file_changes_df.merge(commits_df[["sha", "author_email"]], on="sha", how="left")
    # per (path, author) commit counts
    counts = (
        joined[["path", "author_email", "sha"]]
        .dropna(subset=["path", "sha"])
        .drop_duplicates()
        .groupby(["path", "author_email"], dropna=False)["sha"]
        .nunique()
        .reset_index(name="author_commits")
    )

    totals = counts.groupby("path", dropna=False)["author_commits"].sum().reset_index(name="total_commits")
    merged = counts.merge(totals, on="path", how="left")
    merged["share"] = (merged["author_commits"] / merged["total_commits"]).fillna(0.0)

    top_share = merged.groupby("path", dropna=False)["share"].max().reset_index(name="top_author_share")

    hhi = (
        merged.groupby("path", dropna=False)["share"]
        .apply(lambda s: _herfindahl(s.to_list()))
        .reset_index(name="ownership_hhi")
    )

    out = top_share.merge(hhi, on="path", how="left")
    return out


def compute_module_ownership_metrics(commits_df: pd.DataFrame, file_changes_df: pd.DataFrame) -> pd.DataFrame:
    """Compute per-module ownership concentration metrics."""

    if commits_df.empty or file_changes_df.empty:
        return pd.DataFrame(columns=["module", "top_author_share", "ownership_hhi"])

    df = add_module_column(file_changes_df)
    joined = df.merge(commits_df[["sha", "author_email"]], on="sha", how="left")

    counts = (
        joined[["module", "author_email", "sha"]]
        .dropna(subset=["module", "sha"])
        .drop_duplicates()
        .groupby(["module", "author_email"], dropna=False)["sha"]
        .nunique()
        .reset_index(name="author_commits")
    )

    totals = counts.groupby("module", dropna=False)["author_commits"].sum().reset_index(name="total_commits")
    merged = counts.merge(totals, on="module", how="left")
    merged["share"] = (merged["author_commits"] / merged["total_commits"]).fillna(0.0)

    top_share = merged.groupby("module", dropna=False)["share"].max().reset_index(name="top_author_share")
    hhi = (
        merged.groupby("module", dropna=False)["share"]
        .apply(lambda s: _herfindahl(s.to_list()))
        .reset_index(name="ownership_hhi")
    )

    out = top_share.merge(hhi, on="module", how="left")
    return out


def compute_commit_cochange_pairs(
    file_changes_df: pd.DataFrame,
    *,
    entity_col: str,
) -> pd.DataFrame:
    """Compute undirected co-change pairs from a commit→{entities} mapping.

    Returns columns: a, b, cochange_commits

    Notes:
      - entity_col can be "path" (file coupling) or "module" (module coupling)
      - Uses O(n^2) within each commit; acceptable for typical repo sizes, but can
        get heavy for enormous commits. We cap per-commit entity fanout.
    """

    if file_changes_df.empty or "sha" not in file_changes_df.columns or entity_col not in file_changes_df.columns:
        return pd.DataFrame(columns=["a", "b", "cochange_commits"])

    pairs: Dict[Tuple[str, str], int] = {}
    # Fanout cap: beyond this, coupling becomes noisy and expensive.
    FANOUT_CAP = 80

    for sha, sub in file_changes_df[["sha", entity_col]].dropna().drop_duplicates().groupby("sha", dropna=False):
        entities = sorted(str(x) for x in sub[entity_col].dropna().unique())
        if len(entities) < 2:
            continue
        if len(entities) > FANOUT_CAP:
            entities = entities[:FANOUT_CAP]
        for i in range(len(entities)):
            for j in range(i + 1, len(entities)):
                a, b = entities[i], entities[j]
                pairs[(a, b)] = pairs.get((a, b), 0) + 1

    if not pairs:
        return pd.DataFrame(columns=["a", "b", "cochange_commits"])

    out = pd.DataFrame(
        [(a, b, n) for (a, b), n in pairs.items()],
        columns=["a", "b", "cochange_commits"],
    )
    return out


def compute_entity_coupling_summary(
    pairs_df: pd.DataFrame,
    *,
    entity_col: str,
    top_k: int = 3,
) -> pd.DataFrame:
    """Summarize coupling graph into per-entity stats.

    Output columns:
      - entity_col (entity id)
      - coupling_degree: number of distinct coupled entities
      - coupling_strength_sum: total cochange commits across edges
      - top_coupled_entities: comma-separated list of top-k coupled entity names
    """

    if pairs_df.empty:
        return pd.DataFrame(columns=[entity_col, "coupling_degree", "coupling_strength_sum", "top_coupled_entities"])

    df = pairs_df.copy()
    df["a"] = df["a"].astype(str)
    df["b"] = df["b"].astype(str)
    df["cochange_commits"] = pd.to_numeric(df["cochange_commits"], errors="coerce").fillna(0).astype(int)

    # Build per-node edge list by duplicating undirected edges.
    edges = pd.concat(
        [
            df.rename(columns={"a": entity_col, "b": "other"}),
            df.rename(columns={"b": entity_col, "a": "other"}),
        ],
        ignore_index=True,
    )

    degree = edges.groupby(entity_col, dropna=False)["other"].nunique().reset_index(name="coupling_degree")
    strength = edges.groupby(entity_col, dropna=False)["cochange_commits"].sum().reset_index(name="coupling_strength_sum")

    def _top_list(sub: pd.DataFrame) -> str:
        sub = sub.sort_values(["cochange_commits", "other"], ascending=[False, True])
        return ", ".join(sub["other"].head(top_k).astype(str).tolist())

    # Avoid pandas FutureWarning about GroupBy.apply operating on grouping columns.
    # We only need the non-grouping columns inside the apply.
    top = (
        edges.groupby(entity_col, dropna=False)[["other", "cochange_commits"]]
        .apply(_top_list)
        .reset_index(name="top_coupled_entities")
    )
    out = degree.merge(strength, on=entity_col, how="outer").merge(top, on=entity_col, how="outer")
    return out


def compute_revert_metrics(commits_df: pd.DataFrame, file_changes_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute simple revert-rate metrics for files and modules.

    Heuristic: commit subject starts with "revert" (case-insensitive).

    Returns: (file_reverts_df, module_reverts_df)
      - file_reverts_df columns: path, revert_commits, revert_ratio
      - module_reverts_df columns: module, revert_commits, revert_ratio
    """

    if commits_df.empty or file_changes_df.empty:
        return (
            pd.DataFrame(columns=["path", "revert_commits", "revert_ratio"]),
            pd.DataFrame(columns=["module", "revert_commits", "revert_ratio"]),
        )

    dfc = commits_df[["sha", "message"]].copy()
    dfc["message"] = dfc["message"].fillna("").astype(str)
    dfc["is_revert"] = dfc["message"].str.strip().str.lower().str.startswith("revert")
    revert_shas = set(dfc.loc[dfc["is_revert"], "sha"].astype(str).tolist())

    if not revert_shas:
        return (
            pd.DataFrame(columns=["path", "revert_commits", "revert_ratio"]),
            pd.DataFrame(columns=["module", "revert_commits", "revert_ratio"]),
        )

    joined = file_changes_df[["sha", "path"]].dropna().drop_duplicates()
    joined["is_revert"] = joined["sha"].astype(str).isin(revert_shas)

    file_total = joined.groupby("path", dropna=False)["sha"].nunique().reset_index(name="commits_total")
    file_reverts = (
        joined.loc[joined["is_revert"], ["path", "sha"]]
        .drop_duplicates()
        .groupby("path", dropna=False)["sha"]
        .nunique()
        .reset_index(name="revert_commits")
    )
    file_out = file_total.merge(file_reverts, on="path", how="left")
    file_out["revert_commits"] = file_out["revert_commits"].fillna(0).astype(int)
    file_out["revert_ratio"] = (file_out["revert_commits"] / file_out["commits_total"]).fillna(0.0)
    file_out = file_out[["path", "revert_commits", "revert_ratio"]]

    joined_m = joined.copy()
    joined_m["module"] = joined_m["path"].map(_module_of_path)
    mod_total = joined_m.groupby("module", dropna=False)["sha"].nunique().reset_index(name="commits_total")
    mod_reverts = (
        joined_m.loc[joined_m["is_revert"], ["module", "sha"]]
        .drop_duplicates()
        .groupby("module", dropna=False)["sha"]
        .nunique()
        .reset_index(name="revert_commits")
    )
    mod_out = mod_total.merge(mod_reverts, on="module", how="left")
    mod_out["revert_commits"] = mod_out["revert_commits"].fillna(0).astype(int)
    mod_out["revert_ratio"] = (mod_out["revert_commits"] / mod_out["commits_total"]).fillna(0.0)
    mod_out = mod_out[["module", "revert_commits", "revert_ratio"]]

    return file_out, mod_out


def compute_fix_follow_metrics(
    commits_df: pd.DataFrame,
    file_changes_df: pd.DataFrame,
    *,
    follow_days: int = 7,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute "fix-follow" density per file/module.

    Idea: areas where fixes frequently land soon after changes tend to stay risky
    into the next sprint.

    Definition (per entity):
      - consider a "fix commit" any commit with commit_type == "fix"
      - a fix commit counts as "follow-up" if there was at least one *non-fix*
        commit touching the same entity within `follow_days` before the fix.

    Output (file/module):
      - entity id (path/module)
      - fix_commits
      - fix_follow_commits
      - fix_follow_ratio = fix_follow_commits / max(fix_commits, 1)
      - fix_follow_days (echo)
    """

    if commits_df.empty or file_changes_df.empty:
        empty_f = pd.DataFrame(
            columns=["path", "fix_commits", "fix_follow_commits", "fix_follow_ratio", "fix_follow_days"]
        )
        empty_m = pd.DataFrame(
            columns=["module", "fix_commits", "fix_follow_commits", "fix_follow_ratio", "fix_follow_days"]
        )
        return empty_f, empty_m

    c = commits_df[["sha", "committed_datetime", "commit_type"]].copy()
    c["committed_datetime"] = pd.to_datetime(c["committed_datetime"], utc=True, errors="coerce")
    c["commit_type"] = c["commit_type"].fillna("").astype(str)

    joined = file_changes_df[["sha", "path"]].dropna().drop_duplicates().merge(c, on="sha", how="left")
    joined = joined.dropna(subset=["committed_datetime"])
    joined = joined.sort_values(["path", "committed_datetime", "sha"]).reset_index(drop=True)

    # Prepare module view.
    joined_m = joined.copy()
    joined_m["module"] = joined_m["path"].map(_module_of_path)

    def _compute(df: pd.DataFrame, *, entity_col: str) -> pd.DataFrame:
        rows = []
        window = pd.Timedelta(days=int(follow_days))
        for ent, sub in df.groupby(entity_col, dropna=False):
            sub = sub.sort_values(["committed_datetime", "sha"])
            fix_shas = sub.loc[sub["commit_type"] == "fix", "sha"].astype(str).tolist()
            if not fix_shas:
                rows.append(
                    {
                        entity_col: ent,
                        "fix_commits": 0,
                        "fix_follow_commits": 0,
                        "fix_follow_ratio": 0.0,
                        "fix_follow_days": int(follow_days),
                    }
                )
                continue

            fix_follow = 0
            for sha in fix_shas:
                t_fix = sub.loc[sub["sha"] == sha, "committed_datetime"].iloc[0]
                t0 = t_fix - window
                prev = sub[(sub["committed_datetime"] < t_fix) & (sub["committed_datetime"] >= t0)]
                if (prev["commit_type"] != "fix").any():
                    fix_follow += 1

            fix_n = int(len(fix_shas))
            rows.append(
                {
                    entity_col: ent,
                    "fix_commits": fix_n,
                    "fix_follow_commits": int(fix_follow),
                    "fix_follow_ratio": float(fix_follow) / float(max(1, fix_n)),
                    "fix_follow_days": int(follow_days),
                }
            )

        return pd.DataFrame(rows)

    file_out = _compute(joined, entity_col="path")
    mod_out = _compute(joined_m, entity_col="module")
    return file_out, mod_out


def compute_ownership_churn_metrics(
    commits_df: pd.DataFrame,
    file_changes_df: pd.DataFrame,
    *,
    recent_days: int = 28,
    baseline_days: int = 90,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compute ownership churn / contributor turnover for files and modules.

    Metrics are intended to predict near-future maintainability + delivery risk.

    For each entity, based on commits in the trailing window ending at as_of_day:
      - recent_top_author_share
      - baseline_top_author_share
      - delta_top_author_share = recent - baseline
      - recent_contributors
      - baseline_contributors
      - new_contributors: contributors in recent but not in baseline
      - lost_contributors: contributors in baseline but not in recent

    Notes:
      - baseline window is trailing (as_of_day - baseline_days + 1 .. as_of_day)
      - recent window is trailing (as_of_day - recent_days + 1 .. as_of_day)
      - baseline set uses the *baseline window excluding recent* for turnover comparison
        to make “new/lost” meaningful.
    """

    if commits_df.empty or file_changes_df.empty:
        empty_f = pd.DataFrame(
            columns=[
                "path",
                "recent_top_author_share",
                "baseline_top_author_share",
                "delta_top_author_share",
                "recent_contributors",
                "baseline_contributors",
                "new_contributors",
                "lost_contributors",
                "ownership_recent_days",
                "ownership_baseline_days",
            ]
        )
        empty_m = empty_f.rename(columns={"path": "module"})
        return empty_f, empty_m

    c = commits_df[["sha", "author_email", "committed_datetime"]].copy()
    c["committed_datetime"] = pd.to_datetime(c["committed_datetime"], utc=True, errors="coerce")
    c = c.dropna(subset=["sha", "committed_datetime"])
    as_of_day = c["committed_datetime"].max().normalize()

    recent_start = as_of_day - pd.Timedelta(days=int(recent_days) - 1)
    baseline_start = as_of_day - pd.Timedelta(days=int(baseline_days) - 1)
    # for turnover baseline set, exclude recent window
    turnover_end = recent_start - pd.Timedelta(days=1)

    joined = file_changes_df[["sha", "path"]].dropna().drop_duplicates().merge(c, on="sha", how="left")
    joined = joined.dropna(subset=["committed_datetime"])

    def _compute(df: pd.DataFrame, *, entity_col: str) -> pd.DataFrame:
        rows = []
        for ent, sub in df.groupby(entity_col, dropna=False):
            sub = sub.sort_values(["committed_datetime", "sha"])

            recent = sub[sub["committed_datetime"] >= recent_start]
            baseline = sub[sub["committed_datetime"] >= baseline_start]
            turnover_base = sub[(sub["committed_datetime"] >= baseline_start) & (sub["committed_datetime"] <= turnover_end)]

            def top_share(s: pd.DataFrame) -> float:
                if s.empty:
                    return 0.0
                per_author = (
                    s[["author_email", "sha"]]
                    .dropna()
                    .drop_duplicates()
                    .groupby("author_email", dropna=False)["sha"]
                    .nunique()
                )
                total = float(per_author.sum()) if len(per_author) else 0.0
                if total <= 0:
                    return 0.0
                return float(per_author.max()) / total

            recent_share = top_share(recent)
            baseline_share = top_share(baseline)

            recent_auth = set(recent["author_email"].dropna().astype(str).unique().tolist())
            base_auth = set(turnover_base["author_email"].dropna().astype(str).unique().tolist())

            rows.append(
                {
                    entity_col: ent,
                    "recent_top_author_share": float(recent_share),
                    "baseline_top_author_share": float(baseline_share),
                    "delta_top_author_share": float(recent_share - baseline_share),
                    "recent_contributors": int(len(recent_auth)),
                    "baseline_contributors": int(len(base_auth)),
                    "new_contributors": int(len(recent_auth - base_auth)),
                    "lost_contributors": int(len(base_auth - recent_auth)),
                    "ownership_recent_days": int(recent_days),
                    "ownership_baseline_days": int(baseline_days),
                }
            )

        return pd.DataFrame(rows)

    file_out = _compute(joined, entity_col="path")

    joined_m = joined.copy()
    joined_m["module"] = joined_m["path"].map(_module_of_path)
    mod_out = _compute(joined_m, entity_col="module")
    return file_out, mod_out


def compute_file_metrics(commits_df: pd.DataFrame, file_changes_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-file metrics.

    Expected inputs:
      commits_df columns: sha, author_email, committed_datetime, message
      file_changes_df columns: sha, path, additions, deletions
    """

    if commits_df.empty or file_changes_df.empty:
        return pd.DataFrame(
            columns=[
                "path",
                "commits",
                "contributors",
                "additions",
                "deletions",
                "churn",
                "fix_commits",
                "fix_ratio",
                "first_commit",
                "last_commit",
                "first_seen_day",
                "last_seen_day",
                "as_of_day",
            ]
        )

    # Join commit metadata onto file changes
    joined = file_changes_df.merge(
        commits_df[["sha", "author_email", "committed_datetime", "message", "commit_type"]],
        on="sha",
        how="left",
    )
    joined["churn"] = joined["additions"].fillna(0).astype(int) + joined["deletions"].fillna(0).astype(int)

    grouped = joined.groupby("path", dropna=False)

    fix_commits = (
        joined.loc[joined["commit_type"] == "fix", ["path", "sha"]]
        .drop_duplicates()
        .groupby("path")["sha"]
        .nunique()
    )

    out = pd.DataFrame(
        {
            "path": grouped.size().index,
            "commits": grouped["sha"].nunique().values,
            "contributors": grouped["author_email"].nunique().values,
            "additions": grouped["additions"].sum().values,
            "deletions": grouped["deletions"].sum().values,
            "churn": grouped["churn"].sum().values,
            "fix_commits": fix_commits.reindex(grouped.size().index).fillna(0).astype(int).values,
            "first_commit": grouped["committed_datetime"].min().values,
            "last_commit": grouped["committed_datetime"].max().values,
        }
    )

    # Ownership concentration (bus-factor proxy).
    ownership = compute_file_ownership_metrics(commits_df, file_changes_df)
    out = out.merge(ownership, on="path", how="left")

    # Normalize to UTC day buckets for easy date-to-date trend joins.
    out["first_commit"] = pd.to_datetime(out["first_commit"], utc=True)
    out["last_commit"] = pd.to_datetime(out["last_commit"], utc=True)
    out["first_seen_day"] = out["first_commit"].dt.normalize()
    out["last_seen_day"] = out["last_commit"].dt.normalize()
    out["as_of_day"] = out["last_seen_day"].max() if len(out) else pd.NaT

    out["fix_ratio"] = (out["fix_commits"] / out["commits"]).fillna(0.0)
    out = out.sort_values(["churn", "commits"], ascending=False).reset_index(drop=True)
    return out


def compute_module_metrics(commits_df: pd.DataFrame, file_changes_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per-module (directory) metrics."""

    if commits_df.empty or file_changes_df.empty:
        return pd.DataFrame(
            columns=[
                "module",
                "commits",
                "contributors",
                "files_touched",
                "additions",
                "deletions",
                "churn",
                "fix_commits",
                "fix_ratio",
                "first_commit",
                "last_commit",
                "first_seen_day",
                "last_seen_day",
                "as_of_day",
            ]
        )

    df = add_module_column(file_changes_df)
    joined = df.merge(
        commits_df[["sha", "author_email", "committed_datetime", "message", "commit_type"]],
        on="sha",
        how="left",
    )
    joined["churn"] = joined["additions"].fillna(0).astype(int) + joined["deletions"].fillna(0).astype(int)

    grouped = joined.groupby("module", dropna=False)

    fix_commits = (
        joined.loc[joined["commit_type"] == "fix", ["module", "sha"]]
        .drop_duplicates()
        .groupby("module")["sha"]
        .nunique()
    )

    out = pd.DataFrame(
        {
            "module": grouped.size().index,
            "commits": grouped["sha"].nunique().values,
            "contributors": grouped["author_email"].nunique().values,
            "files_touched": grouped["path"].nunique().values,
            "additions": grouped["additions"].sum().values,
            "deletions": grouped["deletions"].sum().values,
            "churn": grouped["churn"].sum().values,
            "fix_commits": fix_commits.reindex(grouped.size().index).fillna(0).astype(int).values,
            "first_commit": grouped["committed_datetime"].min().values,
            "last_commit": grouped["committed_datetime"].max().values,
        }
    )

    ownership = compute_module_ownership_metrics(commits_df, file_changes_df)
    out = out.merge(ownership, on="module", how="left")

    out["first_commit"] = pd.to_datetime(out["first_commit"], utc=True)
    out["last_commit"] = pd.to_datetime(out["last_commit"], utc=True)
    out["first_seen_day"] = out["first_commit"].dt.normalize()
    out["last_seen_day"] = out["last_commit"].dt.normalize()
    out["as_of_day"] = out["last_seen_day"].max() if len(out) else pd.NaT

    out["fix_ratio"] = (out["fix_commits"] / out["commits"]).fillna(0.0)
    out = out.sort_values(["churn", "commits"], ascending=False).reset_index(drop=True)
    return out


def compute_file_metrics_weekly(commits_df: pd.DataFrame, file_changes_df: pd.DataFrame) -> pd.DataFrame:
    """Weekly per-file metrics for trend analytics.

    Output columns include:
      - path
      - week_start (UTC, week anchored to Monday)
      - commits, contributors, additions, deletions, churn
      - fix_commits, fix_ratio
    """

    if commits_df.empty or file_changes_df.empty:
        return pd.DataFrame(
            columns=[
                "path",
                "week_start",
                "commits",
                "contributors",
                "additions",
                "deletions",
                "churn",
                "fix_commits",
                "fix_ratio",
            ]
        )

    joined = file_changes_df.merge(
        commits_df[["sha", "author_email", "committed_datetime", "commit_type"]],
        on="sha",
        how="left",
    )
    joined["committed_datetime"] = pd.to_datetime(joined["committed_datetime"], utc=True)
    # Week start anchored to Monday, UTC, without dropping tz.
    # We normalize to midnight and subtract the weekday offset.
    joined["week_start"] = (
        joined["committed_datetime"].dt.normalize()
        - pd.to_timedelta(joined["committed_datetime"].dt.weekday, unit="D")
    )
    joined["churn"] = joined["additions"].fillna(0).astype(int) + joined["deletions"].fillna(0).astype(int)

    key_cols = ["path", "week_start"]
    grouped = joined.groupby(key_cols, dropna=False)

    fix_commits = (
        joined.loc[joined["commit_type"] == "fix", key_cols + ["sha"]]
        .drop_duplicates()
        .groupby(key_cols)["sha"]
        .nunique()
    )

    out = grouped.agg(
        commits=("sha", "nunique"),
        contributors=("author_email", "nunique"),
        additions=("additions", "sum"),
        deletions=("deletions", "sum"),
        churn=("churn", "sum"),
    ).reset_index()

    out["fix_commits"] = fix_commits.reindex(pd.MultiIndex.from_frame(out[key_cols])).fillna(0).astype(int).values
    out["fix_ratio"] = (out["fix_commits"] / out["commits"]).fillna(0.0)
    out = out.sort_values(["path", "week_start"]).reset_index(drop=True)
    return out


def compute_module_metrics_weekly(commits_df: pd.DataFrame, file_changes_df: pd.DataFrame) -> pd.DataFrame:
    """Weekly per-module metrics for trend analytics."""

    if commits_df.empty or file_changes_df.empty:
        return pd.DataFrame(
            columns=[
                "module",
                "week_start",
                "commits",
                "contributors",
                "files_touched",
                "additions",
                "deletions",
                "churn",
                "fix_commits",
                "fix_ratio",
            ]
        )

    df = add_module_column(file_changes_df)
    joined = df.merge(
        commits_df[["sha", "author_email", "committed_datetime", "commit_type"]],
        on="sha",
        how="left",
    )
    joined["committed_datetime"] = pd.to_datetime(joined["committed_datetime"], utc=True)
    joined["week_start"] = (
        joined["committed_datetime"].dt.normalize()
        - pd.to_timedelta(joined["committed_datetime"].dt.weekday, unit="D")
    )
    joined["churn"] = joined["additions"].fillna(0).astype(int) + joined["deletions"].fillna(0).astype(int)

    key_cols = ["module", "week_start"]
    grouped = joined.groupby(key_cols, dropna=False)

    fix_commits = (
        joined.loc[joined["commit_type"] == "fix", key_cols + ["sha"]]
        .drop_duplicates()
        .groupby(key_cols)["sha"]
        .nunique()
    )

    out = grouped.agg(
        commits=("sha", "nunique"),
        contributors=("author_email", "nunique"),
        files_touched=("path", "nunique"),
        additions=("additions", "sum"),
        deletions=("deletions", "sum"),
        churn=("churn", "sum"),
    ).reset_index()

    out["fix_commits"] = fix_commits.reindex(pd.MultiIndex.from_frame(out[key_cols])).fillna(0).astype(int).values
    out["fix_ratio"] = (out["fix_commits"] / out["commits"]).fillna(0.0)
    out = out.sort_values(["module", "week_start"]).reset_index(drop=True)
    return out


def compute_file_metrics_daily(commits_df: pd.DataFrame, file_changes_df: pd.DataFrame) -> pd.DataFrame:
    """Daily per-file metrics for trend analytics (UTC day buckets)."""

    if commits_df.empty or file_changes_df.empty:
        return pd.DataFrame(
            columns=[
                "path",
                "day_start",
                "commits",
                "contributors",
                "additions",
                "deletions",
                "churn",
                "fix_commits",
                "fix_ratio",
            ]
        )

    joined = file_changes_df.merge(
        commits_df[["sha", "author_email", "committed_datetime", "commit_type"]],
        on="sha",
        how="left",
    )
    joined["committed_datetime"] = pd.to_datetime(joined["committed_datetime"], utc=True)
    joined["day_start"] = joined["committed_datetime"].dt.normalize()
    joined["churn"] = joined["additions"].fillna(0).astype(int) + joined["deletions"].fillna(0).astype(int)

    key_cols = ["path", "day_start"]
    grouped = joined.groupby(key_cols, dropna=False)

    fix_commits = (
        joined.loc[joined["commit_type"] == "fix", key_cols + ["sha"]]
        .drop_duplicates()
        .groupby(key_cols)["sha"]
        .nunique()
    )

    out = grouped.agg(
        commits=("sha", "nunique"),
        contributors=("author_email", "nunique"),
        additions=("additions", "sum"),
        deletions=("deletions", "sum"),
        churn=("churn", "sum"),
    ).reset_index()

    out["fix_commits"] = fix_commits.reindex(pd.MultiIndex.from_frame(out[key_cols])).fillna(0).astype(int).values
    out["fix_ratio"] = (out["fix_commits"] / out["commits"]).fillna(0.0)
    out = out.sort_values(["path", "day_start"]).reset_index(drop=True)
    return out


def compute_module_metrics_daily(commits_df: pd.DataFrame, file_changes_df: pd.DataFrame) -> pd.DataFrame:
    """Daily per-module metrics for trend analytics (UTC day buckets)."""

    if commits_df.empty or file_changes_df.empty:
        return pd.DataFrame(
            columns=[
                "module",
                "day_start",
                "commits",
                "contributors",
                "files_touched",
                "additions",
                "deletions",
                "churn",
                "fix_commits",
                "fix_ratio",
            ]
        )

    df = add_module_column(file_changes_df)
    joined = df.merge(
        commits_df[["sha", "author_email", "committed_datetime", "commit_type"]],
        on="sha",
        how="left",
    )
    joined["committed_datetime"] = pd.to_datetime(joined["committed_datetime"], utc=True)
    joined["day_start"] = joined["committed_datetime"].dt.normalize()
    joined["churn"] = joined["additions"].fillna(0).astype(int) + joined["deletions"].fillna(0).astype(int)

    key_cols = ["module", "day_start"]
    grouped = joined.groupby(key_cols, dropna=False)

    fix_commits = (
        joined.loc[joined["commit_type"] == "fix", key_cols + ["sha"]]
        .drop_duplicates()
        .groupby(key_cols)["sha"]
        .nunique()
    )

    out = grouped.agg(
        commits=("sha", "nunique"),
        contributors=("author_email", "nunique"),
        files_touched=("path", "nunique"),
        additions=("additions", "sum"),
        deletions=("deletions", "sum"),
        churn=("churn", "sum"),
    ).reset_index()

    out["fix_commits"] = fix_commits.reindex(pd.MultiIndex.from_frame(out[key_cols])).fillna(0).astype(int).values
    out["fix_ratio"] = (out["fix_commits"] / out["commits"]).fillna(0.0)
    out = out.sort_values(["module", "day_start"]).reset_index(drop=True)
    return out
