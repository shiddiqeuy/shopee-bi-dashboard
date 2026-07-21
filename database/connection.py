"""
DuckDB connection pool — supports concurrent access across requests.

Usage:
    from database.connection import get_connection, release_connection

    conn = get_connection()       # acquire from pool (blocks if empty)
    try:
        ...  # use conn
    finally:
        release_connection(conn)  # return to pool
"""

from __future__ import annotations

import queue
from typing import Optional

import duckdb

from config.config import DB_PATH
from utils.logger import get_logger

log = get_logger(__name__)

_connection_pool: Optional[queue.Queue[duckdb.DuckDBPyConnection]] = None
_POOL_SIZE = 4


def _create_connection() -> duckdb.DuckDBPyConnection:
    conn = duckdb.connect(str(DB_PATH))
    conn.execute("PRAGMA temp_directory = 'tmp'")
    conn.execute("SET enable_progress_bar = false")
    return conn


def init_pool(size: int = 4) -> None:
    """Create the connection pool with *size* connections."""
    global _connection_pool, _POOL_SIZE
    if _connection_pool is not None:
        return
    _POOL_SIZE = size
    _connection_pool = queue.Queue()
    for _ in range(size):
        _connection_pool.put(_create_connection())
    log.info("Initialised DuckDB connection pool (size=%d)", size)


def get_connection() -> duckdb.DuckDBPyConnection:
    """Acquire a connection from the pool (blocks until one is available)."""
    if _connection_pool is None:
        init_pool()
    conn = _connection_pool.get()
    return conn


def release_connection(conn: duckdb.DuckDBPyConnection) -> None:
    """Return a connection to the pool so other requests can reuse it."""
    if _connection_pool is not None:
        _connection_pool.put(conn)


def close_pool() -> None:
    """Close all connections in the pool and reset."""
    global _connection_pool
    if _connection_pool is None:
        return
    while not _connection_pool.empty():
        try:
            conn = _connection_pool.get_nowait()
            conn.close()
        except queue.Empty:
            break
    _connection_pool = None
    log.info("DuckDB connection pool closed")


# Backward-compatible aliases for Streamlit / tests that import close_connection
close_connection = close_pool


def replace_pool_for_test(
    conn: duckdb.DuckDBPyConnection,
) -> None:
    """Replace the pool with a single-entry pool using *conn* (test helper)."""
    global _connection_pool
    _connection_pool = queue.Queue()
    _connection_pool.put(conn)
