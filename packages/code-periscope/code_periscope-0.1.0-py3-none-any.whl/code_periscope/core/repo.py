from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse

from typing import Optional

from git import InvalidGitRepositoryError, Repo


def detect_repo_url(repo_path: Path) -> Optional[str]:
    """Best-effort detection of a local repo's canonical URL.

    Heuristics:
    - Prefer remote named "origin".
    - Otherwise use the first configured remote.
    - Prefer the remote's fetch URL.

    Returns None if the repo has no remotes or if the URL can't be read.
    """

    try:
        repo = Repo(str(repo_path), search_parent_directories=True)
    except Exception:
        return None

    try:
        remotes = list(getattr(repo, "remotes", []) or [])
    except Exception:
        remotes = []
    if not remotes:
        return None

    chosen = None
    for r in remotes:
        try:
            if str(getattr(r, "name", "")) == "origin":
                chosen = r
                break
        except Exception:
            continue
    if chosen is None:
        chosen = remotes[0]

    # GitPython exposes URLs in a few shapes depending on version.
    for attr in ("url", "urls"):
        try:
            v = getattr(chosen, attr)
            if isinstance(v, str) and v.strip():
                return v.strip()
            if v is not None:
                urls = list(v)  # urls property often yields an iterator
                for u in urls:
                    s = str(u).strip()
                    if s:
                        return s
        except Exception:
            pass

    return None


def _default_cache_dir() -> Path:
    # Allow override for CI and power users.
    override = os.environ.get("CODE_PERISCOPE_CACHE_DIR")
    if override:
        return Path(override).expanduser().resolve()

    # macOS/Linux-friendly cache location.
    return Path.home() / ".cache" / "code-periscope" / "repos"


def _safe_repo_dirname(git_url: str) -> str:
    """Generate a stable, filesystem-safe directory name for a URL."""
    parsed = urlparse(git_url)
    # For scp-like SSH URLs (git@github.com:org/repo.git), urlparse is awkward.
    # Hash is used to be safe & deterministic.
    h = hashlib.sha256(git_url.encode("utf-8")).hexdigest()[:12]

    tail = (parsed.path or "").rstrip("/")
    # Try to keep a human hint when possible
    hint = tail.split("/")[-1] if tail else "repo"
    hint = hint.removesuffix(".git")
    hint = "".join(c if (c.isalnum() or c in "-_") else "_" for c in hint)[:40]
    if not hint:
        hint = "repo"

    return f"{hint}-{h}"


def resolve_repository(*, repo: Optional[Path], git_url: Optional[str], refresh: bool) -> Path:
    """Return a local path to the repository, cloning if needed.

    Exactly one of (repo, git_url) must be provided.

    Returns:
        Path to the local repository root.
    """

    if (repo is None) == (git_url is None):
        raise ValueError("Provide exactly one of repo or git_url")

    if repo is not None:
        resolved = repo.expanduser().resolve()
        try:
            Repo(str(resolved), search_parent_directories=True)
        except InvalidGitRepositoryError as e:
            raise ValueError(f"Not a git repository: {resolved}") from e
        return resolved

    assert git_url is not None
    cache_dir = _default_cache_dir()
    cache_dir.mkdir(parents=True, exist_ok=True)

    target = cache_dir / _safe_repo_dirname(git_url)

    if refresh and target.exists():
        shutil.rmtree(target)

    if not target.exists():
        Repo.clone_from(git_url, target)

    return target
