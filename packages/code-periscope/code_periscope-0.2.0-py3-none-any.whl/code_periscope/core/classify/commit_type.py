from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(frozen=True)
class CommitType:
    label: str  # e.g. feature, fix, refactor, docs, test, chore, perf, ci, build, style, other
    confidence: float  # 0..1


_PATTERNS: list[tuple[str, re.Pattern]] = [
    ("fix", re.compile(r"\b(fix|bug|hotfix|patch|regression)\b", re.IGNORECASE)),
    ("feature", re.compile(r"\b(feat|feature|add|implement|introduce)\b", re.IGNORECASE)),
    ("refactor", re.compile(r"\b(refactor|cleanup|restructure)\b", re.IGNORECASE)),
    ("perf", re.compile(r"\b(perf|optimi[sz]e|speed up)\b", re.IGNORECASE)),
    ("docs", re.compile(r"\b(docs?|readme|changelog)\b", re.IGNORECASE)),
    ("test", re.compile(r"\b(test|tests|spec)\b", re.IGNORECASE)),
    ("ci", re.compile(r"\b(ci|github actions|workflow)\b", re.IGNORECASE)),
    ("build", re.compile(r"\b(build|deps?|dependencies|bump)\b", re.IGNORECASE)),
    ("style", re.compile(r"\b(format|lint|style)\b", re.IGNORECASE)),
    ("chore", re.compile(r"\b(chore|misc|housekeeping)\b", re.IGNORECASE)),
]


def classify_commit_message(message: str) -> CommitType:
    msg = (message or "").strip()
    if not msg:
        return CommitType(label="other", confidence=0.2)

    # Conventional commits: feat:, fix:, refactor:, etc.
    m = re.match(r"^(\w+)(\(.+\))?:\s+", msg)
    if m:
        prefix = m.group(1).lower()
        mapping = {
            "feat": "feature",
            "fix": "fix",
            "refactor": "refactor",
            "docs": "docs",
            "test": "test",
            "chore": "chore",
            "perf": "perf",
            "ci": "ci",
            "build": "build",
            "style": "style",
        }
        if prefix in mapping:
            return CommitType(label=mapping[prefix], confidence=0.95)

    for label, pat in _PATTERNS:
        if pat.search(msg):
            return CommitType(label=label, confidence=0.7)

    return CommitType(label="other", confidence=0.3)
