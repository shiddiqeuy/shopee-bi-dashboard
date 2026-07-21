"""
Merges multiple Polars DataFrames into a single deduplicated dataset.

Strategy:
1  Concatenate all DataFrames vertically.
2  Remove duplicate order_ids keeping the first occurrence.
3  Return a single canonical DataFrame.
"""

from __future__ import annotations

from typing import Optional

import polars as pl

from utils.logger import get_logger

log = get_logger(__name__)


def merge_dataframes(
    frames: list[pl.DataFrame],
    dedup_on: str = "order_id",
    keep: str = "first",
) -> pl.DataFrame:
    """Merge and deduplicate a list of DataFrames.

    Parameters
    ----------
    frames:
        List of DataFrames with compatible schemas.
    dedup_on:
        Column to deduplicate on.
    keep:
        Which duplicate to keep ('first' or 'last').

    Returns
    -------
    A single deduplicated DataFrame.
    """
    if not frames:
        log.warning("merge_dataframes called with empty list")
        return pl.DataFrame()

    if len(frames) == 1:
        result = frames[0]
    else:
        result = pl.concat(frames, how="vertical_relaxed")

    before = result.height
    result = result.unique(subset=[dedup_on], keep=keep)
    after = result.height
    if before > after:
        log.info(
            "Deduplication removed %d duplicate rows on '%s'",
            before - after, dedup_on,
        )

    return result


def merge_with_metadata(
    frames: list[pl.DataFrame],
    source_column: str = "_source_file",
    dedup_on: str = "order_id",
) -> pl.DataFrame:
    """Merge DataFrames, adding a source file column before dedup."""
    tagged: list[pl.DataFrame] = []
    for f in frames:
        if source_column not in f.columns:
            f = f.with_columns(pl.lit("merged").alias(source_column))
        tagged.append(f)

    return merge_dataframes(tagged, dedup_on=dedup_on)
