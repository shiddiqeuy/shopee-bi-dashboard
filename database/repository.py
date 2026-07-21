"""
DuckDB repository — implements the abstract Repository interface.

All data access goes through this class. The rest of the application
never touches DuckDB directly.
"""

from __future__ import annotations

from typing import Any, Optional

import duckdb
import polars as pl

from core.interfaces import Repository
from database.connection import get_connection
from utils.logger import get_logger

log = get_logger(__name__)


class DuckDBRepository(Repository):
    """Concrete repository backed by DuckDB."""

    def __init__(self, conn: Optional[duckdb.DuckDBPyConnection] = None) -> None:
        self.conn = conn or get_connection()

    def insert_orders(self, df: pl.DataFrame) -> int:
        """Insert a Polars DataFrame into the orders staging table."""
        row_count = df.height
        if row_count == 0:
            return 0
        self.conn.register("df", df.to_pandas())
        self.conn.execute("DELETE FROM orders WHERE order_id IN (SELECT order_id FROM df)")
        self.conn.execute("INSERT INTO orders SELECT *, CURRENT_TIMESTAMP AS _loaded_at FROM df")
        log.info("Inserted %d rows into orders staging", row_count)
        return row_count

    def build_warehouse(self) -> None:
        """Build the star-schema warehouse from staging data."""
        from database.warehouse import WarehouseBuilder
        builder = WarehouseBuilder(self.conn)
        builder.build()

    def query(self, sql: str, params: Optional[dict[str, Any]] = None) -> pl.DataFrame:
        """Execute SQL and return a Polars DataFrame."""
        if params:
            return pl.from_arrow(self.conn.execute(sql, params).to_arrow_table())
        return pl.from_arrow(self.conn.execute(sql).to_arrow_table())

    def table_exists(self, name: str) -> bool:
        """Check if a table exists in the database."""
        result = self.conn.execute(
            "SELECT count(*) FROM information_schema.tables WHERE table_name = ?",
            [name],
        ).fetchone()
        return result[0] > 0

    def staging_count(self) -> int:
        """Return the number of rows in the orders staging table."""
        result = self.conn.execute("SELECT count(*) FROM orders").fetchone()
        return result[0]

    def clear_staging(self) -> None:
        """Truncate the orders staging table."""
        self.conn.execute("DELETE FROM orders")
        log.info("Cleared orders staging table")

    def execute_sql(self, sql: str) -> None:
        """Execute raw SQL (for DDL or admin operations)."""
        self.conn.execute(sql)
