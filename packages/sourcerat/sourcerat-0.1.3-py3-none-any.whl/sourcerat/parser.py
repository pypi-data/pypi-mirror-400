import argparse
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

from .config import DEFAULT_EXCLUDE_DIRS


def _get_version() -> str:
    try:
        return version("sourcerat")
    except PackageNotFoundError:
        return "unknown"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sourcerat",
        description="Collect and bundle source code for LLM input",
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Project root directory (default: current directory)",
    )

    parser.add_argument(
        "--exclude-files",
        type=str,
        help="Comma-separated list of files or paths to exclude",
    )

    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and directories",
    )

    parser.add_argument(
        "--respect-gitignore",
        action="store_true",
        help="Respect .gitignore rules in project root",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show scanned files, don't generate output",
    )

    parser.add_argument(
        "--no-smart-sort",
        action="store_true",
        help="Don't use smart sorting of files",
    )

    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (default: stdout)",
    )

    parser.add_argument(
        "-fs",
        "--file-suffixes",
        type=str,
        help="Comma-separated list of file suffixes (e.g. py,c,h,rs)",
    )

    parser.add_argument(
        "-i",
        "--include",
        type=str,
        help="Comma-separated list of directories to include",
    )

    parser.add_argument(
        "-e",
        "--exclude",
        type=str,
        default=",".join(DEFAULT_EXCLUDE_DIRS),
        help="Comma-separated list of directories to exclude "
        f"(default: {','.join(DEFAULT_EXCLUDE_DIRS)})",
    )

    parser.add_argument(
        "--max-files",
        type=int,
        help="Maximum number of files",
    )

    parser.add_argument(
        "--max-lines",
        type=int,
        help="Maximum number of lines per file",
    )

    parser.add_argument(
        "--max-bytes",
        type=int,
        help="Maximum file size in bytes",
    )

    parser.add_argument(
        "--format",
        choices=("plain", "markdown"),
        default="plain",
        help="Output format",
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"sourcerat {_get_version()}",
    )

    return parser
