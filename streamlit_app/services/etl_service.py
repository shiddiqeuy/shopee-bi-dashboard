"""
ETLService — orchestrates the full ETL pipeline for uploaded files.

Saves uploaded file to input directory, runs the Shopee ETL pipeline,
and builds the warehouse.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from config.config import INPUT_DIR
from database.migrations import migrate
from database.repository import DuckDBRepository
from etl.shopee.pipeline import ShopeeETLPipeline
from utils.logger import get_logger

log = get_logger(__name__)


class ETLService:
    """Orchestrates file ingestion and warehouse build."""

    def __init__(self, repo: DuckDBRepository) -> None:
        self.repo = repo

    def run(self, file_path: str) -> dict:
        """Run full ETL on a file and build warehouse.

        Returns status dict with row counts.
        """
        migrate(self.repo.conn)

        pipeline = ShopeeETLPipeline(self.repo)
        rows = pipeline.run(file_path)

        result = {"rows_loaded": rows, "status": "success"}

        if rows > 0:
            self.repo.build_warehouse()
            result["warehouse_built"] = True
            result["total_rows"] = self.repo.staging_count()

        return result
