"""
Trend analytics module.

Computes: monthly revenue, customer, orders, growth rates,
month-over-month, running total, moving average, seasonality.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from core.interfaces import AnalyticsModule, Repository
from utils.logger import get_logger

log = get_logger(__name__)

_SQL_MONTHLY_REVENUE = """
SELECT
    STRFTIME(order_date, '%Y-%m') AS month,
    SUM(total_amount) AS revenue,
    COUNT(DISTINCT order_id) AS order_count,
    COUNT(DISTINCT buyer_username) AS customer_count
FROM orders
WHERE order_status != 'cancelled'
  AND order_date IS NOT NULL
GROUP BY month
ORDER BY month
"""

_SQL_MONTHLY_CANCELLATION = """
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


class TrendAnalytics(AnalyticsModule):
    """Monthly trend and time-series analytics."""

    @property
    def name(self) -> str:
        return "trend"

    def register(self) -> str:
        return self.name

    def compute(self, repo: Repository) -> dict[str, Any]:
        monthly = repo.query(_SQL_MONTHLY_REVENUE)
        if monthly.height == 0:
            return {"months": []}

        monthly = monthly.with_columns([
            pl.col("revenue").shift(1).alias("prev_revenue"),
            pl.col("order_count").shift(1).alias("prev_orders"),
            pl.col("customer_count").shift(1).alias("prev_customers"),
        ])

        monthly = monthly.with_columns([
            pl.when(pl.col("prev_revenue") > 0)
            .then((pl.col("revenue") - pl.col("prev_revenue")) / pl.col("prev_revenue") * 100)
            .otherwise(0).alias("revenue_mom_pct"),
            pl.when(pl.col("prev_orders") > 0)
            .then((pl.col("order_count") - pl.col("prev_orders")) / pl.col("prev_orders") * 100)
            .otherwise(0).alias("orders_mom_pct"),
            pl.when(pl.col("prev_customers") > 0)
            .then((pl.col("customer_count") - pl.col("prev_customers")) / pl.col("prev_customers") * 100)
            .otherwise(0).alias("customers_mom_pct"),
        ])

        monthly = monthly.with_columns([
            pl.col("revenue").cum_sum().alias("running_total_revenue"),
            pl.col("order_count").cum_sum().alias("running_total_orders"),
        ])

        window = 3
        monthly = monthly.with_columns([
            pl.col("revenue").shift(0).rolling_mean(window_size=window).alias("ma_3_revenue"),
            pl.col("order_count").shift(0).rolling_mean(window_size=window).alias("ma_3_orders"),
        ])

        cancel_df = repo.query(_SQL_MONTHLY_CANCELLATION)
        months = monthly.to_dicts()
        cancel_map = {r["month"]: r for r in cancel_df.to_dicts()}

        for m in months:
            c = cancel_map.get(m["month"], {})
            m["cancelled_orders"] = c.get("cancelled_orders", 0)
            m["cancelled_revenue"] = float(c.get("cancelled_revenue", 0))

        return {"months": months}
