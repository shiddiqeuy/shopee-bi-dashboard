"""
Tests for customer analytics module.
"""

from __future__ import annotations

import polars as pl

from analytics.customer import CustomerAnalytics
from database.repository import DuckDBRepository


def test_customer_analytics_empty(repo: DuckDBRepository) -> None:
    module = CustomerAnalytics()
    result = module.compute(repo)
    assert result["total_customers"] == 0
    assert result["repeat_rate"] == 0.0


def test_customer_analytics_with_data(repo: DuckDBRepository, sample_df: pl.DataFrame) -> None:
    repo.insert_orders(sample_df)
    repo.build_warehouse()

    module = CustomerAnalytics()
    result = module.compute(repo)
    assert result["total_customers"] > 0
    assert "top_customers" in result
    assert "segments" in result
