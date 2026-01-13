from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional

import pandas as pd
from git import Repo


@dataclass(frozen=True)
class CommitRecord:
    sha: str
    author_name: str
    author_email: str
    authored_datetime: datetime
    committed_datetime: datetime
    message: str


@dataclass(frozen=True)
class FileChangeRecord:
    sha: str
    path: str
    additions: int
    deletions: int


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def iter_commit_and_file_changes(
    repo_path: Path,
    *,
    max_commits: Optional[int] = None,
) -> tuple[List[CommitRecord], List[FileChangeRecord]]:
    """Extract commit metadata + per-file line stats.

    Notes:
      - Uses `commit.stats.files` from GitPython, which is fast and good for MVP.
      - Renames are not specially handled yet (future improvement).
    """

    repo = Repo(str(repo_path))
    if repo.bare:
        raise ValueError(f"Repository at {repo_path} is bare")

    commits: List[CommitRecord] = []
    changes: List[FileChangeRecord] = []

    n = 0
    for c in repo.iter_commits(rev="HEAD"):
        commits.append(
            CommitRecord(
                sha=c.hexsha,
                author_name=getattr(c.author, "name", "") or "",
                author_email=getattr(c.author, "email", "") or "",
                authored_datetime=_to_utc(c.authored_datetime),
                committed_datetime=_to_utc(c.committed_datetime),
                message=(c.message or "").strip(),
            )
        )

        stats = c.stats
        # stats.files keys are file paths as seen in the diff.
        for path, s in stats.files.items():
            changes.append(
                FileChangeRecord(
                    sha=c.hexsha,
                    path=path,
                    additions=int(s.get("insertions", 0) or 0),
                    deletions=int(s.get("deletions", 0) or 0),
                )
            )

        n += 1
        if max_commits is not None and n >= max_commits:
            break

    return commits, changes


def commits_to_df(commits: Iterable[CommitRecord]) -> pd.DataFrame:
    df = pd.DataFrame([asdict(c) for c in commits])
    if not df.empty:
        df["authored_datetime"] = pd.to_datetime(df["authored_datetime"], utc=True)
        df["committed_datetime"] = pd.to_datetime(df["committed_datetime"], utc=True)
    return df


def file_changes_to_df(changes: Iterable[FileChangeRecord]) -> pd.DataFrame:
    df = pd.DataFrame([asdict(ch) for ch in changes])
    return df
