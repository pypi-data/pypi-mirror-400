from __future__ import annotations

from pathlib import Path


def build_tree(paths: list[Path], root: Path) -> str:
    """
    Build a textual directory tree from a list of file paths.

    The tree only reflects the given paths (already scanned & filtered).
    """
    tree = _build_tree_structure(paths, root)
    lines: list[str] = []

    _render_tree(tree, lines, prefix="")
    return "\n".join(lines)


def _build_tree_structure(
    paths: list[Path],
    root: Path,
) -> dict:
    """
    Build a nested dict structure representing the directory tree.
    """
    tree: dict = {}

    for path in paths:
        relative = path.relative_to(root)
        current = tree

        for part in relative.parts:
            current = current.setdefault(part, {})

    return tree


def _render_tree(
    tree: dict,
    lines: list[str],
    prefix: str,
) -> None:
    """
    Render the nested tree structure into text lines.
    """
    entries = sorted(tree.items(), key=lambda x: x[0])

    for index, (name, subtree) in enumerate(entries):
        is_last = index == len(entries) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{name}")

        extension = "    " if is_last else "│   "
        _render_tree(subtree, lines, prefix + extension)
