"""
Base ETL orchestrator — a registry-driven pipeline runner.

Each marketplace provides an Extractor + Transformer + Loader triplet.
The ETLRunner discovers all files in the input directory, dispatches
to the correct pipeline, and logs every step.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import polars as pl

from core.interfaces import ETLPipeline, Extractor, Transformer, Loader
from utils.logger import get_logger

log = get_logger(__name__)


class ETLRunner:
    """Orchestrates extract → transform → load across all input files."""

    def __init__(self, input_dir: str | Path, loader: Loader) -> None:
        self.input_dir = Path(input_dir)
        self.loader = loader
        self._pipelines: dict[str, ETLPipeline] = {}

    def register(self, source_type: str, pipeline: ETLPipeline) -> None:
        """Register an ETL pipeline for a source type (e.g. 'shopee')."""
        self._pipelines[source_type] = pipeline
        log.info("Registered ETL pipeline: %s", source_type)

    def detect_source(self, path: Path) -> Optional[str]:
        """Detect the source type from the file name or extension."""
        name = path.name.lower()
        if "shopee" in name or name.endswith(".xlsx"):
            return "shopee"
        return None

    def run_all(self) -> int:
        """Run ETL for every file in the input directory. Returns total rows loaded."""
        files = sorted(self.input_dir.glob("*.*"))
        if not files:
            log.warning("No files found in %s", self.input_dir)
            return 0

        total = 0
        for file_path in files:
            if not file_path.is_file():
                continue
            source = self.detect_source(file_path)
            if source is None:
                log.info("Skipping unrecognised file: %s", file_path.name)
                continue
            pipeline = self._pipelines.get(source)
            if not pipeline:
                log.warning("No pipeline registered for source: %s", source)
                continue
            try:
                rows = pipeline.run(str(file_path))
                total += rows
                log.info(
                    "Loaded %d rows from %s via %s pipeline",
                    rows, file_path.name, source,
                )
            except Exception:
                log.exception("ETL failed for %s", file_path.name)
        return total

    def run_single(self, path: str | Path, source: Optional[str] = None) -> int:
        """Run ETL for a single file."""
        path = Path(path)
        src = source or self.detect_source(path)
        if not src:
            log.error("Cannot detect source for %s", path.name)
            return 0
        pipeline = self._pipelines.get(src)
        if not pipeline:
            log.error("No pipeline for source: %s", src)
            return 0
        return pipeline.run(str(path))
