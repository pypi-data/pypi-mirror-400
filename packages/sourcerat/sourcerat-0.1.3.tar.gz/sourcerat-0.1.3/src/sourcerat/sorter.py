from __future__ import annotations

from pathlib import Path

from sourcerat.config import ScanConfig

ENTRYPOINT_NAMES = {
    # Python
    "main.py",
    "__main__.py",
    "app.py",
    "cli.py",
    # Rust
    "main.rs",
    "app.rs",
    # C / C++
    "main.c",
    "app.c",
    "main.cpp",
    "app.cpp",
    # Java
    "Main.java",
    "App.java",
    # JavaScript
    "index.js",
    "main.js",
    "app.js",
}


DEPRIORITIZED_DIRS = {
    "tests",
    "test",
    "examples",
    "example",
    "demo",
}


def sort_paths(
    paths: list[Path],
    config: ScanConfig,
) -> list[Path]:
    return sorted(paths, key=lambda p: _score(p, config), reverse=True)


def _score(path: Path, config: ScanConfig) -> int:
    score = 0
    rel = path.relative_to(config.root)

    # generic
    if path.name in ENTRYPOINT_NAMES:
        score += 100

    depth = len(rel.parts)
    score += max(0, 20 - depth)

    if any(part in DEPRIORITIZED_DIRS for part in rel.parts):
        score -= 50

    score += _language_score(path, config)

    return score


def _language_score(path: Path, config: ScanConfig) -> int:
    suffix = path.suffix.lower()

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return 0

    # Python
    if suffix == ".py":
        score = 0
        if 'if __name__ == "__main__"' in text:
            score += 40
        if any(x in text for x in ("argparse", "click", "typer")):
            score += 20
        if path.name == "__init__.py":
            score += 5
        return score

    # Rust
    if suffix == ".rs":
        score = 0
        if path.name == "main.rs":
            score += 120
        if "fn main(" in text:
            score += 60
        if path.name == "lib.rs":
            score += 30
        return score

    # C
    if suffix == ".c":
        if "main(" in text:
            return 60

    # C++
    if suffix == ".cpp":
        if "main(" in text:
            return 60

    if suffix in {".h", ".hpp"}:
        return -10

    # Java
    if suffix == ".java":
        score = 0
        if "public static void main" in text:
            score += 80
        if path.stem == path.parent.name:
            score += 20
        return score

    # JavaScript
    if suffix in {".js", ".mjs", ".cjs"}:
        score = 0
        if text.startswith("#!/usr/bin/env node"):
            score += 80
        if path.name == "index.js":
            score += 60
        if any(x in text for x in ("require(", "import ")):
            score += 10
        return score

    return 0
