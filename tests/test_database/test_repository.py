"""
Tests for the DuckDB repository.
"""

from __future__ import annotations

import duckdb
import polars as pl
import pytest

from database.repository import DuckDBRepository
from tests.conftest import _create_test_schema


def test_insert_orders(repo: DuckDBRepository, sample_df: pl.DataFrame) -> None:
    count = repo.insert_orders(sample_df)
    assert count == 3

    result = repo.query("SELECT * FROM orders ORDER BY order_id")
    assert result.height == 3
    assert result["order_id"][0] == "ORD-001"


def test_query(repo: DuckDBRepository, sample_df: pl.DataFrame) -> None:
    repo.insert_orders(sample_df)
    result = repo.query("SELECT count(*) AS cnt FROM orders")
    assert result["cnt"][0] == 3


def test_table_exists(repo: DuckDBRepository) -> None:
    assert repo.table_exists("orders") is True
    assert repo.table_exists("nonexistent") is False


def test_staging_count(repo: DuckDBRepository, sample_df: pl.DataFrame) -> None:
    assert repo.staging_count() == 0
    repo.insert_orders(sample_df)
    assert repo.staging_count() == 3


def test_clear_staging(repo: DuckDBRepository, sample_df: pl.DataFrame) -> None:
    repo.insert_orders(sample_df)
    repo.clear_staging()
    assert repo.staging_count() == 0
