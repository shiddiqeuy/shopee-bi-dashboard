"""
City analytics module.

Computes: revenue per city, orders, customers, repeat rate, contribution,
top products per city, average order value, growth, opportunity & potential scores.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from config.config import ANALYTICS
from core.interfaces import AnalyticsModule, Repository
from utils.logger import get_logger

log = get_logger(__name__)

_SQL_CITY_SUMMARY = """
SELECT
    c.city_name,
    c.province,
    COUNT(DISTINCT f.sales_key) AS order_count,
    COUNT(DISTINCT f.customer_key) AS customer_count,
    SUM(f.total_amount) AS revenue
FROM fact_sales f
JOIN dim_city c ON f.city_key = c.city_key
WHERE f.order_status != 'cancelled'
GROUP BY c.city_name, c.province
ORDER BY revenue DESC
"""

_SQL_CITY_REPEAT = """
SELECT
    city,
    buyer_username,
    COUNT(DISTINCT order_id) AS order_count
FROM orders
WHERE order_status != 'cancelled'
GROUP BY city, buyer_username
"""

_SQL_CITY_TOP_PRODUCTS = """
SELECT
    o.city,
    o.product_name,
    SUM(o.total_amount) AS revenue
FROM orders o
WHERE o.order_status != 'cancelled'
GROUP BY o.city, o.product_name
ORDER BY o.city, revenue DESC
"""

_SQL_CITY_GROWTH = """
WITH monthly AS (
    SELECT
        o.city,
        STRFTIME(o.order_date, '%Y-%m') AS month,
        SUM(o.total_amount) AS revenue
    FROM orders o
    WHERE o.order_status != 'cancelled'
    GROUP BY o.city, month
),
ranked AS (
    SELECT *,
        LAG(revenue) OVER (PARTITION BY city ORDER BY month) AS prev_revenue
    FROM monthly
)
SELECT
    city,
    month,
    revenue,
    prev_revenue,
    CASE WHEN prev_revenue > 0 THEN (revenue - prev_revenue) / prev_revenue * 100 ELSE 0 END AS growth_pct
FROM ranked
ORDER BY city, month DESC
"""


class CityAnalytics(AnalyticsModule):
    """City-level geographic performance analytics."""

    @property
    def name(self) -> str:
        return "city"

    def register(self) -> str:
        return self.name

    def compute(self, repo: Repository) -> dict[str, Any]:
        summary = repo.query(_SQL_CITY_SUMMARY)
        if summary.height == 0:
            return {"cities": [], "top_cities": []}

        total_revenue = summary["revenue"].sum()
        summary = summary.with_columns(
            (pl.col("revenue") / total_revenue * 100).alias("contribution_pct")
        )

        repeat_df = repo.query(_SQL_CITY_REPEAT)
        repeat_rates = self._compute_repeat_rates(repeat_df)
        summary = summary.with_columns(
            pl.col("city_name").replace_strict(
                {r["city"]: r["repeat_rate"] for r in repeat_rates},
                default=0.0,
            ).alias("repeat_rate")
        )

        top_products_df = repo.query(_SQL_CITY_TOP_PRODUCTS)
        top_3 = self._top_3_products(top_products_df)

        growth_df = repo.query(_SQL_CITY_GROWTH)
        latest_growth = self._latest_growth(growth_df)

        summary = summary.with_columns(
            pl.col("city_name").replace_strict(
                {g["city"]: g["growth_pct"] for g in latest_growth},
                default=0.0,
            ).alias("growth_pct")
        )
        summary = summary.with_columns(
            (pl.col("revenue") / pl.col("order_count")).alias("avg_order_value")
        )

        weights = ANALYTICS["opportunity_score_weight"]
        summary = summary.with_columns(
            (
                pl.col("growth_pct") * weights["revenue_growth"]
                + pl.col("customer_count") * weights["customer_growth"]
                + pl.col("repeat_rate") * weights["repeat_rate"]
                + pl.col("avg_order_value") * weights["avg_basket"]
            ).alias("opportunity_score")
        )

        cities = summary.to_dicts()
        for c in cities:
            c["top_products"] = top_3.get(c["city_name"], [])

        return {
            "cities": cities,
            "top_cities": summary.head(20).to_dicts(),
        }

    def _compute_repeat_rates(self, df: pl.DataFrame) -> list[dict[str, Any]]:
        if df.height == 0:
            return []
        rates = df.group_by("city").agg([
            pl.count("buyer_username").alias("total_customers"),
            (pl.col("order_count") >= 2).sum().alias("repeat_customers"),
        ]).with_columns(
            (pl.col("repeat_customers") / pl.col("total_customers") * 100).alias("repeat_rate")
        )
        return rates.to_dicts()

    def _top_3_products(self, df: pl.DataFrame) -> dict[str, list[dict[str, Any]]]:
        result: dict[str, list[dict[str, Any]]] = {}
        for row in df.group_by("city").agg(
            pl.col("product_name", "revenue").sort_by("revenue", descending=True).head(3)
        ).to_dicts():
            result[row["city"]] = row["product_name"]
        return result

    def _latest_growth(self, df: pl.DataFrame) -> list[dict[str, Any]]:
        if df.height == 0:
            return []
        latest = df.group_by("city").agg(
            pl.col("growth_pct").last()
        )
        return latest.to_dicts()
