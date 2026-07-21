"""
DuckDB connection manager — singleton per process.

Usage:
    from database.connection import get_connection
    conn = get_connection()
"""

from __future__ import annotations

from typing import Optional

import duckdb

from config.config import DB_PATH
from utils.logger import get_logger

log = get_logger(__name__)

_connection: Optional[duckdb.DuckDBPyConnection] = None


def get_connection() -> duckdb.DuckDBPyConnection:
    """Return the singleton DuckDB connection, creating it if needed."""
    global _connection
    if _connection is None:
        log.info("Opening DuckDB at %s", DB_PATH)
        _connection = duckdb.connect(str(DB_PATH))
        _connection.execute("PRAGMA temp_directory = 'tmp'")
        _connection.execute("SET enable_progress_bar = false")
    return _connection


def close_connection() -> None:
    """Close the singleton DuckDB connection."""
    global _connection
    if _connection is not None:
        log.info("Closing DuckDB connection")
        _connection.close()
        _connection = None
