"""
Shared fixtures for all tests.

Uses an in-memory DuckDB so no test touches the real database.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Generator

import duckdb
import polars as pl
import pytest

from config.config import COLUMN_MAP, CANONICAL_COLUMNS
from database.repository import DuckDBRepository


@pytest.fixture
def in_memory_db() -> Generator[duckdb.DuckDBPyConnection, None, None]:
    """Provide an in-memory DuckDB connection for testing."""
    conn = duckdb.connect(":memory:")
    conn.execute("SET enable_progress_bar = false")
    yield conn
    conn.close()


@pytest.fixture
def repo(in_memory_db: duckdb.DuckDBPyConnection) -> DuckDBRepository:
    """Provide a repository backed by in-memory DuckDB."""
    r = DuckDBRepository(in_memory_db)
    _create_test_schema(in_memory_db)
    return r


def _create_test_schema(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE orders (
            order_id            VARCHAR,
            order_status        VARCHAR,
            product_name        VARCHAR,
            product_sku         VARCHAR,
            variation           VARCHAR,
            quantity            INTEGER,
            price               DECIMAL(18,2),
            total_amount        DECIMAL(18,2),
            buyer_name          VARCHAR,
            buyer_username      VARCHAR,
            city                VARCHAR,
            province            VARCHAR,
            shipping_provider   VARCHAR,
            shipping_method     VARCHAR,
            shipping_cost       DECIMAL(18,2),
            payment_method      VARCHAR,
            order_date          TIMESTAMP,
            payment_date        TIMESTAMP,
            shipping_date       TIMESTAMP,
            voucher_seller      DECIMAL(18,2),
            voucher_shopee      DECIMAL(18,2),
            cancellation_reason VARCHAR,
            _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)


@pytest.fixture
def sample_df() -> pl.DataFrame:
    """A small sample of canonical order data."""
    return pl.DataFrame({
        "order_id": ["ORD-001", "ORD-002", "ORD-003"],
        "order_status": ["completed", "completed", "cancelled"],
        "product_name": ["Product A", "Product B", "Product C"],
        "product_sku": ["SKU-A", "SKU-B", "SKU-C"],
        "variation": ["Red", "Blue", "Green"],
        "quantity": [2, 1, 3],
        "price": ["50000", "75000", "30000"],
        "total_amount": ["100000", "75000", "90000"],
        "buyer_name": ["Budi", "Ani", "Citra"],
        "buyer_username": ["budi01", "ani89", "citra22"],
        "city": ["Jakarta Pusat", "Bandung", "Surabaya"],
        "province": ["DKI Jakarta", "Jawa Barat", "Jawa Timur"],
        "shipping_provider": ["JNE", "J&T", "SiCepat"],
        "shipping_method": ["REG", "YES", "ECO"],
        "shipping_cost": ["10000", "15000", "8000"],
        "payment_method": ["Transfer Bank", "COD", "OVO"],
        "order_date": ["2024-01-15 10:00:00", "2024-01-16 14:30:00", "2024-01-17 09:00:00"],
        "payment_date": ["2024-01-15 10:05:00", "2024-01-16 14:35:00", None],
        "shipping_date": ["2024-01-15 12:00:00", "2024-01-16 16:00:00", None],
        "voucher_seller": ["0", "5000", "0"],
        "voucher_shopee": ["0", "0", "10000"],
        "cancellation_reason": [None, None, "out of stock"],
    })
