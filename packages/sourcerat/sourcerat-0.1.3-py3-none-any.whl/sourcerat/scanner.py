from __future__ import annotations

from pathlib import Path

from .config import ScanConfig
from .gitignore import is_ignored, load_gitignore


def scan_project(config: ScanConfig) -> list[Path]:
    """
    Recursively scan the project directory using pathlib.

    This function only collects file paths.
    """
    files: list[Path] = []

    root = config.root

    gitignore_patterns: list[str] = []
    if config.respect_gitignore:
        print("Git Ignore is enabled")
        gitignore_patterns = load_gitignore(root)

    for path in root.rglob("*"):
        if path.is_dir():
            continue

        if not _is_allowed(path, config):
            continue

        if config.respect_gitignore:
            print("Git Ignore is enabled")
            if is_ignored(path, root, gitignore_patterns):
                continue

        files.append(path)

    return files


def _is_allowed(path: Path, config: ScanConfig) -> bool:
    """
    Check whether a file path is allowed based on directory rules.
    """
    rel = path.relative_to(config.root)

    # exclude specific files or paths
    rel_str = rel.as_posix()
    if rel_str in config.exclude_files or path.name in config.exclude_files:
        return False

    # include_dirs: file must be inside one of them
    if config.include_dirs:
        if not any(
            rel.parts[0] == inc or inc in rel.parts for inc in config.include_dirs
        ):
            return False

    for part in path.parts:
        if not config.include_hidden and part.startswith("."):
            return False
        if part in config.exclude_dirs:
            return False

    return True
