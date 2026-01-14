from __future__ import annotations

from pathlib import Path

from .config import ScanConfig


def apply_filters(
    paths: list[Path],
    config: ScanConfig,
) -> list[Path]:
    """
    Apply all configured filters to a list of file paths.

    Filters are applied in a deterministic order:
    1. file suffix
    2. file size (bytes)
    3. max files limit
    """
    result = paths
    pipeline = [_filter_by_suffix, _filter_by_size, _limit_files]
    for fn in pipeline:
        result = fn(result, config)

    return result


def _filter_by_suffix(
    paths: list[Path],
    config: ScanConfig,
) -> list[Path]:
    """
    Keep only files matching configured suffixes.

    If no suffixes are configured, all files are kept.
    """
    if not config.file_suffixes:
        return paths

    suffixes = {f".{s.lstrip('.')}" for s in config.file_suffixes}

    return [p for p in paths if p.suffix in suffixes]


def _filter_by_size(
    paths: list[Path],
    config: ScanConfig,
) -> list[Path]:
    """
    Exclude files larger than the configured max_bytes.
    """
    if config.max_bytes is None:
        return paths

    return [p for p in paths if p.stat().st_size <= config.max_bytes]


def _limit_files(
    paths: list[Path],
    config: ScanConfig,
) -> list[Path]:
    """
    Limit the total number of files.
    """
    if config.max_files is None:
        return paths

    return paths[: config.max_files]
