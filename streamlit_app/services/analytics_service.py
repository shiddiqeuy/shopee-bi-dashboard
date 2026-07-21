"""
AnalyticsService — orchestrates analytics computation.

Runs all 8 analytics modules and generates hidden insights.
"""

from __future__ import annotations

from typing import Any, Optional

from analytics.base import AnalyticsEngine
from analytics.cancellation import CancellationAnalytics
from analytics.city import CityAnalytics
from analytics.customer import CustomerAnalytics
from analytics.hidden_insights import HiddenInsightEngine
from analytics.payment import PaymentAnalytics
from analytics.product import ProductAnalytics
from analytics.province import ProvinceAnalytics
from analytics.shipping import ShippingAnalytics
from analytics.trend import TrendAnalytics
from database.repository import DuckDBRepository
from utils.logger import get_logger

log = get_logger(__name__)


class AnalyticsService:
    """Orchestrates all analytics modules and insight generation."""

    def __init__(self, repo: DuckDBRepository) -> None:
        self.repo = repo

    def compute_all(self) -> dict[str, Any]:
        """Run all registered analytics modules.

        Returns the combined results dict with insights.
        """
        engine = AnalyticsEngine(self.repo)
        engine.register(CustomerAnalytics())
        engine.register(ProductAnalytics())
        engine.register(CityAnalytics())
        engine.register(ProvinceAnalytics())
        engine.register(TrendAnalytics())
        engine.register(ShippingAnalytics())
        engine.register(PaymentAnalytics())
        engine.register(CancellationAnalytics())

        results = engine.compute_all()

        insight_engine = HiddenInsightEngine(self.repo)
        insights = insight_engine.generate(results)
        results["insights"] = [ins.__dict__ for ins in insights]

        return results
