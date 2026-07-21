"""
Dashboard page — KPI cards, charts, and insights.

This is the main analytics view of the application.
"""

from __future__ import annotations

from typing import Any, Optional

import altair as alt
import polars as pl
import streamlit as st

from config.config import THEME
from database.connection import get_connection
from database.repository import DuckDBRepository
from streamlit_app.components.chart_card import chart_card
from streamlit_app.components.data_table import data_table
from streamlit_app.components.metric_card import metric_card


def _get_repo() -> DuckDBRepository:
    return DuckDBRepository(get_connection())


def _load_analytics() -> Optional[dict[str, Any]]:
    """Compute and cache analytics results."""
    repo = _get_repo()
    if not repo.table_exists("fact_sales"):
        return None
    from streamlit_app.services.analytics_service import AnalyticsService

    service = AnalyticsService(repo)
    return service.compute_all()


def _format_rp(value: float) -> str:
    if value >= 1_000_000_000:
        return f"Rp {value/1_000_000_000:.1f}B"
    if value >= 1_000_000:
        return f"Rp {value/1_000_000:.1f}M"
    return f"Rp {value:,.0f}"


def _render_kpis(analytics: dict[str, Any]) -> None:
    cust = analytics.get("customer", {})
    prod = analytics.get("product", {})
    cancel = analytics.get("cancellation", {})

    kpi_data = [
        ("Total Revenue", _format_rp(cust.get("total_revenue", 0)), "Revenue from all completed orders"),
        ("Total Orders", f"{cancel.get('total_orders', 0):,}", "All orders including cancelled"),
        ("Total Customers", f"{cust.get('total_customers', 0):,}", "Unique buyers"),
        ("Avg Order Value", _format_rp(cust.get("avg_basket", 0)), "Revenue ÷ orders"),
        ("Repeat Rate", f"{cust.get('repeat_rate', 0):.1f}%", "Customers with 2+ orders"),
        ("Cancellation", f"{cancel.get('cancellation_rate', 0):.1f}%", "Orders cancelled"),
    ]

    cols = st.columns(6)
    for col, (label, value, help_text) in zip(cols, kpi_data):
        with col:
            metric_card(label, value, help_text=help_text)


def _render_insights(analytics: dict[str, Any]) -> None:
    insights = analytics.get("insights", [])
    if not insights:
        return

    st.markdown("### 💡 Business Insights")

    high = [i for i in insights if i.get("priority") == "high"]
    medium = [i for i in insights if i.get("priority") == "medium"]

    for ins in high[:3]:
        with st.container(border=True):
            st.markdown(
                f"<span style='background:#fee2e2; color:#dc2626; padding:2px 8px; "
                f"border-radius:4px; font-size:0.7rem; font-weight:600;'>{ins.get('type', '').upper()}</span> "
                f"<strong>{ins.get('title', '')}</strong>",
                unsafe_allow_html=True,
            )
            st.markdown(ins.get("description", ""))
            if ins.get("recommendation"):
                st.markdown(f"💡 *{ins['recommendation']}*")

    for ins in medium[:2]:
        with st.container(border=True):
            st.markdown(
                f"<span style='background:#fef3c7; color:#d97706; padding:2px 8px; "
                f"border-radius:4px; font-size:0.7rem; font-weight:600;'>{ins.get('type', '').upper()}</span> "
                f"<strong>{ins.get('title', '')}</strong>",
                unsafe_allow_html=True,
            )
            st.markdown(ins.get("description", ""))


def _render_revenue_trend(analytics: dict[str, Any]) -> None:
    months = analytics.get("trend", {}).get("months", [])
    if not months:
        return
    df = pl.DataFrame(months).with_columns(
        pl.col("revenue").cast(pl.Float64).alias("revenue_f64"),
    )
    chart = (
        alt.Chart(df.to_pandas())
        .mark_line(point=True, strokeWidth=2.5, color="#1B98F5")
        .encode(
            x=alt.X("month:N", title=None, sort=None),
            y=alt.Y("revenue_f64:Q", title="Revenue", axis=alt.Axis(format="~s")),
            tooltip=["month", alt.Tooltip("revenue_f64", format=",.0f")],
        )
        .properties(height=300)
    )
    chart_card("Revenue Trend", chart)


def _render_monthly_orders(analytics: dict[str, Any]) -> None:
    months = analytics.get("trend", {}).get("months", [])
    if not months:
        return
    df = pl.DataFrame(months)
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar(color="#00C9A7")
        .encode(
            x=alt.X("month:N", title=None, sort=None),
            y=alt.Y("order_count:Q", title="Orders"),
            tooltip=["month", "order_count"],
        )
        .properties(height=250)
    )
    chart_card("Monthly Orders", chart)


def _render_top_products(analytics: dict[str, Any]) -> None:
    products = analytics.get("product", {}).get("products", [])
    if not products:
        return
    df = pl.DataFrame(products[:10]).with_columns(
        pl.col("total_revenue").cast(pl.Float64).alias("revenue_f64"),
    )
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar(color="#1B98F5")
        .encode(
            y=alt.Y("product_name:N", title=None, sort="-x"),
            x=alt.X("revenue_f64:Q", title="Revenue", axis=alt.Axis(format="~s")),
            tooltip=["product_name", alt.Tooltip("revenue_f64", format=",.0f")],
        )
        .properties(height=300)
    )
    chart_card("Top Products by Revenue", chart)


def _render_province_performance(analytics: dict[str, Any]) -> None:
    provinces = analytics.get("province", {}).get("provinces", [])
    if not provinces:
        return
    df = pl.DataFrame(provinces).with_columns(
        pl.col("revenue").cast(pl.Float64).alias("revenue_f64"),
    )
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar(color="#0B6FA6")
        .encode(
            y=alt.Y("province:N", title=None, sort="-x"),
            x=alt.X("revenue_f64:Q", title="Revenue", axis=alt.Axis(format="~s")),
            tooltip=["province", alt.Tooltip("revenue_f64", format=",.0f")],
        )
        .properties(height=250)
    )
    chart_card("Province Performance", chart)


def _render_city_performance(analytics: dict[str, Any]) -> None:
    cities = analytics.get("city", {}).get("cities", [])
    if not cities:
        return
    df = pl.DataFrame(cities).with_columns(
        pl.col("revenue").cast(pl.Float64).alias("revenue_f64"),
    )
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar(color="#00C9A7")
        .encode(
            y=alt.Y("city_name:N", title=None, sort="-x"),
            x=alt.X("revenue_f64:Q", title="Revenue", axis=alt.Axis(format="~s")),
            tooltip=["city_name", alt.Tooltip("revenue_f64", format=",.0f")],
        )
        .properties(height=300)
    )
    chart_card("City Performance", chart)


def _render_customer_segments(analytics: dict[str, Any]) -> None:
    segments = analytics.get("customer", {}).get("segments", [])
    if not segments:
        return
    df = pl.DataFrame(segments)
    colors = ["#1B98F5", "#00C9A7", "#FFB74D", "#FF6B6B", "#A29BFE", "#FD79A8"]
    chart = (
        alt.Chart(df.to_pandas())
        .mark_arc(innerRadius=50)
        .encode(
            theta=alt.Theta("count:Q"),
            color=alt.Color(
                "segment:N",
                scale=alt.Scale(
                    domain=df["segment"].to_list(),
                    range=colors[: df.height],
                ),
                legend=alt.Legend(orient="bottom", title=None),
            ),
            tooltip=["segment", "count"],
        )
        .properties(height=300)
    )
    chart_card("Customer Segmentation", chart)


def _render_shipping_analysis(analytics: dict[str, Any]) -> None:
    providers = analytics.get("shipping", {}).get("providers", [])
    if not providers:
        return
    df = pl.DataFrame(providers)
    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar(color="#A29BFE")
        .encode(
            x=alt.X("shipping_provider:N", title=None, sort="-y"),
            y=alt.Y("order_count:Q", title="Orders"),
            tooltip=["shipping_provider", "order_count"],
        )
        .properties(height=250)
    )
    chart_card("Shipping Provider Share", chart)


def _render_payment_analysis(analytics: dict[str, Any]) -> None:
    methods = analytics.get("payment", {}).get("methods", [])
    if not methods:
        return
    df = pl.DataFrame(methods)
    chart = (
        alt.Chart(df.to_pandas())
        .mark_arc()
        .encode(
            theta=alt.Theta("revenue:Q"),
            color=alt.Color("payment_method:N", legend=alt.Legend(orient="bottom", title=None)),
            tooltip=["payment_method", alt.Tooltip("revenue", format=",.0f")],
        )
        .properties(height=300)
    )
    chart_card("Payment Method Distribution", chart)


def render() -> None:
    st.title("Dashboard")

    repo = _get_repo()
    if not repo.table_exists("orders"):
        st.info("No data yet. Go to **Upload** to add order data.", icon="📁")
        return

    with st.spinner("Computing analytics..."):
        analytics = _load_analytics()

    if not analytics:
        st.warning("No analytics data available. Upload a file first.")
        return

    # ── KPI Row ──
    _render_kpis(analytics)

    st.divider()

    # ── Charts Top Row ──
    col1, col2 = st.columns(2)
    with col1:
        _render_revenue_trend(analytics)
    with col2:
        _render_monthly_orders(analytics)

    # ── Charts Middle Row ──
    col1, col2 = st.columns(2)
    with col1:
        _render_top_products(analytics)
    with col2:
        _render_customer_segments(analytics)

    # ── Charts Bottom Row ──
    col1, col2 = st.columns(2)
    with col1:
        _render_province_performance(analytics)
    with col2:
        _render_city_performance(analytics)

    # ── Charts Bottom Row 2 ──
    col1, col2 = st.columns(2)
    with col1:
        _render_shipping_analysis(analytics)
    with col2:
        _render_payment_analysis(analytics)

    st.divider()

    # ── Insights ──
    _render_insights(analytics)

    # ── Raw data button ──
    with st.expander("View raw data"):
        raw = repo.query("SELECT * FROM orders ORDER BY order_date DESC LIMIT 100")
        data_table(raw, height=300)
