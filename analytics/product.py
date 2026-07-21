"""
Product analytics module.

Computes: revenue, quantity, ABC classification, Pareto 80/20,
top products, fast/slow moving, cross-selling candidates, product affinity.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from config.config import ANALYTICS
from core.interfaces import AnalyticsModule, Repository
from utils.logger import get_logger

log = get_logger(__name__)

_SQL_PRODUCT_SUMMARY = """
SELECT
    p.product_name,
    p.product_sku,
    COUNT(DISTINCT f.sales_key) AS order_count,
    SUM(f.quantity) AS total_quantity,
    SUM(f.total_amount) AS total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
WHERE f.order_status != 'cancelled'
GROUP BY p.product_name, p.product_sku
ORDER BY total_revenue DESC
"""

_SQL_PRODUCT_AFFINITY = """
WITH product_pairs AS (
    SELECT
        o1.order_id,
        o1.product_name AS product_a,
        o2.product_name AS product_b
    FROM orders o1
    JOIN orders o2 ON o1.order_id = o2.order_id AND o1.product_name < o2.product_name
    WHERE o1.order_status != 'cancelled'
)
SELECT
    product_a,
    product_b,
    COUNT(DISTINCT order_id) AS co_occurrence
FROM product_pairs
GROUP BY product_a, product_b
ORDER BY co_occurrence DESC
LIMIT 20
"""


class ProductAnalytics(AnalyticsModule):
    """Product performance analytics."""

    @property
    def name(self) -> str:
        return "product"

    def register(self) -> str:
        return self.name

    def compute(self, repo: Repository) -> dict[str, Any]:
        summary = repo.query(_SQL_PRODUCT_SUMMARY)
        if summary.height == 0:
            return {"products": [], "abc": [], "pareto": [], "affinity": []}

        pareto_threshold = ANALYTICS["pareto_threshold"]
        abc_a = ANALYTICS["abc_a_threshold"]
        abc_b = ANALYTICS["abc_b_threshold"]

        total_revenue = summary["total_revenue"].sum()
        summary = summary.with_columns(
            (pl.col("total_revenue") / total_revenue * 100).alias("revenue_pct")
        )
        summary = summary.with_columns(
            pl.col("revenue_pct").cum_sum().alias("cumulative_pct")
        )

        abc = self._abc_classify(summary, abc_a, abc_b)
        pareto = self._pareto_analysis(summary, pareto_threshold)
        affinity = repo.query(_SQL_PRODUCT_AFFINITY).to_dicts()

        top_20 = summary.head(20).to_dicts()
        fast_moving = self._fast_moving(repo)
        slow_moving = self._slow_moving(repo)

        return {
            "products": top_20,
            "abc": abc,
            "pareto": pareto,
            "affinity": affinity,
            "fast_moving": fast_moving,
            "slow_moving": slow_moving,
            "total_products": summary.height,
            "total_revenue": float(total_revenue),
        }

    def _abc_classify(self, df: pl.DataFrame, a_thresh: float, b_thresh: float) -> list[dict[str, Any]]:
        if df.height == 0:
            return []
        result = df.with_columns(
            pl.when(pl.col("cumulative_pct") <= a_thresh * 100)
            .then(pl.lit("A"))
            .when(pl.col("cumulative_pct") <= b_thresh * 100)
            .then(pl.lit("B"))
            .otherwise(pl.lit("C"))
            .alias("classification")
        )
        return result.group_by("classification").agg([
            pl.count().alias("count"),
            pl.sum("total_revenue").alias("revenue"),
        ]).to_dicts()

    def _pareto_analysis(self, df: pl.DataFrame, threshold: float) -> dict[str, Any]:
        pareto_df = df.filter(pl.col("cumulative_pct") <= threshold * 100)
        return {
            "product_count": pareto_df.height,
            "total_products": df.height,
            "revenue_contribution": threshold * 100,
            "pareto_ratio": round(pareto_df.height / df.height * 100, 2) if df.height else 0,
        }

    _SQL_FAST_MOVING = """
        SELECT product_name, SUM(quantity) AS qty_sold
        FROM orders
        WHERE order_status != 'cancelled'
          AND order_date >= CURRENT_DATE - $days
        GROUP BY product_name
        ORDER BY qty_sold DESC
        LIMIT 10
        """

    _SQL_SLOW_MOVING = """
        SELECT product_name, SUM(quantity) AS qty_sold
        FROM orders
        WHERE order_status != 'cancelled'
        GROUP BY product_name
        HAVING MAX(order_date) < CURRENT_DATE - $days
        ORDER BY qty_sold DESC
        LIMIT 10
        """

    def _fast_moving(self, repo: Repository) -> list[dict[str, Any]]:
        days = ANALYTICS["fast_moving_days"]
        return repo.query(self._SQL_FAST_MOVING, {"days": days}).to_dicts()

    def _slow_moving(self, repo: Repository) -> list[dict[str, Any]]:
        days = ANALYTICS["slow_moving_days"]
        return repo.query(self._SQL_SLOW_MOVING, {"days": days}).to_dicts()
