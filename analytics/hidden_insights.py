"""
Hidden Insight Engine.

Automatically detects business opportunities, risks, and anomalies
from the computed analytics data. Writes recommendations in the
style of a management consultant.
"""

from __future__ import annotations

from typing import Any

from core.entities import Insight
from core.interfaces import InsightEngine, Repository
from utils.logger import get_logger

log = get_logger(__name__)


class HiddenInsightEngine(InsightEngine):
    """Generates actionable business insights from analytics results."""

    def __init__(self, repository: Repository) -> None:
        self.repo = repository

    def generate(self, analytics: dict[str, Any]) -> list[Insight]:
        insights: list[Insight] = []

        if "city" in analytics:
            insights.extend(self._city_insights(analytics["city"]))
        if "product" in analytics:
            insights.extend(self._product_insights(analytics["product"]))
        if "customer" in analytics:
            insights.extend(self._customer_insights(analytics["customer"]))
        if "cancellation" in analytics:
            insights.extend(self._cancellation_insights(analytics["cancellation"]))
        if "trend" in analytics:
            insights.extend(self._trend_insights(analytics["trend"]))

        insights.sort(key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x.priority, 1))
        return insights

    def _city_insights(self, city_data: dict[str, Any]) -> list[Insight]:
        result: list[Insight] = []
        cities = city_data.get("cities", [])
        if not cities:
            return result

        cities_sorted = sorted(cities, key=lambda c: c.get("growth_pct", 0), reverse=True)
        for c in cities_sorted[:3]:
            growth = c.get("growth_pct", 0)
            if growth > 20:
                result.append(Insight(
                    type="opportunity",
                    title=f"Top Growing City: {c['city_name']}",
                    description=(
                        f"{c['city_name']} is growing at {growth:.1f}% with "
                        f"{c.get('customer_count', 0)} customers. "
                        "Consider increasing marketing spend and inventory allocation."
                    ),
                    metric_value=growth,
                    dimension=c["city_name"],
                    recommendation=f"Increase ad spend in {c['city_name']} by 30% and add 2 new product variants.",
                    priority="high",
                ))

        for c in cities_sorted:
            rev = c.get("revenue", 0)
            repeat = c.get("repeat_rate", 0)
            if rev > 10000000 and repeat < 10:
                result.append(Insight(
                    type="risk",
                    title=f"High Revenue, Low Repeat: {c['city_name']}",
                    description=(
                        f"{c['city_name']} generates Rp {rev:,.0f} revenue but "
                        f"only {repeat:.1f}% repeat rate. Customers buy once but don't return."
                    ),
                    metric_value=repeat,
                    dimension=c["city_name"],
                    recommendation="Launch a loyalty program and post-purchase email sequence in this city.",
                    priority="high",
                ))
                break

        return result

    def _product_insights(self, product_data: dict[str, Any]) -> list[Insight]:
        result: list[Insight] = []
        products = product_data.get("products", [])
        if not products:
            return result

        for p in products[:3]:
            result.append(Insight(
                type="hidden_potential",
                title=f"Top Performer: {p['product_name']}",
                description=(
                    f"Revenue Rp {p.get('total_revenue', 0):,.0f} from "
                    f"{p.get('order_count', 0)} orders."
                ),
                metric_value=float(p.get("total_revenue", 0)),
                dimension=p["product_name"],
                recommendation="Feature this product in the homepage banner and bundle with accessories.",
                priority="high",
            ))

        pareto = product_data.get("pareto", {})
        if pareto.get("pareto_ratio", 0) > 0:
            result.append(Insight(
                type="recommendation",
                title="Pareto 80/20 Product Concentration",
                description=(
                    f"Top {pareto.get('product_count', 0)} products contribute "
                    f"{pareto.get('revenue_contribution', 0)}% of revenue. "
                    "Long tail needs activation."
                ),
                metric_value=pareto.get("pareto_ratio", 0),
                dimension="product_portfolio",
                recommendation="Run a 'discover new items' promo for bottom 50% products to activate long tail.",
                priority="medium",
            ))

        return result

    def _customer_insights(self, customer_data: dict[str, Any]) -> list[Insight]:
        result: list[Insight] = []
        segments = customer_data.get("segments", [])
        for seg in segments:
            if seg["segment"] == "At Risk" and seg["count"] > 0:
                result.append(Insight(
                    type="risk",
                    title=f"{seg['count']} Customers At Risk of Churning",
                    description=(
                        f"{seg['count']} customers have low recency and frequency. "
                        "They are about to churn."
                    ),
                    metric_value=float(seg["count"]),
                    dimension="customer_retention",
                    recommendation="Send a 'we miss you' voucher campaign to all At Risk customers immediately.",
                    priority="high",
                ))
            if seg["segment"] == "Champion" and seg["count"] > 0:
                result.append(Insight(
                    type="opportunity",
                    title=f"{seg['count']} Champion Customers Identified",
                    description=f"Your best customers. Nurture them.",
                    metric_value=float(seg["count"]),
                    dimension="customer_loyalty",
                    recommendation="Create a VIP loyalty tier with exclusive early access and free shipping.",
                    priority="medium",
                ))

        repeat_rate = customer_data.get("repeat_rate", 0)
        if repeat_rate < 15:
            result.append(Insight(
                type="risk",
                title="Low Repeat Purchase Rate",
                description=f"Only {repeat_rate:.1f}% of customers repurchase. Industry benchmark is 20-30%.",
                metric_value=repeat_rate,
                dimension="repeat_rate",
                recommendation="Implement a post-purchase email sequence with product recommendations.",
                priority="high",
            ))

        return result

    def _cancellation_insights(self, cancel_data: dict[str, Any]) -> list[Insight]:
        result: list[Insight] = []
        rate = cancel_data.get("cancellation_rate", 0)
        if rate > 10:
            result.append(Insight(
                type="risk",
                title=f"High Cancellation Rate: {rate:.1f}%",
                description="Cancellation rate exceeds 10%. Investigate root causes.",
                metric_value=rate,
                dimension="cancellation",
                recommendation="Audit top cancellation reasons and address inventory accuracy.",
                priority="high",
            ))
        by_reason = cancel_data.get("by_reason", [])
        if by_reason:
            top_reason = by_reason[0]
            result.append(Insight(
                type="anomaly",
                title=f"Top Cancellation Reason: {top_reason.get('cancellation_reason', 'N/A')}",
                description=(
                    f"{top_reason.get('cancelled_orders', 0)} orders cancelled due to "
                    f"'{top_reason.get('cancellation_reason', 'Unknown')}'."
                ),
                metric_value=float(top_reason.get("cancelled_orders", 0)),
                dimension="cancellation_reason",
                recommendation=f"Address '{top_reason.get('cancellation_reason', 'N/A')}' — review product descriptions and stock accuracy.",
                priority="medium",
            ))
        return result

    def _trend_insights(self, trend_data: dict[str, Any]) -> list[Insight]:
        result: list[Insight] = []
        months = trend_data.get("months", [])
        if len(months) >= 2:
            last = months[-1]
            prev = months[-2]
            mom = last.get("revenue_mom_pct", 0)
            if mom < -20:
                result.append(Insight(
                    type="risk",
                    title=f"Revenue Dropped {mom:.1f}% MoM",
                    description=f"Revenue declined from {prev.get('month')} to {last.get('month')}.",
                    metric_value=mom,
                    dimension="revenue_trend",
                    recommendation="Investigate cause: seasonality, competitor activity, or marketing gap.",
                    priority="high",
                ))
            elif mom > 30:
                result.append(Insight(
                    type="opportunity",
                    title=f"Revenue Surged {mom:.1f}% MoM",
                    description=f"Strong growth from {prev.get('month')} to {last.get('month')}.",
                    metric_value=mom,
                    dimension="revenue_trend",
                    recommendation="Analyze what drove the surge and replicate the strategy.",
                    priority="medium",
                ))
        return result
