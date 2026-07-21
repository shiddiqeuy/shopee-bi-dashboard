"""
Shopee ETL pipeline — wires extractor, transformer, and loader together.
"""

from __future__ import annotations

from core.interfaces import ETLPipeline, Repository
from etl.log_writer import ETLLogWriter
from etl.shopee.extractor import ShopeeExtractor
from etl.shopee.loader import ShopeeLoader
from etl.shopee.transformer import ShopeeTransformer
from utils.decorators import log_etl, measure_time
from utils.logger import get_logger

log = get_logger(__name__)


class ShopeeETLPipeline(ETLPipeline):
    """End-to-end ETL pipeline for Shopee order exports."""

    def __init__(self, repository: Repository) -> None:
        self.extractor = ShopeeExtractor()
        self.transformer = ShopeeTransformer()
        self.loader = ShopeeLoader(repository)
        self.log_writer = ETLLogWriter()

    @log_etl
    @measure_time
    def run(self, source_path: str) -> int:
        rows_extracted = 0
        rows_invalid = 0
        rows_loaded = 0
        status = "success"
        error_message = None

        try:
            raw_rows = list(self.extractor.extract(source_path))
            rows_extracted = len(raw_rows)

            df = self.transformer.transform(raw_rows)
            rows_invalid = rows_extracted - len(df)

            rows_loaded = self.loader.load(df)
        except Exception as exc:
            status = "failed"
            error_message = str(exc)
            log.exception("Shopee ETL pipeline failed for %s", source_path)
            raise
        finally:
            self.log_writer.write_run(
                source_file=source_path,
                rows_extracted=rows_extracted,
                rows_loaded=rows_loaded,
                rows_invalid=rows_invalid,
                status=status,
                error_message=error_message,
            )

        return rows_loaded
