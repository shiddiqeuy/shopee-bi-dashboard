"""
Abstract interfaces for the Clean Architecture boundary layers.

All concrete implementations (ShopeeETL, DuckDBRepository, ExcelDashboard)
depend on these abstractions, not on each other.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator, Sequence
from typing import Any, Optional

import polars as pl

from core.entities import Insight


# ── Repository ──────────────────────────────────────────────────────────────


class Repository(ABC):
    """Abstract data-access boundary."""

    @abstractmethod
    def insert_orders(self, df: pl.DataFrame) -> int:
        """Insert orders into staging. Returns row count."""

    @abstractmethod
    def build_warehouse(self) -> None:
        """Build star-schema tables from staging."""

    @abstractmethod
    def query(self, sql: str, params: Optional[dict[str, Any]] = None) -> pl.DataFrame:
        """Execute a SQL query and return a Polars DataFrame."""

    @abstractmethod
    def table_exists(self, name: str) -> bool:
        """Check if a table exists in the database."""


# ── ETL Pipeline ────────────────────────────────────────────────────────────


class Extractor(ABC):
    """Reads raw data from a source file and yields dicts."""

    @abstractmethod
    def extract(self, path: str) -> Generator[dict[str, Any], None, None]:
        """Yield raw row-dicts from *path*."""


class Transformer(ABC):
    """Transforms raw dicts into canonical entities."""

    @abstractmethod
    def transform(self, rows: Sequence[dict[str, Any]]) -> pl.DataFrame:
        """Return a Polars DataFrame with canonical schema."""


class Loader(ABC):
    """Writes a canonical DataFrame into the database."""

    @abstractmethod
    def load(self, df: pl.DataFrame) -> int:
        """Insert data and return inserted row count."""


class ETLPipeline(ABC):
    """Orchestrates extract → transform → load for one source."""

    @abstractmethod
    def run(self, source_path: str) -> int:
        """Run full ETL for *source_path*. Returns rows loaded."""


# ── Analytics Module ────────────────────────────────────────────────────────


class AnalyticsModule(ABC):
    """One analytical concern — e.g. customer, product, city."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable module name."""

    @abstractmethod
    def compute(self, repo: Repository) -> dict[str, Any]:
        """Run analytics queries and return a result dict."""

    @abstractmethod
    def register(self) -> str:
        """Self-register and return module name."""


# ── Dashboard / Excel ───────────────────────────────────────────────────────


class SheetWriter(ABC):
    """Writes one sheet in the Excel workbook."""

    @property
    @abstractmethod
    def sheet_name(self) -> str:
        """Sheet tab name."""

    @abstractmethod
    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        """Write content into *sheet* using *workbook* and *analytics* data."""


class DashboardBuilder(ABC):
    """Orchestrates building the full dashboard workbook."""

    @abstractmethod
    def build(self, analytics: dict[str, Any]) -> str:
        """Generate the dashboard Excel file. Returns output path."""


# ── Insight Engine ──────────────────────────────────────────────────────────


class InsightEngine(ABC):
    """Generates hidden business insights from analytics results."""

    @abstractmethod
    def generate(self, analytics: dict[str, Any]) -> list[Insight]:
        """Produce a list of Insight objects."""
