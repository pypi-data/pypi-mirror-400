from __future__ import annotations

import sys
from pathlib import Path

from sourcerat.sorter import sort_paths

from .config import ScanConfig
from .filters import apply_filters
from .parser import build_parser
from .renderer import render_file_list, render_files, render_tree
from .scanner import scan_project
from .tree import build_tree

DEBUG = False


def _write_output(text: str, output: Path | None) -> None:
    if output is None:
        sys.stdout.write(text)
    else:
        output.write_text(text, encoding="utf-8")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    config: ScanConfig = ScanConfig.from_args(args=args)
    paths = scan_project(config=config)
    paths = apply_filters(paths=paths, config=config)

    if not config.no_smart_sort:
        paths = sort_paths(paths=paths, config=config)

    if config.dry_run:
        output = render_file_list(paths, config.root)
        _write_output(output, config.output)
        return

    tree_text = build_tree(paths, config.root)

    output = "\n".join([render_tree(tree_text), render_files(paths, config)])

    _write_output(output, config.output)

    if DEBUG:
        for key, value in vars(args).items():
            print(f"  {key}: {value}")
