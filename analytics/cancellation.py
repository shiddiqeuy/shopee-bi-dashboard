"""
Cancellation analytics module.

Computes: cancellation rate, cancellation by city, product, and trend.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from core.interfaces import AnalyticsModule, Repository
from utils.logger import get_logger

log = get_logger(__name__)

_SQL_CANCELLATION_RATE = """
SELECT
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT CASE WHEN order_status = 'cancelled' THEN order_id END) AS cancelled_orders
FROM orders
"""

_SQL_CANCELLATION_CITY = """
SELECT
    city,
    province,
    COUNT(DISTINCT order_id) AS cancelled_orders,
    SUM(total_amount) AS cancelled_revenue
FROM orders
WHERE order_status = 'cancelled'
GROUP BY city, province
ORDER BY cancelled_orders DESC
"""

_SQL_CANCELLATION_PRODUCT = """
SELECT
    product_name,
    COUNT(DISTINCT order_id) AS cancelled_orders,
    SUM(total_amount) AS cancelled_revenue
FROM orders
WHERE order_status = 'cancelled'
GROUP BY product_name
ORDER BY cancelled_orders DESC
LIMIT 20
"""

_SQL_CANCELLATION_TREND = """
SELECT
    STRFTIME(order_date, '%Y-%m') AS month,
    COUNT(DISTINCT order_id) AS cancelled_orders,
    SUM(total_amount) AS cancelled_revenue
FROM orders
WHERE order_status = 'cancelled'
  AND order_date IS NOT NULL
GROUP BY month
ORDER BY month
"""

_SQL_CANCELLATION_REASONS = """
SELECT
    cancellation_reason,
    COUNT(DISTINCT order_id) AS cancelled_orders,
    SUM(total_amount) AS cancelled_revenue
FROM orders
WHERE order_status = 'cancelled'
  AND cancellation_reason IS NOT NULL
  AND cancellation_reason != ''
GROUP BY cancellation_reason
ORDER BY cancelled_orders DESC
"""


class CancellationAnalytics(AnalyticsModule):
    """Cancellation rate and breakdown analytics."""

    @property
    def name(self) -> str:
        return "cancellation"

    def register(self) -> str:
        return self.name

    def compute(self, repo: Repository) -> dict[str, Any]:
        rate_df = repo.query(_SQL_CANCELLATION_RATE)
        if rate_df.height == 0:
            return {"cancellation_rate": 0.0}

        total = rate_df["total_orders"][0]
        cancelled = rate_df["cancelled_orders"][0]
        cancellation_rate = round(cancelled / total * 100, 2) if total else 0.0

        by_city = repo.query(_SQL_CANCELLATION_CITY).to_dicts()
        by_product = repo.query(_SQL_CANCELLATION_PRODUCT).to_dicts()
        by_month = repo.query(_SQL_CANCELLATION_TREND).to_dicts()
        by_reason = repo.query(_SQL_CANCELLATION_REASONS).to_dicts()

        return {
            "cancellation_rate": cancellation_rate,
            "total_orders": int(total),
            "cancelled_orders": int(cancelled),
            "by_city": by_city,
            "by_product": by_product,
            "by_month": by_month,
            "by_reason": by_reason,
        }
