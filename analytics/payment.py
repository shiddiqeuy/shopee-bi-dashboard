"""
Payment analytics module.

Computes: payment method distribution, revenue by method,
customer preference by region, average transaction value by method.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from core.interfaces import AnalyticsModule, Repository
from utils.logger import get_logger

log = get_logger(__name__)

_SQL_PAYMENT_SUMMARY = """
SELECT
    payment_method,
    COUNT(DISTINCT order_id) AS order_count,
    COUNT(DISTINCT buyer_username) AS customer_count,
    SUM(total_amount) AS revenue,
    AVG(total_amount) AS avg_transaction
FROM orders
WHERE payment_method IS NOT NULL
  AND payment_method != ''
  AND order_status != 'cancelled'
GROUP BY payment_method
ORDER BY revenue DESC
"""

_SQL_PAYMENT_REGION = """
SELECT
    payment_method,
    province,
    COUNT(DISTINCT order_id) AS order_count
FROM orders
WHERE payment_method IS NOT NULL
  AND payment_method != ''
  AND order_status != 'cancelled'
GROUP BY payment_method, province
ORDER BY payment_method, order_count DESC
"""


class PaymentAnalytics(AnalyticsModule):
    """Payment method analytics."""

    @property
    def name(self) -> str:
        return "payment"

    def register(self) -> str:
        return self.name

    def compute(self, repo: Repository) -> dict[str, Any]:
        summary = repo.query(_SQL_PAYMENT_SUMMARY)
        region = repo.query(_SQL_PAYMENT_REGION)

        if summary.height == 0:
            return {"methods": [], "region_preferences": []}

        total_revenue = summary["revenue"].sum()
        summary = summary.with_columns(
            (pl.col("revenue") / total_revenue * 100).alias("share_pct")
        )

        top_regions = self._top_regions(region)

        return {
            "methods": summary.to_dicts(),
            "region_preferences": top_regions,
            "total_revenue": float(total_revenue),
        }

    def _top_regions(self, df: pl.DataFrame) -> list[dict[str, Any]]:
        if df.height == 0:
            return []
        top = df.group_by("payment_method").agg(
            pl.col("province", "order_count").sort_by("order_count", descending=True).head(3)
        )
        return top.to_dicts()
