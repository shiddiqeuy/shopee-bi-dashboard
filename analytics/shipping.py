"""
Shipping analytics module.

Computes: courier performance, shipping method preference,
average shipping cost, shipping performance metrics.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from core.interfaces import AnalyticsModule, Repository
from utils.logger import get_logger

log = get_logger(__name__)

_SQL_SHIPPING_SUMMARY = """
SELECT
    shipping_provider,
    shipping_method,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(shipping_cost) AS total_cost,
    AVG(shipping_cost) AS avg_cost
FROM orders
WHERE shipping_provider IS NOT NULL
  AND shipping_provider != ''
GROUP BY shipping_provider, shipping_method
ORDER BY order_count DESC
"""

_SQL_SHIPPING_PREF = """
SELECT
    shipping_provider,
    city,
    COUNT(DISTINCT order_id) AS order_count
FROM orders
WHERE shipping_provider IS NOT NULL AND shipping_provider != ''
GROUP BY shipping_provider, city
ORDER BY shipping_provider, order_count DESC
"""


class ShippingAnalytics(AnalyticsModule):
    """Shipping provider and courier analytics."""

    @property
    def name(self) -> str:
        return "shipping"

    def register(self) -> str:
        return self.name

    def compute(self, repo: Repository) -> dict[str, Any]:
        summary = repo.query(_SQL_SHIPPING_SUMMARY)
        preferences = repo.query(_SQL_SHIPPING_PREF)

        if summary.height == 0:
            return {"providers": [], "preferences": []}

        total_orders = summary["order_count"].sum()
        summary = summary.with_columns(
            (pl.col("order_count") / total_orders * 100).alias("share_pct")
        )

        top_prefs = self._top_preferences(preferences)

        return {
            "providers": summary.to_dicts(),
            "preferences": top_prefs,
            "total_orders": int(total_orders),
        }

    def _top_preferences(self, df: pl.DataFrame) -> list[dict[str, Any]]:
        if df.height == 0:
            return []
        top = df.group_by("shipping_provider").agg(
            pl.col("city", "order_count").sort_by("order_count", descending=True).head(3)
        )
        return top.to_dicts()
