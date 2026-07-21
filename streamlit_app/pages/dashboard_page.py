"""
Dashboard page — KPI cards, charts, insights, and customer table.
Mobile-responsive with stacked layout on small screens.
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

# ── Responsive CSS ──────────────────────────────────────────────────────
_RESPONSIVE_CSS = """
<style>
    /* KPI grid: 3 cols desktop, 2 cols tablet, 1 col mobile */
    .kpi-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 0.75rem;
    }
    @media (max-width: 900px) {
        .kpi-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 500px) {
        .kpi-grid { grid-template-columns: 1fr; }
    }
    /* chart containers stack full-width on small screens */
    .chart-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 1rem;
    }
    @media (max-width: 768px) {
        .chart-grid { grid-template-columns: 1fr; }
    }
    /* responsive tables */
    .dataframe { font-size: 0.85rem; }
    @media (max-width: 600px) {
        .dataframe { font-size: 0.7rem; }
        .dataframe th, .dataframe td { padding: 4px 6px !important; }
        .stTabs [data-baseweb="tab-list"] { gap: 4px; }
        .stTabs [data-baseweb="tab"] { font-size: 0.75rem; padding: 4px 8px; }
    }
</style>
"""


def _get_repo() -> DuckDBRepository:
    return DuckDBRepository(get_connection())


@st.cache_data(ttl=300)
def _load_analytics() -> Optional[dict[str, Any]]:
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
    cancel = analytics.get("cancellation", {})

    kpi_data = [
        ("Total Revenue", _format_rp(cust.get("total_revenue", 0)), "Revenue from completed orders"),
        ("Total Orders", f"{cancel.get('total_orders', 0):,}", "All orders including cancelled"),
        ("Total Customers", f"{cust.get('total_customers', 0):,}", "Unique buyers"),
        ("Avg Order Value", _format_rp(cust.get("avg_basket", 0)), "Revenue / orders"),
        ("Repeat Rate", f"{cust.get('repeat_rate', 0):.1f}%", "Customers with 2+ orders"),
        ("Cancellation", f"{cancel.get('cancellation_rate', 0):.1f}%", "Orders cancelled"),
    ]

    st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
    for label, value, help_text in kpi_data:
        metric_card(label, value, help_text=help_text)
    st.markdown("</div>", unsafe_allow_html=True)


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


def _render_top_customers(repo: DuckDBRepository) -> None:
    """Table: customer name, revenue, total orders, reorder products."""
    if not repo.table_exists("orders"):
        return

    sql = """
        SELECT
            buyer_name,
            COUNT(DISTINCT order_id) AS total_orders,
            SUM(total_amount) AS total_revenue,
            (
                SELECT COUNT(*)
                FROM (
                    SELECT o2.product_name
                    FROM orders o2
                    WHERE o2.buyer_username = o.buyer_username
                      AND o2.order_status != 'cancelled'
                    GROUP BY o2.product_name
                    HAVING COUNT(DISTINCT o2.order_id) > 1
                )
            ) AS reorder_products
        FROM orders o
        WHERE order_status != 'cancelled'
        GROUP BY buyer_name, buyer_username
        ORDER BY total_revenue DESC
        LIMIT 20
    """
    raw = repo.query(sql)
    if not raw:
        return

    df = pl.DataFrame(raw).with_columns(
        pl.col("total_revenue").cast(pl.Float64).alias("revenue_f64"),
        pl.col("reorder_products").cast(pl.Int64).alias("reorder_f64"),
    )

    st.markdown("### 🏆 Top Customers")
    st.markdown(
        "<p style='color:#64748b; font-size:0.85rem;'>"
        "Highest revenue customers, with reorder count (products ordered more than once)."
        "</p>",
        unsafe_allow_html=True,
    )

    data_table(df, height=400)


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
        .properties(height=280)
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
        .properties(height=280)
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
        .properties(height=280)
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
        .properties(height=280)
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
        .properties(height=280)
    )
    chart_card("Payment Method Distribution", chart)


def render() -> None:
    st.markdown(_RESPONSIVE_CSS, unsafe_allow_html=True)
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

    # ── Top Customers Table ──
    _render_top_customers(repo)

    st.divider()

    # ── Charts (stacked full-width on mobile) ──
    col1, col2 = st.columns(2)
    with col1:
        _render_revenue_trend(analytics)
    with col2:
        _render_monthly_orders(analytics)

    col1, col2 = st.columns(2)
    with col1:
        _render_top_products(analytics)
    with col2:
        _render_customer_segments(analytics)

    col1, col2 = st.columns(2)
    with col1:
        _render_province_performance(analytics)
    with col2:
        _render_city_performance(analytics)

    col1, col2 = st.columns(2)
    with col1:
        _render_shipping_analysis(analytics)
    with col2:
        _render_payment_analysis(analytics)

    st.divider()

    # ── Insights ──
    _render_insights(analytics)

    # ── Raw data ──
    with st.expander("View raw data"):
        raw = repo.query("SELECT * FROM orders ORDER BY order_date DESC LIMIT 100")
        data_table(raw, height=300)
