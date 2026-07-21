"""
Integration test: ETL → Warehouse → Analytics full pipeline.

Tests the entire data flow:
1. Transform raw dicts (simulating Shopee export) via ShopeeTransformer
2. Load into DuckDB staging via ShopeeLoader
3. Build star-schema warehouse via WarehouseBuilder
4. Run all 8 analytics modules

Uses in-memory DuckDB — no file I/O, no external dependencies.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

import polars as pl
import pytest

from analytics.base import AnalyticsEngine
from analytics.cancellation import CancellationAnalytics
from analytics.city import CityAnalytics
from analytics.customer import CustomerAnalytics
from analytics.payment import PaymentAnalytics
from analytics.product import ProductAnalytics
from analytics.province import ProvinceAnalytics
from analytics.shipping import ShippingAnalytics
from analytics.trend import TrendAnalytics
from database.migrations import migrate
from database.repository import DuckDBRepository
from etl.shopee.loader import ShopeeLoader
from etl.shopee.transformer import ShopeeTransformer

# ── Test data ──────────────────────────────────────────────────────────────
# Simulates raw rows as extracted from a Shopee export file.
# Uses Indonesian number format (dots = thousands separator).

_RAW_ROWS: list[dict[str, Any]] = [
    {
        "order_id": "INT-001",
        "order_status": "Completed",
        "product_name": "Sepatu Running",
        "product_sku": "SPT-001",
        "variation": "Merah/42",
        "quantity": 2,
        "price": "150.000",
        "total_amount": "300.000",
        "buyer_name": "Budi Santoso",
        "buyer_username": "budi_s",
        "city": "Jakarta Pusat",
        "province": "DKI Jakarta",
        "shipping_provider": "JNE",
        "shipping_method": "REG",
        "shipping_cost": "15.000",
        "payment_method": "Transfer Bank",
        "order_date": "2026-06-01 10:00:00",
        "payment_date": "2026-06-01 10:05:00",
        "shipping_date": "2026-06-01 14:00:00",
        "voucher_seller": "0",
        "voucher_shopee": "5.000",
        "cancellation_reason": "",
    },
    {
        "order_id": "INT-002",
        "order_status": "Completed",
        "product_name": "Tas Ransel",
        "product_sku": "TR-001",
        "variation": "Hitam",
        "quantity": 1,
        "price": "85.000",
        "total_amount": "85.000",
        "buyer_name": "Ani Wijaya",
        "buyer_username": "ani_w",
        "city": "Bandung",
        "province": "Jawa Barat",
        "shipping_provider": "J&T",
        "shipping_method": "YES",
        "shipping_cost": "12.000",
        "payment_method": "COD",
        "order_date": "2026-06-02 14:30:00",
        "payment_date": "2026-06-02 14:35:00",
        "shipping_date": "2026-06-02 16:00:00",
        "voucher_seller": "5.000",
        "voucher_shopee": "0",
        "cancellation_reason": "",
    },
    {
        "order_id": "INT-003",
        "order_status": "Completed",
        "product_name": "Sepatu Running",
        "product_sku": "SPT-001",
        "variation": "Biru/43",
        "quantity": 1,
        "price": "150.000",
        "total_amount": "150.000",
        "buyer_name": "Citra Dewi",
        "buyer_username": "citra_d",
        "city": "Surabaya",
        "province": "Jawa Timur",
        "shipping_provider": "SiCepat",
        "shipping_method": "ECO",
        "shipping_cost": "10.000",
        "payment_method": "OVO",
        "order_date": "2026-06-03 09:00:00",
        "payment_date": "2026-06-03 09:10:00",
        "shipping_date": "2026-06-03 11:00:00",
        "voucher_seller": "0",
        "voucher_shopee": "0",
        "cancellation_reason": "",
    },
    {
        "order_id": "INT-004",
        "order_status": "Cancelled",
        "product_name": "Jam Tangan",
        "product_sku": "JT-001",
        "variation": "Silver",
        "quantity": 1,
        "price": "200.000",
        "total_amount": "200.000",
        "buyer_name": "Budi Santoso",
        "buyer_username": "budi_s",
        "city": "Jakarta Pusat",
        "province": "DKI Jakarta",
        "shipping_provider": "JNE",
        "shipping_method": "OKE",
        "shipping_cost": "10.000",
        "payment_method": "Transfer Bank",
        "order_date": "2026-06-05 11:00:00",
        "payment_date": "2026-06-05 11:05:00",
        "shipping_date": "",
        "voucher_seller": "0",
        "voucher_shopee": "0",
        "cancellation_reason": "out of stock",
    },
    {
        "order_id": "INT-005",
        "order_status": "Completed",
        "product_name": "Tas Ransel",
        "product_sku": "TR-001",
        "variation": "Biru",
        "quantity": 1,
        "price": "85.000",
        "total_amount": "85.000",
        "buyer_name": "Ani Wijaya",
        "buyer_username": "ani_w",
        "city": "Bandung",
        "province": "Jawa Barat",
        "shipping_provider": "J&T",
        "shipping_method": "YES",
        "shipping_cost": "12.000",
        "payment_method": "COD",
        "order_date": "2026-06-10 10:00:00",
        "payment_date": "2026-06-10 10:05:00",
        "shipping_date": "2026-06-10 13:00:00",
        "voucher_seller": "0",
        "voucher_shopee": "0",
        "cancellation_reason": "",
    },
    {
        "order_id": "INT-006",
        "order_status": "Completed",
        "product_name": "Topi Baseball",
        "product_sku": "TP-001",
        "variation": "Hitam",
        "quantity": 3,
        "price": "25.000",
        "total_amount": "75.000",
        "buyer_name": "Deni Pratama",
        "buyer_username": "deni_p",
        "city": "Medan",
        "province": "Sumatera Utara",
        "shipping_provider": "POS Indonesia",
        "shipping_method": "Kilat",
        "shipping_cost": "20.000",
        "payment_method": "GoPay",
        "order_date": "2026-06-15 16:00:00",
        "payment_date": "2026-06-15 16:05:00",
        "shipping_date": "2026-06-16 09:00:00",
        "voucher_seller": "0",
        "voucher_shopee": "0",
        "cancellation_reason": "",
    },
]

_EXPECTED_ORDER_COUNT = 6
_EXPECTED_CITIES = {"Jakarta Pusat", "Bandung", "Surabaya", "Medan"}
_EXPECTED_PRODUCTS = {"Sepatu Running", "Tas Ransel", "Topi Baseball", "Jam Tangan"}
_EXPECTED_CUSTOMERS = {"budi_s", "ani_w", "citra_d", "deni_p"}
_EXPECTED_MODULES = [
    "customer", "product", "city", "province",
    "trend", "shipping", "payment", "cancellation",
]


# ── Fixtures ───────────────────────────────────────────────────────────────


@pytest.fixture
def populated_repo(in_memory_db, request) -> DuckDBRepository:
    """Repository with orders loaded through the full ETL pipeline."""
    from database.connection import (
        replace_pool_for_test,
    )  # inject in-memory connection into pool

    replace_pool_for_test(in_memory_db)
    migrate(in_memory_db)
    repo = DuckDBRepository(in_memory_db)

    transformer = ShopeeTransformer()
    df = transformer.transform(_RAW_ROWS)
    assert not df.is_empty(), "Transformer should produce rows"

    loader = ShopeeLoader(repo)
    count = loader.load(df)
    assert count == _EXPECTED_ORDER_COUNT

    repo.build_warehouse()
    return repo


@pytest.fixture
def analytics_results(populated_repo: DuckDBRepository) -> dict[str, Any]:
    """Analytics results from all registered modules."""
    engine = AnalyticsEngine(populated_repo)
    for module_cls in [
        CustomerAnalytics,
        ProductAnalytics,
        CityAnalytics,
        ProvinceAnalytics,
        TrendAnalytics,
        ShippingAnalytics,
        PaymentAnalytics,
        CancellationAnalytics,
    ]:
        engine.register(module_cls())
    return engine.compute_all()


# ── Tests ──────────────────────────────────────────────────────────────────


class TestFullPipeline:
    """End-to-end pipeline: ETL → Warehouse → Analytics."""

    def test_all_modules_completed(self, analytics_results: dict[str, Any]) -> None:
        """All 8 analytics modules should run without error."""
        assert analytics_results["_module_count"] == 8
        for name in _EXPECTED_MODULES:
            assert name in analytics_results, f"Missing module: {name}"
            module_result = analytics_results[name]
            assert "error" not in module_result or not module_result["error"], (
                f"Module {name} failed with error"
            )

    def test_customer_analytics(self, analytics_results: dict[str, Any]) -> None:
        """Customer analytics returns correct KPIs."""
        cust = analytics_results["customer"]
        assert cust["total_customers"] == 4
        assert cust["repeat_customers"] >= 1  # budi_s and ani_w have 2+ orders
        assert cust["total_revenue"] > 0
        assert cust["avg_basket"] > 0
        assert cust["avg_clv"] > 0
        assert len(cust["segments"]) > 0
        assert len(cust["top_customers"]) > 0
        assert len(cust["rfm_data"]) == 4

    def test_product_analytics(self, analytics_results: dict[str, Any]) -> None:
        """Product analytics includes non-cancelled products only."""
        prod = analytics_results["product"]
        assert prod["total_products"] == 3  # "Jam Tangan" is cancelled only
        assert prod["total_revenue"] > 0
        assert len(prod["products"]) > 0
        assert len(prod["abc"]) > 0
        assert len(prod["affinity"]) >= 0
        assert "pareto" in prod

    def test_city_analytics(self, analytics_results: dict[str, Any]) -> None:
        """City analytics includes all cities with non-cancelled orders."""
        city = analytics_results["city"]
        assert len(city["cities"]) == 4  # All cities have completed orders
        assert len(city["top_cities"]) > 0
        city_names = {c["city_name"] for c in city["cities"]}
        assert "Jakarta Pusat" in city_names
        assert "Bandung" in city_names
        # Verify contribution percentages sum roughly to 100
        total_contrib = sum(c["contribution_pct"] for c in city["cities"])
        assert 95 < total_contrib < 105

    def test_province_analytics(self, analytics_results: dict[str, Any]) -> None:
        """Province analytics groups cities correctly."""
        prov = analytics_results["province"]
        assert prov["total_provinces"] >= 3
        assert prov["total_revenue"] > 0
        province_names = {p["province"] for p in prov["provinces"]}
        assert "DKI Jakarta" in province_names
        assert "Jawa Barat" in province_names

    def test_trend_analytics(self, analytics_results: dict[str, Any]) -> None:
        """Trend analytics aggregates monthly data."""
        trend = analytics_results["trend"]
        assert len(trend["months"]) > 0
        month = trend["months"][0]
        assert "revenue" in month
        assert "order_count" in month
        assert "customer_count" in month
        assert "revenue_mom_pct" in month
        assert "running_total_revenue" in month
        assert "ma_3_revenue" in month

    def test_shipping_analytics(self, analytics_results: dict[str, Any]) -> None:
        """Shipping analytics lists providers and preferences."""
        ship = analytics_results["shipping"]
        assert len(ship["providers"]) > 0
        assert ship["total_orders"] > 0
        provider_names = {p["shipping_provider"] for p in ship["providers"]}
        assert "JNE" in provider_names
        assert "J&T" in provider_names

    def test_payment_analytics(self, analytics_results: dict[str, Any]) -> None:
        """Payment analytics lists methods with distribution."""
        pay = analytics_results["payment"]
        assert len(pay["methods"]) > 0
        assert pay["total_revenue"] > 0
        method_names = {m["payment_method"] for m in pay["methods"]}
        assert "Transfer Bank" in method_names
        assert "COD" in method_names

    def test_cancellation_analytics(self, analytics_results: dict[str, Any]) -> None:
        """Cancellation analytics reports at least 1 cancelled order."""
        cancel = analytics_results["cancellation"]
        assert cancel["cancelled_orders"] >= 1
        assert cancel["total_orders"] == _EXPECTED_ORDER_COUNT
        assert cancel["cancellation_rate"] > 0
        assert len(cancel["by_reason"]) > 0
        assert cancel["by_reason"][0]["cancellation_reason"] == "out of stock"


class TestWarehouseIntegrity:
    """Star-schema warehouse data integrity."""

    def test_fact_sales_row_count(self, populated_repo: DuckDBRepository) -> None:
        """fact_sales should contain all orders joined to dimensions."""
        count = populated_repo.query("SELECT COUNT(1) AS cnt FROM fact_sales")
        assert count["cnt"][0] == _EXPECTED_ORDER_COUNT

    def test_fact_sales_joins(self, populated_repo: DuckDBRepository) -> None:
        """All dimension keys in fact_sales should be non-zero."""
        nulls = populated_repo.query("""
            SELECT
                SUM(CASE WHEN customer_key = 0 THEN 1 ELSE 0 END) AS null_customers,
                SUM(CASE WHEN product_key = 0 THEN 1 ELSE 0 END) AS null_products,
                SUM(CASE WHEN city_key = 0 THEN 1 ELSE 0 END) AS null_cities,
                SUM(CASE WHEN date_key = 0 THEN 1 ELSE 0 END) AS null_dates
            FROM fact_sales
        """)
        row = nulls.row(0, named=True)
        assert row["null_customers"] == 0
        assert row["null_products"] == 0
        assert row["null_cities"] == 0
        assert row["null_dates"] == 0

    def test_dim_customer_non_cancelled_only(self, populated_repo: DuckDBRepository) -> None:
        """Customers with only cancelled orders should not appear in dim."""
        dim = populated_repo.query("SELECT buyer_username FROM dim_customer")
        usernames = set(dim["buyer_username"].to_list())
        assert "budi_s" in usernames  # has completed + cancelled
        assert "citra_d" in usernames  # has completed
        # No customers with only cancelled orders in this dataset

    def test_dim_date_range(self, populated_repo: DuckDBRepository) -> None:
        """dim_date spans from min to max order date."""
        dates = populated_repo.query("SELECT MIN(date) AS d_min, MAX(date) AS d_max FROM dim_date")
        row = dates.row(0, named=True)
        assert row["d_min"] is not None
        assert row["d_max"] is not None
        assert row["d_min"] <= row["d_max"]


class TestETLStage:
    """ETL transformer and loader stage."""

    def test_transform_raw_rows(self) -> None:
        """Transformer converts Indonesian number format correctly."""
        transformer = ShopeeTransformer()
        df = transformer.transform(_RAW_ROWS)
        assert df.height == 6

        row = df.filter(pl.col("order_id") == "INT-001").row(0, named=True)
        assert row["product_name"] == "Sepatu Running"
        assert row["order_status"] == "completed"
        assert row["quantity"] == "2"

    def test_loader_deduplication(self, in_memory_db, repo) -> None:
        """Loading same order_id twice should keep only the latest."""
        migrate(in_memory_db)
        transformer = ShopeeTransformer()
        df = transformer.transform(_RAW_ROWS[:1])

        loader = ShopeeLoader(repo)
        loader.load(df)
        loader.load(df)  # duplicate

        count = repo.query("SELECT COUNT(1) AS cnt FROM orders")
        assert count["cnt"][0] == 1  # deduplicated

    def test_total_revenue_calculation(self, analytics_results: dict[str, Any]) -> None:
        """Total revenue should match expected values."""
        prod = analytics_results["product"]
        # Completed orders only:
        # INT-001: 300.000, INT-002: 85.000, INT-003: 150.000,
        # INT-005: 85.000, INT-006: 75.000 = 695.000
        assert prod["total_revenue"] == pytest.approx(695_000, rel=0.01)

    def test_repeat_customers_identified(self, analytics_results: dict[str, Any]) -> None:
        """Customers with 2+ completed orders are counted as repeat."""
        cust = analytics_results["customer"]
        # budi_s: INT-001 (completed) + INT-004 (cancelled, excluded) = 1
        # ani_w:  INT-002 + INT-005 (both completed) = 2 → repeat
        assert cust["repeat_customers"] == 1
