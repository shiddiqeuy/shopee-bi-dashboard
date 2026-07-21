"""
Customer analytics module.

Computes: unique customers, repeat rate, CLV, RFM scores,
customer segmentation, top customers, order frequency, avg basket.
"""

from __future__ import annotations

from typing import Any

import polars as pl

from core.interfaces import AnalyticsModule, Repository
from utils.logger import get_logger

log = get_logger(__name__)

_SQL_CUSTOMER_SUMMARY = """
SELECT
    c.buyer_username,
    c.buyer_name,
    c.first_order_date,
    c.last_order_date,
    c.total_orders,
    c.total_revenue,
    c.city,
    c.province
FROM dim_customer c
ORDER BY c.total_revenue DESC
"""

_SQL_REPEAT_CUSTOMERS = """
SELECT
    buyer_username,
    total_orders,
    CASE WHEN total_orders >= 2 THEN 1 ELSE 0 END AS is_repeat
FROM dim_customer
"""

_SQL_ORDER_FREQ = """
SELECT
    buyer_username,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(total_amount) AS total_spent,
    DATEDIFF('day', MIN(order_date), MAX(order_date)) AS days_span
FROM orders
WHERE order_status != 'cancelled'
GROUP BY buyer_username
"""

_SQL_RFM = """
WITH rfm_raw AS (
    SELECT
        buyer_username,
        DATEDIFF('day', MAX(order_date), CURRENT_DATE) AS recency,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(total_amount) AS monetary
    FROM orders
    WHERE order_status != 'cancelled'
    GROUP BY buyer_username
)
SELECT * FROM rfm_raw
"""


class CustomerAnalytics(AnalyticsModule):
    """Customer behaviour and segmentation analytics."""

    @property
    def name(self) -> str:
        return "customer"

    def register(self) -> str:
        return self.name

    def compute(self, repo: Repository) -> dict[str, Any]:
        if not repo.table_exists("dim_customer"):
            return self._empty_result()

        summary = repo.query(_SQL_CUSTOMER_SUMMARY)
        rfm = repo.query(_SQL_RFM)
        repeat_df = repo.query(_SQL_REPEAT_CUSTOMERS)

        total_customers = summary.height
        total_repeat = repeat_df.filter(pl.col("is_repeat") == 1).height
        total_new = total_customers - total_repeat
        repeat_rate = round(total_repeat / total_customers * 100, 2) if total_customers else 0.0
        total_revenue = summary["total_revenue"].sum()
        avg_basket = round(total_revenue / summary["total_orders"].sum(), 2) if summary.height else 0.0
        avg_clv = round(total_revenue / total_customers, 2) if total_customers else 0.0

        rfm_scored = self._compute_rfm_scores(rfm)
        segments = self._segment_customers(rfm_scored)

        top_10 = summary.head(10).to_dicts()
        segment_counts = self._count_segments(segments)

        return {
            "total_customers": total_customers,
            "repeat_customers": total_repeat,
            "new_customers": total_new,
            "repeat_rate": repeat_rate,
            "total_revenue": float(total_revenue),
            "avg_basket": float(avg_basket),
            "avg_clv": float(avg_clv),
            "top_customers": top_10,
            "segments": segment_counts,
            "rfm_data": rfm_scored.to_dicts(),
        }

    def _empty_result(self) -> dict[str, Any]:
        return {
            "total_customers": 0,
            "repeat_customers": 0,
            "new_customers": 0,
            "repeat_rate": 0.0,
            "total_revenue": 0.0,
            "avg_basket": 0.0,
            "avg_clv": 0.0,
            "top_customers": [],
            "segments": [],
            "rfm_data": [],
        }

    def _compute_rfm_scores(self, rfm: pl.DataFrame) -> pl.DataFrame:
        if rfm.height == 0:
            return rfm
        rfm = rfm.with_columns([
            pl.col("recency").rank(method="min").alias("r_rank"),
            pl.col("frequency").rank(method="min", descending=True).alias("f_rank"),
            pl.col("monetary").rank(method="min", descending=True).alias("m_rank"),
        ])
        total = rfm.height
        rfm = rfm.with_columns([
            (pl.col("r_rank") / total * 4 + 1).cast(pl.Int32).alias("r_score"),
            (pl.col("f_rank") / total * 4 + 1).cast(pl.Int32).alias("f_score"),
            (pl.col("m_rank") / total * 4 + 1).cast(pl.Int32).alias("m_score"),
        ])
        rfm = rfm.with_columns(
            (pl.col("r_score") * 100 + pl.col("f_score") * 10 + pl.col("m_score")).alias("rfm_score")
        )
        return rfm

    def _segment_customers(self, rfm: pl.DataFrame) -> pl.DataFrame:
        if rfm.height == 0:
            return rfm
        result = rfm.with_columns(
            pl.when((pl.col("r_score") >= 4) & (pl.col("f_score") >= 4))
            .then(pl.lit("Champion"))
            .when((pl.col("r_score") >= 3) & (pl.col("f_score") >= 3))
            .then(pl.lit("Loyal"))
            .when((pl.col("r_score") >= 3) & (pl.col("f_score") <= 2))
            .then(pl.lit("Potential"))
            .when((pl.col("r_score") >= 2) & (pl.col("f_score") >= 3))
            .then(pl.lit("Needs Attention"))
            .when((pl.col("r_score") <= 2) & (pl.col("f_score") >= 2))
            .then(pl.lit("At Risk"))
            .when((pl.col("r_score") <= 2) & (pl.col("f_score") <= 2))
            .then(pl.lit("Lost"))
            .otherwise(pl.lit("Other"))
            .alias("segment")
        )
        return result

    def _count_segments(self, segmented: pl.DataFrame) -> list[dict[str, Any]]:
        if segmented.height == 0:
            return []
        seg_order = ["Champion", "Loyal", "Potential", "Needs Attention", "At Risk", "Lost"]
        counts = (segmented
                  .group_by("segment")
                  .agg(pl.len().alias("count")))
        order_map = {s: i for i, s in enumerate(seg_order)}
        result = sorted(counts.to_dicts(), key=lambda x: order_map.get(x.get("segment", ""), 99))
        return result
