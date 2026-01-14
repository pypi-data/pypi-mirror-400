from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

DEFAULT_EXCLUDE_FILES = {
    # Python
    "uv.lock",
    "poetry.lock",
    "Pipfile.lock",
    # Rust
    "Cargo.lock",
    # JavaScript / Node
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    # Java / JVM
    "gradle.lockfile",
}

DEFAULT_EXCLUDE_DIRS = [
    # common
    ".git",
    ".hg",
    ".svn",
    ".idea",
    ".vscode",
    # Python
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "venv",
    ".venv",
    "env",
    # Rust
    "target",
    # JavaScript / Node
    "node_modules",
    "dist",
    "build",
    # Java
    "out",
    ".gradle",
    "build",
    # C / C++
    "cmake-build-debug",
    "cmake-build-release",
    "CMakeFiles",
]


def _split_csv(value: str | None) -> list[str]:
    """Split a comma-separated CLI argument into a list of strings."""
    if not value:
        return []
    return [v.strip() for v in value.split(",") if v.strip()]


@dataclass(slots=True)
class ScanConfig:
    """
    Immutable configuration object derived from CLI arguments.

    This class contains all parameters required to scan a project,
    filter relevant source files, and render the final output.
    """

    root: Path
    output: Path | None
    dry_run: bool
    no_smart_sort: bool
    respect_gitignore: bool

    file_suffixes: set[str]
    include_dirs: set[str]
    exclude_dirs: set[str]
    exclude_files: set[str]

    include_hidden: bool

    max_files: int | None
    max_lines: int | None
    max_bytes: int | None

    format: str

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> ScanConfig:
        """
        Create a ScanConfig instance from parsed argparse arguments.

        This method performs only lightweight normalization
        (e.g. CSV splitting, Path resolving) and no validation.
        """
        if args.exclude_files is None:
            exclude_files = set(DEFAULT_EXCLUDE_FILES)
        else:
            exclude_files = set(_split_csv(args.exclude_files))

        return cls(
            root=Path(args.path).resolve(),
            output=args.output,
            file_suffixes=set(_split_csv(args.file_suffixes)),
            include_dirs=set(_split_csv(args.include)),
            exclude_dirs=set(_split_csv(args.exclude)),
            include_hidden=args.include_hidden,
            max_files=args.max_files,
            max_lines=args.max_lines,
            max_bytes=args.max_bytes,
            format=args.format,
            dry_run=args.dry_run,
            no_smart_sort=args.no_smart_sort,
            respect_gitignore=args.respect_gitignore,
            exclude_files=exclude_files,
        )
