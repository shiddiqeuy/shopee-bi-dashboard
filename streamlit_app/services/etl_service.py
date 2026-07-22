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

    # ── File management ──────────────────────────────────────────────────

    @staticmethod
    def save_upload(file_bytes: bytes, filename: str) -> Path:
        """Save an uploaded file to INPUT_DIR and return its path."""
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        dest = INPUT_DIR / filename
        dest.write_bytes(file_bytes)
        log.info("Saved uploaded file: %s", dest)
        return dest

    @staticmethod
    def list_files() -> list[dict]:
        """Return list of files in INPUT_DIR with metadata."""
        if not INPUT_DIR.exists():
            return []
        files = []
        for p in sorted(INPUT_DIR.iterdir()):
            if p.is_file():
                stat = p.stat()
                files.append({
                    "name": p.name,
                    "path": str(p),
                    "size": stat.st_size,
                    "size_display": _format_size(stat.st_size),
                    "modified": stat.st_mtime,
                })
        return files

    @staticmethod
    def delete_file(filename: str) -> bool:
        """Delete a file from INPUT_DIR by name."""
        path = INPUT_DIR / filename
        if path.exists() and path.is_file():
            path.unlink()
            log.info("Deleted file: %s", path)
            return True
        return False

    @staticmethod
    def clear_all() -> int:
        """Delete all files in INPUT_DIR. Returns count of deleted files."""
        count = 0
        if INPUT_DIR.exists():
            for p in INPUT_DIR.iterdir():
                if p.is_file():
                    p.unlink()
                    count += 1
        log.info("Cleared %d files from input directory", count)
        return count

    # ── ETL ──────────────────────────────────────────────────────────────

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

    def rebuild_all(self) -> dict:
        """Rebuild staging and warehouse from files currently in INPUT_DIR."""
        migrate(self.repo.conn)
        self.repo.clear_staging()

        pipeline = ShopeeETLPipeline(self.repo)
        results = []
        total_loaded = 0

        for file_info in self.list_files():
            filename = file_info["name"]
            try:
                rows = pipeline.run(file_info["path"])
                total_loaded += rows
                results.append({
                    "filename": filename,
                    "rows_loaded": rows,
                    "warehouse_built": False,
                    "total_rows": total_loaded,
                    "status": "success",
                })
            except Exception as exc:
                log.exception("ETL rebuild failed for %s", filename)
                results.append({
                    "filename": filename,
                    "rows_loaded": 0,
                    "warehouse_built": False,
                    "total_rows": total_loaded,
                    "status": "error",
                    "error": str(exc),
                })

        self.repo.build_warehouse()
        final_total = self.repo.staging_count()
        for result in results:
            result["warehouse_built"] = True
            result["total_rows"] = final_total

        return {
            "results": results,
            "rows_loaded": total_loaded,
            "warehouse_built": True,
            "total_rows": final_total,
            "status": "success" if all(r["status"] == "success" for r in results) else "partial_error",
        }


def _format_size(size: int) -> str:
    """Format byte size to human-readable string."""
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}" if unit != "B" else f"{size} B"
        size /= 1024
    return f"{size:.1f} TB"
