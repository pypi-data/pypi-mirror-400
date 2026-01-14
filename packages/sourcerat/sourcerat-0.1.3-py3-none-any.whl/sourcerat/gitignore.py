from __future__ import annotations

from fnmatch import fnmatch
from pathlib import Path


def load_gitignore(root: Path) -> list[str]:
    """
    Load .gitignore patterns from project root.
    Comments and empty lines are ignored.
    """
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        raise ValueError(f"No .gitignore found in scan root: {root}")

    patterns: list[str] = []
    for line in gitignore.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        patterns.append(line)

    return patterns


def is_ignored(path: Path, root: Path, patterns: list[str]) -> bool:
    """
    Check whether a path matches any gitignore pattern.
    """
    rel = path.relative_to(root).as_posix()

    for pattern in patterns:
        # directory patterns
        if pattern.endswith("/") and rel.startswith(pattern.rstrip("/")):
            return True
        if fnmatch(rel, pattern):
            return True

    return False
