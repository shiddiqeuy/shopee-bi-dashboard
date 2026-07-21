"""
Province analytics module.

Computes: province ranking, revenue, customer count, contribution, growth.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from core.interfaces import AnalyticsModule, Repository
from utils.logger import get_logger

log = get_logger(__name__)

_SQL_PROVINCE_SUMMARY = """
SELECT
    c.province,
    COUNT(DISTINCT f.sales_key) AS order_count,
    COUNT(DISTINCT f.customer_key) AS customer_count,
    SUM(f.total_amount) AS revenue
FROM fact_sales f
JOIN dim_city c ON f.city_key = c.city_key
WHERE f.order_status != 'cancelled'
GROUP BY c.province
ORDER BY revenue DESC
"""

_SQL_PROVINCE_GROWTH = """
WITH monthly AS (
    SELECT
        c.province,
        STRFTIME(o.order_date, '%Y-%m') AS month,
        SUM(o.total_amount) AS revenue
    FROM orders o
    JOIN dim_city c ON o.city = c.city_name
    WHERE o.order_status != 'cancelled'
    GROUP BY c.province, month
),
ranked AS (
    SELECT *,
        LAG(revenue) OVER (PARTITION BY province ORDER BY month) AS prev_revenue
    FROM monthly
)
SELECT
    province,
    month,
    revenue,
    prev_revenue,
    CASE WHEN prev_revenue > 0 THEN (revenue - prev_revenue) / prev_revenue * 100 ELSE 0 END AS growth_pct
FROM ranked
ORDER BY province, month DESC
"""


class ProvinceAnalytics(AnalyticsModule):
    """Province-level performance analytics."""

    @property
    def name(self) -> str:
        return "province"

    def register(self) -> str:
        return self.name

    def compute(self, repo: Repository) -> dict[str, Any]:
        summary = repo.query(_SQL_PROVINCE_SUMMARY)
        if summary.height == 0:
            return {"provinces": []}

        total_revenue = summary["revenue"].sum()
        summary = summary.with_columns(
            (pl.col("revenue") / total_revenue * 100).alias("contribution_pct")
        )

        growth_df = repo.query(_SQL_PROVINCE_GROWTH)
        latest_growth = self._latest_growth(growth_df)

        summary = summary.with_columns(
            pl.col("province").replace_strict(
                {g["province"]: g["growth_pct"] for g in latest_growth},
                default=0.0,
            ).alias("growth_pct")
        )

        provinces = summary.to_dicts()
        return {
            "provinces": provinces,
            "total_provinces": summary.height,
            "total_revenue": float(total_revenue),
        }

    def _latest_growth(self, df: pl.DataFrame) -> list[dict[str, Any]]:
        if df.height == 0:
            return []
        latest = df.group_by("province").agg(
            pl.col("growth_pct").last()
        )
        return latest.to_dicts()
