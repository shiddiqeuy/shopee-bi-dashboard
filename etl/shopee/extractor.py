"""
Shopee order export extractor.

Reads .xlsx / .xls / .csv files exported from Shopee and yields
raw row-dicts with column names normalised via the config mapping.
"""

from __future__ import annotations

from collections.abc import Generator
from pathlib import Path
from typing import Any, Optional

import pandas as pd
import polars as pl

from config.config import COLUMN_MAP
from core.interfaces import Extractor
from utils.helpers import safe_string
from utils.logger import get_logger

log = get_logger(__name__)


class ShopeeExtractor(Extractor):
    """Extract rows from a Shopee export file."""

    SUPPORTED_EXTENSIONS = {".xlsx", ".xls", ".csv"}

    def extract(self, path: str) -> Generator[dict[str, Any], None, None]:
        file_path = Path(path)
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")

        log.info("Extracting from: %s", file_path.name)
        raw_df = self._read_file(file_path)
        mapped_df = self._rename_columns(raw_df)
        log.info("Extracted %d rows from %s", len(mapped_df), file_path.name)

        for row in mapped_df.to_dicts():
            yield row

    def _read_file(self, path: Path) -> pl.DataFrame:
        """Read file into a Polars DataFrame with string columns."""
        ext = path.suffix.lower()
        if ext == ".csv":
            try:
                return pl.read_csv(
                    path,
                    infer_schema=False,
                    truncate_ragged_lines=True,
                    ignore_errors=True,
                )
            except Exception:
                log.warning("Falling back to pandas for CSV: %s", path.name)
                pdf = pd.read_csv(path, dtype=str, encoding_errors="replace")
                return pl.from_pandas(pdf)
        else:
            try:
                pdf = pd.read_excel(path, dtype=str, engine="openpyxl")
                return pl.from_pandas(pdf)
            except Exception:
                log.warning("Fallback reading excel: %s", path.name)
                pdf = pd.read_excel(path, dtype=str, engine="xlrd")
                return pl.from_pandas(pdf)

    def _rename_columns(self, df: pl.DataFrame) -> pl.DataFrame:
        """Map raw column names to canonical names via COLUMN_MAP.

        Handles duplicate target names by keeping only the first mapping.
        """
        rename_map: dict[str, str] = {}
        seen_targets: set[str] = set()
        for col in df.columns:
            key = safe_string(col).lower()
            target = COLUMN_MAP.get(key, key)
            if target in seen_targets:
                log.debug("Skipping duplicate column '%s' → '%s'", col, target)
                continue
            seen_targets.add(target)
            rename_map[col] = target

        return df.rename(rename_map)
