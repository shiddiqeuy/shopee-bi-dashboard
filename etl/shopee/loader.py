"""
Shopee data loader — writes canonical DataFrame into DuckDB staging.

The loader inserts into the `orders` staging table via the repository.
"""

from __future__ import annotations

import polars as pl

from core.interfaces import Loader, Repository
from utils.logger import get_logger

log = get_logger(__name__)


class ShopeeLoader(Loader):
    """Load transformed Shopee data into the warehouse."""

    def __init__(self, repository: Repository) -> None:
        self.repository = repository

    def load(self, df: pl.DataFrame) -> int:
        if df.is_empty():
            log.warning("ShopeeLoader: empty DataFrame, nothing to load")
            return 0

        count = self.repository.insert_orders(df)
        log.info("Loaded %d rows into orders staging", count)
        return count
