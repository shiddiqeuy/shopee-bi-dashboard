"""
DashboardService — generates the Excel dashboard from analytics results.

Reuses the existing Excel dashboard builder.
"""

from __future__ import annotations

from typing import Any, Optional

from database.repository import DuckDBRepository
from utils.logger import get_logger

log = get_logger(__name__)


class DashboardService:
    """Generates the downloadable Excel dashboard."""

    def __init__(self, repo: DuckDBRepository) -> None:
        self.repo = repo

    def generate(self, analytics: dict[str, Any]) -> str:
        """Generate Excel dashboard and return file path."""
        from dashboard.builder import ExcelDashboardBuilder
        from dashboard.sheets.cancellation import CancellationSheet
        from dashboard.sheets.city_performance import CityPerformanceSheet
        from dashboard.sheets.customer_behaviour import CustomerBehaviourSheet
        from dashboard.sheets.executive import ExecutiveSheet
        from dashboard.sheets.hidden_insight import HiddenInsightSheet
        from dashboard.sheets.kpi import KPISummarySheet
        from dashboard.sheets.methodology import MethodologySheet
        from dashboard.sheets.monthly_trend import MonthlyTrendSheet
        from dashboard.sheets.payment import PaymentSheet
        from dashboard.sheets.product_performance import ProductPerformanceSheet
        from dashboard.sheets.province_performance import ProvincePerformanceSheet
        from dashboard.sheets.raw_data import RawDataSheet
        from dashboard.sheets.shipping import ShippingSheet

        builder = ExcelDashboardBuilder(self.repo)
        builder.register(ExecutiveSheet())
        builder.register(KPISummarySheet())
        builder.register(CityPerformanceSheet())
        builder.register(ProvincePerformanceSheet())
        builder.register(ProductPerformanceSheet())
        builder.register(CustomerBehaviourSheet())
        builder.register(MonthlyTrendSheet())
        builder.register(ShippingSheet())
        builder.register(PaymentSheet())
        builder.register(CancellationSheet())
        builder.register(HiddenInsightSheet())
        builder.register(RawDataSheet())
        builder.register(MethodologySheet())

        return builder.build(analytics)
