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

_CHART_COLORS = THEME["chart_colors"]

_CSS = """
<style>
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
    .section-header {
        display: flex; align-items: center; gap: 0.5rem;
        margin: 1.5rem 0 0.25rem 0;
    }
    .section-header h3 { margin: 0; }
    .section-sub {
        color: #64748b; font-size: 0.85rem; margin: 0 0 1rem 0;
    }
    .loading-card {
        border: 1px solid #e2e8f0;
        border-radius: 0.5rem;
        padding: 2rem;
        text-align: center;
        background: #f8fafc;
    }
    .dataframe { font-size: 0.85rem; }
    @media (max-width: 600px) {
        .dataframe { font-size: 0.7rem; }
        .dataframe th, .dataframe td { padding: 4px 6px !important; }
    }
</style>
"""


def _get_repo() -> DuckDBRepository:
    return DuckDBRepository(get_connection())


@st.cache_data(ttl=300, show_spinner=False)
def _load_analytics() -> Optional[dict[str, Any]]:
    repo = _get_repo()
    if not repo.table_exists("fact_sales"):
        return None
    from streamlit_app.services.analytics_service import AnalyticsService
    service = AnalyticsService(repo)
    return service.compute_all()


def _format_rp(value: float) -> str:
    if value >= 1_000_000_000:
        return f"Rp {value/1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"Rp {value/1_000_000:.2f}M"
    return f"Rp {value:,.0f}"


def _section(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"<div class='section-header'><h3>{title}</h3></div>",
        unsafe_allow_html=True,
    )
    if subtitle:
        st.markdown(f"<p class='section-sub'>{subtitle}</p>", unsafe_allow_html=True)


def _render_kpis(analytics: dict[str, Any]) -> None:
    cust = analytics.get("customer", {})
    cancel = analytics.get("cancellation", {})

    kpi_data = [
        ("Total Revenue", _format_rp(cust.get("total_revenue", 0)), "Revenue from completed orders", "💰"),
        ("Total Orders", f"{cancel.get('total_orders', 0):,}", "All orders including cancelled", "📦"),
        ("Total Customers", f"{cust.get('total_customers', 0):,}", "Unique buyers", "👥"),
        ("Avg Order Value", _format_rp(cust.get("avg_basket", 0)), "Revenue / orders", "🛒"),
        ("Repeat Rate", f"{cust.get('repeat_rate', 0):.1f}%", "Customers with 2+ orders", "🔄"),
        ("Cancellation", f"{cancel.get('cancellation_rate', 0):.1f}%", "Orders cancelled", "❌"),
    ]

    cols = st.columns(6)
    for col, (label, value, help_text, icon) in zip(cols, kpi_data):
        with col:
            with st.container(border=True):
                st.markdown(
                    f"<p style='color:#64748b; font-size:0.75rem; margin-bottom:2px;'>{icon} {label}</p>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<p style='font-size:1.3rem; font-weight:700; margin:0;'>{value}</p>",
                    unsafe_allow_html=True,
                )
                st.caption(help_text)


def _render_insights(analytics: dict[str, Any]) -> None:
    insights = analytics.get("insights", [])
    if not insights:
        return
    _section("Business Insights", "AI-generated recommendations based on your data")
    high = [i for i in insights if i.get("priority") == "high"]
    medium = [i for i in insights if i.get("priority") == "medium"]
    for ins in high[:3]:
        with st.container(border=True):
            cols = st.columns([6, 1])
            with cols[0]:
                st.markdown(
                    f"<span style='background:#fee2e2; color:#dc2626; padding:2px 8px; "
                    f"border-radius:4px; font-size:0.7rem; font-weight:600;'>{ins.get('type', '').upper()}</span> "
                    f"<strong>{ins.get('title', '')}</strong>",
                    unsafe_allow_html=True,
                )
                st.markdown(ins.get("description", ""))
                if ins.get("recommendation"):
                    st.markdown(f"💡 *{ins['recommendation']}*")
            with cols[1]:
                st.markdown(
                    f"<p style='color:#dc2626; font-weight:600; font-size:0.8rem; text-align:right;'>HIGH</p>",
                    unsafe_allow_html=True,
                )
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
    if not repo.table_exists("orders"):
        return
    sql = """
        SELECT
            COALESCE(NULLIF(buyer_name, ''), buyer_username) AS buyer_name,
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
    if raw.is_empty():
        return

    df = pl.DataFrame(raw).with_columns(
        pl.col("total_revenue").cast(pl.Float64),
        pl.col("reorder_products").cast(pl.Int64),
    )
    _section("Top Customers", "Highest revenue customers with reorder activity")

    pdf = df.to_pandas()
    pdf["total_revenue_fmt"] = pdf["total_revenue"].apply(_format_rp)

    st.dataframe(
        pdf[["buyer_name", "total_revenue_fmt", "total_orders", "reorder_products"]],
        column_config={
            "buyer_name": "Customer Name",
            "total_revenue_fmt": "Total Revenue",
            "total_orders": "Orders",
            "reorder_products": "Reorder Products",
        },
        use_container_width=True,
        hide_index=True,
        height=400,
    )


def _render_revenue_trend(analytics: dict[str, Any]) -> None:
    months = analytics.get("trend", {}).get("months", [])
    if not months:
        return
    df = pl.DataFrame(months).with_columns(pl.col("revenue").cast(pl.Float64))

    base = alt.Chart(df.to_pandas()).encode(
        x=alt.X("month:N", title=None, sort=None, axis=alt.Axis(labelAngle=-25, labelOverlap=True)),
    )
    line = base.mark_line(point=True, strokeWidth=2.5, color="#1B98F5").encode(
        y=alt.Y("revenue:Q", title="Revenue", axis=alt.Axis(format="~s")),
        tooltip=["month", alt.Tooltip("revenue", format=",.0f")],
    )
    area = base.mark_area(opacity=0.15, color="#1B98F5").encode(
        y=alt.Y("revenue:Q"),
    )
    chart_card("Revenue Trend", area + line, height=300)


def _render_monthly_orders(analytics: dict[str, Any]) -> None:
    months = analytics.get("trend", {}).get("months", [])
    if not months:
        return
    df = pl.DataFrame(months)

    bars = (
        alt.Chart(df.to_pandas())
        .mark_bar(color="#00C9A7", cornerRadiusTopLeft=4, cornerRadiusTopRight=4)
        .encode(
            x=alt.X("month:N", title=None, sort=None, axis=alt.Axis(labelAngle=-25, labelOverlap=True)),
            y=alt.Y("order_count:Q", title="Orders"),
            tooltip=["month", "order_count"],
        )
    )
    trend = (
        alt.Chart(df.to_pandas())
        .mark_line(color="#0B6FA6", strokeWidth=2, strokeDash=[4, 4])
        .encode(
            x="month:N",
            y=alt.Y("order_count:Q"),
        )
    )
    chart_card("Monthly Orders", bars + trend, height=280)


def _render_top_products(analytics: dict[str, Any]) -> None:
    products = analytics.get("product", {}).get("products", [])
    if not products:
        return
    df = pl.DataFrame(products[:10]).with_columns(pl.col("total_revenue").cast(pl.Float64))

    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar(color=_CHART_COLORS[0], cornerRadiusTopRight=4)
        .encode(
            y=alt.Y("product_name:N", title=None, sort="-x", axis=alt.Axis(labelLimit=200)),
            x=alt.X("total_revenue:Q", title="Revenue", axis=alt.Axis(format="~s")),
            tooltip=[
                "product_name",
                "total_quantity",
                alt.Tooltip("total_revenue", format=",.0f"),
            ],
        )
        .properties(height=280)
    )
    text = chart.mark_text(align="left", dx=4, fontSize=10, color="#64748b").encode(
        text=alt.Text("total_revenue:Q", format="~s"),
    )
    chart_card("Top Products by Revenue", chart + text, height=300)


def _render_province_performance(analytics: dict[str, Any]) -> None:
    provinces = analytics.get("province", {}).get("provinces", [])
    if not provinces:
        return
    df = pl.DataFrame(provinces).with_columns(pl.col("revenue").cast(pl.Float64))

    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar(cornerRadiusTopRight=4)
        .encode(
            y=alt.Y("province:N", title=None, sort="-x", axis=alt.Axis(labelLimit=150)),
            x=alt.X("revenue:Q", title="Revenue", axis=alt.Axis(format="~s")),
            color=alt.Color("revenue:Q", scale=alt.Scale(
                scheme="blues", domain=[df["revenue"].min(), df["revenue"].max()],
            ), legend=None),
            tooltip=["province", alt.Tooltip("revenue", format=",.0f"), "order_count"],
        )
        .properties(height=250)
    )
    chart_card("Province Performance", chart, height=270)


def _render_city_performance(analytics: dict[str, Any]) -> None:
    cities = analytics.get("city", {}).get("cities", [])
    if not cities:
        return
    df = pl.DataFrame(cities).with_columns(pl.col("revenue").cast(pl.Float64))

    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar(cornerRadiusTopRight=4)
        .encode(
            y=alt.Y("city_name:N", title=None, sort="-x", axis=alt.Axis(labelLimit=150)),
            x=alt.X("revenue:Q", title="Revenue", axis=alt.Axis(format="~s")),
            color=alt.Color("revenue:Q", scale=alt.Scale(
                scheme="teals", domain=[df["revenue"].min(), df["revenue"].max()],
            ), legend=None),
            tooltip=["city_name", "province", alt.Tooltip("revenue", format=",.0f"), "order_count"],
        )
        .properties(height=280)
    )
    chart_card("City Performance", chart, height=300)


def _render_customer_segments(analytics: dict[str, Any]) -> None:
    segments = analytics.get("customer", {}).get("segments", [])
    if not segments:
        return
    df = pl.DataFrame(segments)
    total = df["count"].sum()
    df = df.with_columns(
        (pl.col("count") / total * 100).round(1).alias("pct"),
    )

    colors = _CHART_COLORS[: df.height]
    chart = (
        alt.Chart(df.to_pandas())
        .mark_arc(innerRadius=55, stroke="#fff", strokeWidth=2)
        .encode(
            theta=alt.Theta("count:Q"),
            color=alt.Color(
                "segment:N",
                scale=alt.Scale(domain=df["segment"].to_list(), range=colors),
                legend=alt.Legend(orient="bottom", title=None, columns=3, labelFontSize=11),
            ),
            tooltip=["segment", "count", alt.Tooltip("pct", format=".1f")],
        )
        .properties(height=300)
    )
    text = chart.mark_text(radius=95, fontSize=10, fontWeight=600, color="#64748b").encode(
        text=alt.Text("pct:Q", format=".1f"),
    )
    chart_card("Customer Segmentation", chart, height=310)


def _render_shipping_analysis(analytics: dict[str, Any]) -> None:
    providers = analytics.get("shipping", {}).get("providers", [])
    if not providers:
        return
    df = pl.DataFrame(providers)
    total_orders = df["order_count"].sum()
    df = df.with_columns(
        (pl.col("order_count") / total_orders * 100).round(1).alias("pct"),
    )

    chart = (
        alt.Chart(df.to_pandas())
        .mark_bar(cornerRadiusTopRight=4)
        .encode(
            x=alt.X("shipping_provider:N", title=None, sort="-y", axis=alt.Axis(labelAngle=0)),
            y=alt.Y("order_count:Q", title="Orders"),
            color=alt.Color("shipping_provider:N", scale=alt.Scale(
                scheme="category10",
            ), legend=None),
            tooltip=["shipping_provider", "order_count", alt.Tooltip("pct", format=".1f")],
        )
        .properties(height=250)
    )
    text = chart.mark_text(dy=-6, fontSize=10, color="#64748b").encode(
        text=alt.Text("pct:Q", format=".1f"),
    )
    chart_card("Shipping Provider Share", chart + text, height=280)


def _render_payment_analysis(analytics: dict[str, Any]) -> None:
    methods = analytics.get("payment", {}).get("methods", [])
    if not methods:
        return
    df = pl.DataFrame(methods).with_columns(pl.col("revenue").cast(pl.Float64))

    colors = _CHART_COLORS[: df.height]
    chart = (
        alt.Chart(df.to_pandas())
        .mark_arc(stroke="#fff", strokeWidth=2)
        .encode(
            theta=alt.Theta("revenue:Q"),
            color=alt.Color(
                "payment_method:N",
                scale=alt.Scale(domain=df["payment_method"].to_list(), range=colors),
                legend=alt.Legend(orient="bottom", title=None, columns=2, labelFontSize=11),
            ),
            tooltip=["payment_method", alt.Tooltip("revenue", format=",.0f")],
        )
        .properties(height=300)
    )
    chart_card("Payment Method Distribution", chart, height=310)


def render() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
    st.title("Dashboard")

    repo = _get_repo()
    if not repo.table_exists("orders"):
        st.info("No data yet. Go to **Upload** to add order data.", icon="📁")
        return

    # ── Loading with progress ──────────────────────────────────────────
    load_placeholder = st.empty()
    progress_bar = load_placeholder.progress(0, text="Preparing...")

    progress_bar.progress(10, text="Connecting to database...")
    progress_bar.progress(20, text="Checking data availability...")

    progress_bar.progress(30, text="Computing customer analytics...")
    progress_bar.progress(45, text="Computing product analytics...")
    progress_bar.progress(55, text="Computing geographic analytics...")
    progress_bar.progress(70, text="Computing trend & shipping analytics...")
    progress_bar.progress(85, text="Generating business insights...")

    analytics = _load_analytics()

    progress_bar.progress(100, text="Done!")
    load_placeholder.empty()

    if not analytics:
        st.warning("No analytics data available. Upload a file first.")
        return

    # ── KPI Row ──
    _render_kpis(analytics)

    st.divider()

    # ── Top Customers ──
    _render_top_customers(repo)

    st.divider()

    # ── Charts ──
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
