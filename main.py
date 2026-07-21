"""
Shopee BI Dashboard — CLI entry point.

Usage:
    python main.py                  # Full pipeline: ETL → Warehouse → Analytics → Dashboard
    python main.py --etl-only       # ETL only
    python main.py --analytics-only # Analytics only (requires existing warehouse)
    python main.py --dashboard-only # Dashboard only (requires existing analytics cache)
    python main.py --list-files     # List files in input/ directory
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from config.config import INPUT_DIR
from database.connection import close_connection, get_connection
from database.migrations import migrate
from database.repository import DuckDBRepository
from utils.logger import get_logger

log = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Shopee BI Dashboard — automated marketplace analytics",
    )
    parser.add_argument("--etl-only", action="store_true", help="Run ETL only")
    parser.add_argument("--analytics-only", action="store_true", help="Run analytics only")
    parser.add_argument("--dashboard-only", action="store_true", help="Generate dashboard only")
    parser.add_argument("--list-files", action="store_true", help="List input files and exit")
    return parser.parse_args()


def list_input_files() -> None:
    files = sorted(INPUT_DIR.glob("*.*"))
    if not files:
        print(f"No files found in {INPUT_DIR}")
        return
    print(f"Files in {INPUT_DIR}:")
    for f in files:
        size = f.stat().st_size
        print(f"  {f.name} ({size:,} bytes)")


def run_etl(repo: DuckDBRepository) -> None:
    from etl.base import ETLRunner
    from etl.shopee.pipeline import ShopeeETLPipeline

    migrate(get_connection())

    shopee_pipeline = ShopeeETLPipeline(repo)
    runner = ETLRunner(INPUT_DIR, shopee_pipeline.loader)
    runner.register("shopee", shopee_pipeline)

    total = runner.run_all()
    log.info("ETL complete: %d total rows loaded", total)

    if total > 0:
        repo.build_warehouse()


def run_analytics(repo: DuckDBRepository) -> dict[str, Any]:
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

    engine = AnalyticsEngine(repo)
    engine.register(CustomerAnalytics())
    engine.register(ProductAnalytics())
    engine.register(CityAnalytics())
    engine.register(ProvinceAnalytics())
    engine.register(TrendAnalytics())
    engine.register(ShippingAnalytics())
    engine.register(PaymentAnalytics())
    engine.register(CancellationAnalytics())

    results = engine.compute_all()

    insight_engine = HiddenInsightEngine(repo)
    results["insights"] = [
        ins.__dict__ for ins in insight_engine.generate(results)
    ]

    raw_df = repo.query("SELECT * FROM orders LIMIT 5000")
    results["raw_data"] = raw_df.to_dicts()

    log.info("Analytics complete: %d modules, %d insights", results["_module_count"], len(results["insights"]))
    return results


def run_dashboard(repo: DuckDBRepository, analytics: dict[str, Any]) -> str:
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

    builder = ExcelDashboardBuilder(repo)
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

    path = builder.build(analytics)
    log.info("Dashboard generated: %s", path)
    return path


def main() -> None:
    args = parse_args()

    if args.list_files:
        list_input_files()
        return

    repo = DuckDBRepository()

    try:
        if args.analytics_only:
            results = run_analytics(repo)
            print(f"Analytics computed: {results['_module_count']} modules, {len(results.get('insights', []))} insights")
        elif args.dashboard_only:
            results = run_analytics(repo)
            path = run_dashboard(repo, results)
            print(f"Dashboard saved: {path}")
        elif args.etl_only:
            run_etl(repo)
            print("ETL complete.")
        else:
            run_etl(repo)
            results = run_analytics(repo)
            path = run_dashboard(repo, results)
            print("\nFull pipeline complete!")
            print(f"  Dashboard: {path}")
            print(f"  Modules:   {results['_module_count']}")
            print(f"  Insights:  {len(results.get('insights', []))}")

    except Exception:
        log.exception("Pipeline failed")
        sys.exit(1)
    finally:
        close_connection()


if __name__ == "__main__":
    main()
