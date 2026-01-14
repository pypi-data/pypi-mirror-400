from __future__ import annotations

from pathlib import Path

from .config import ScanConfig


def render_tree(tree_text: str) -> str:
    """
    Render the directory tree section.
    """
    return "\n".join(
        [
            "PROJECT TREE",
            tree_text,
            "",
        ]
    )


def render_files(
    paths: list[Path],
    config: ScanConfig,
) -> str:
    """
    Render file contents in the specified format.
    """
    root = config.root
    file_format = config.format.lower()

    if file_format == "markdown":
        return render_files_markdown(paths, root, config)
    elif file_format == "plain":
        return render_files_plain(paths, root, config)

    return render_files_plain(paths, root, config) + "\n"


def render_file_list(paths: list[Path], root: Path) -> str:
    """
    Render a simple file list (used for --dry-run).
    """
    lines = ["[DRY RUN]", f"Scanned files: {len(paths)}", ""]

    for path in paths:
        lines.append(str(path.relative_to(root)))

    return "\n".join(lines) + "\n"


def render_files_plain(paths: list[Path], root: Path, config: ScanConfig) -> str:
    """
    Render file contents in plain text format.
    """
    parts: list[str] = []

    for path in paths:
        rel = path.relative_to(root)
        parts.append(f"FILE: {rel}")
        parts.append(_read_file(path, config))
        parts.append("")

    return "\n".join(parts)


def render_files_markdown(paths: list[Path], root: Path, config: ScanConfig) -> str:
    """
    Render file contents in Markdown format.
    """
    parts: list[str] = []

    for path in paths:
        rel = path.relative_to(root)
        parts.append(f"## {rel}")
        parts.append("```")
        parts.append(_read_file(path, config))
        parts.append("```")
        parts.append("")

    return "\n".join(parts)


def _read_file(path: Path, config: ScanConfig) -> str:
    """
    Read file content and apply max_lines if configured.
    """
    text = path.read_text(encoding="utf-8", errors="replace")

    if config.max_lines is None:
        return text

    lines = text.splitlines()
    if len(lines) <= config.max_lines:
        return text

    truncated = lines[: config.max_lines]
    truncated.append(f"... [truncated after {config.max_lines} lines]")
    return "\n".join(truncated)
