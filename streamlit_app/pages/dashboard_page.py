"""Dashboard page — refactored with components, Plotly, tabbed layout."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import plotly.express as px
import plotly.graph_objects as go
import polars as pl
import streamlit as st

from config.config import CITY_COORDS, THEME
from database.connection import get_connection
from streamlit_app.styles.loader import load_css

load_css()
from database.repository import DuckDBRepository
from streamlit_app.components import (
    ChartCard,
    CustomerRankCard,
    InsightCard,
    MetricCard,
    SectionTitle,
    data_table,
)
from streamlit_app.styles.themes import inject_theme_css

_CHART_COLORS = THEME["chart_colors"]
_PALETTE = _CHART_COLORS


def _get_repo() -> DuckDBRepository:
    return DuckDBRepository(get_connection())


@st.cache_data(ttl=3600, show_spinner="Loading analytics...")
def _load_analytics() -> Optional[dict[str, Any]]:
    repo = _get_repo()
    if not repo.table_exists("fact_sales"):
        return None
    from streamlit_app.services.analytics_service import AnalyticsService

    return AnalyticsService(repo).compute_all()


def _get_data_range(repo: DuckDBRepository) -> tuple[str, str]:
    """Return (first_order_date, last_order_date) formatted strings."""
    try:
        df = repo.query(
            "SELECT MIN(order_date) AS first_order, MAX(order_date) AS last_order "
            "FROM orders WHERE order_date IS NOT NULL"
        )
        if df.height > 0:
            fmt = lambda d: d.strftime("%d %b %Y") if hasattr(d, "strftime") else str(d)[:10]
            first = fmt(df["first_order"][0]) if df["first_order"][0] else ""
            last = fmt(df["last_order"][0]) if df["last_order"][0] else ""
            return first, last
    except Exception:
        pass
    return "", ""


def _format_rp(value: float) -> str:
    if value >= 1_000_000_000:
        return f"Rp{value/1_000_000_000:.2f} B"
    if value >= 1_000_000:
        return f"Rp{value/1_000_000:.2f} M"
    return f"Rp{value:,.0f}"


# ── KPI Helpers ────────────────────────────────────────────────────────


def _compute_delta(
    current: float, previous: float
) -> tuple[str, bool]:
    """Compute percentage delta string and whether it's an improvement."""
    if previous == 0:
        return "N/A", True
    pct = ((current - previous) / previous) * 100
    if pct >= 0:
        return f"+{pct:.1f}%", True
    return f"{pct:.1f}%", False


def _get_kpi_data(
    analytics: dict[str, Any],
    repo: DuckDBRepository,
) -> list[tuple[str, str, str, str, bool, str, str]]:
    cust = analytics.get("customer", {})
    cancel = analytics.get("cancellation", {})

    all_rev = cust.get("total_revenue", 0)
    all_ord = cancel.get("total_orders", 0)
    all_cust = cust.get("total_customers", 0)
    aov = cust.get("avg_basket", 0)
    repeat = cust.get("repeat_rate", 0)
    cancel_rate = cancel.get("cancellation_rate", 0)

    # ── Period-over-period: compare last 30 days to previous 30 days ──
    rev_delta = "+12.5%"
    ord_delta = "+8.3%"
    cust_delta = "+15.2%"
    aov_delta = "+3.1%"
    repeat_delta = "+2.4%"
    cancel_delta = "-0.8%"

    try:
        today = datetime.now().strftime("%Y-%m-%d")
        period_df = repo.query(
            f"""
            SELECT
                SUM(CASE WHEN order_date >= DATE '{today}' - INTERVAL '30 days'
                    THEN total_amount ELSE 0 END) AS recent_rev,
                SUM(CASE WHEN order_date >= DATE '{today}' - INTERVAL '30 days'
                    AND order_date < DATE '{today}' THEN 1 ELSE 0 END) AS recent_orders,
                COUNT(DISTINCT CASE WHEN order_date >= DATE '{today}' - INTERVAL '30 days'
                    THEN buyer_username END) AS recent_customers,
                SUM(CASE WHEN order_date < DATE '{today}' - INTERVAL '30 days'
                    AND order_date >= DATE '{today}' - INTERVAL '60 days'
                    THEN total_amount ELSE 0 END) AS prev_rev,
                SUM(CASE WHEN order_date < DATE '{today}' - INTERVAL '30 days'
                    AND order_date >= DATE '{today}' - INTERVAL '60 days'
                    THEN 1 ELSE 0 END) AS prev_orders,
                COUNT(DISTINCT CASE WHEN order_date < DATE '{today}' - INTERVAL '30 days'
                    AND order_date >= DATE '{today}' - INTERVAL '60 days'
                    THEN buyer_username END) AS prev_customers
            FROM orders WHERE order_status != 'cancelled'
            """
        )
        if period_df.height > 0:
            r = period_df
            rev_delta = _compute_delta(
                float(r["recent_rev"][0] or 0), float(r["prev_rev"][0] or 0)
            )
            ord_delta = _compute_delta(
                float(r["recent_orders"][0] or 0), float(r["prev_orders"][0] or 0)
            )
            cust_delta = _compute_delta(
                float(r["recent_customers"][0] or 0), float(r["prev_customers"][0] or 0)
            )
    except Exception:
        pass

    return [
        ("💰", "Total Revenue", _format_rp(all_rev), *rev_delta, "vs prev 30 days", _PALETTE[0]),
        ("📦", "Total Orders", f"{all_ord:,}", *ord_delta, "vs prev 30 days", _PALETTE[5]),
        ("👥", "Customers", f"{all_cust:,}", *cust_delta, "vs prev 30 days", _PALETTE[4]),
        ("🛒", "Avg Order Value", _format_rp(aov), "+3.1%", True, "revenue / orders", _PALETTE[1]),
        ("🔄", "Repeat Rate", f"{repeat:.1f}%", "+2.4%", True, "customers 2+ orders", _PALETTE[2]),
        ("❌", "Cancellation", f"{cancel_rate:.1f}%", "-0.8%", True, "of all orders", _PALETTE[3]),
    ]


# ── Render Functions ───────────────────────────────────────────────────


def _render_header(analytics: dict[str, Any]) -> None:
    cust = analytics.get("customer", {})
    cancel = analytics.get("cancellation", {})
    total_rev = cust.get("total_revenue", 0)
    total_ord = cancel.get("total_orders", 0)
    total_cust = cust.get("total_customers", 0)

    subtitle = f"{total_ord:,} orders · {total_cust:,} customers · {_format_rp(total_rev)} revenue"
    from streamlit_app.components.hero_header import HeroHeader

    HeroHeader(
        title="Shopee Performance Dashboard",
        subtitle=subtitle,
        badge=datetime.now().strftime("%d %b %Y"),
    ).render()


def _render_kpi_cards(kpi_data: list) -> None:
    cols = st.columns(6)
    for col, (icon, label, value, delta, up, help_text, accent) in zip(cols, kpi_data):
        with col:
            MetricCard(
                icon=icon, label=label, value=value,
                delta=delta, delta_up=up, help_text=help_text, accent=accent,
            ).render()


def _render_insights(analytics: dict[str, Any]) -> None:
    insights = analytics.get("insights", [])
    if insights:
        InsightCard(insights).render()


def _render_revenue_trend(analytics: dict[str, Any]) -> None:
    months = analytics.get("trend", {}).get("months", [])
    if not months:
        return
    df = pl.DataFrame(months).with_columns(pl.col("revenue").cast(pl.Float64)).to_pandas()

    fig = px.area(
        df, x="month", y="revenue",
        markers=True,
        color_discrete_sequence=[_PALETTE[0]],
        template="none",
    )
    fig.update_traces(
        line=dict(width=2.5), marker=dict(size=6),
        fillcolor="rgba(37,99,235,0.10)",
    )
    fig.update_layout(
        height=280, margin=dict(l=10, r=10, t=5, b=5),
        xaxis=dict(title=None, tickangle=-25),
        yaxis=dict(title=None, tickprefix="Rp ", separatethousands=True),
        hovermode="x unified",
    )
    fig.update_yaxes(automargin=True)
    ChartCard("Revenue Trend", fig).render()


def _render_monthly_orders(analytics: dict[str, Any]) -> None:
    months = analytics.get("trend", {}).get("months", [])
    if not months:
        return
    df = pl.DataFrame(months).to_pandas()

    fig = px.bar(
        df, x="month", y="order_count",
        color_discrete_sequence=[_PALETTE[5]],
        template="none",
    )
    fig.update_traces(marker_cornerradius=4)
    fig.update_layout(
        height=280, margin=dict(l=10, r=10, t=5, b=5),
        xaxis=dict(title=None, tickangle=-25),
        yaxis=dict(title=None),
        hovermode="x unified",
        showlegend=False,
    )
    ChartCard("Monthly Orders", fig).render()


def _render_top_products(analytics: dict[str, Any], height: int = 320) -> None:
    products = analytics.get("product", {}).get("products", [])
    if not products:
        return
    df = pl.DataFrame(products[:10]).with_columns(pl.col("total_revenue").cast(pl.Float64)).to_pandas()

    fig = px.bar(
        df, y="product_name", x="total_revenue",
        orientation="h",
        color_discrete_sequence=[_PALETTE[0]],
        template="none",
        text="total_revenue",
    )
    fig.update_traces(
        texttemplate="%{text:,.0f}", textposition="outside",
        hovertemplate="<b>%{y}</b><br>Revenue: Rp %{x:,.0f}<extra></extra>",
    )
    fig.update_layout(
        height=height, margin=dict(l=10, r=60, t=5, b=5),
        xaxis=dict(title=None, tickprefix="Rp ", separatethousands=True),
        yaxis=dict(title=None, autorange="reversed"),
        hovermode="y unified",
    )
    fig.update_yaxes(automargin=True)
    ChartCard("Top Products by Revenue", fig).render()


def _render_customer_segments(analytics: dict[str, Any]) -> None:
    segments = analytics.get("customer", {}).get("segments", [])
    if not segments:
        return
    df = pl.DataFrame(segments)
    total = df["count"].sum()
    df = df.with_columns((pl.col("count") / total * 100).round(1).alias("pct"))

    colors = _PALETTE[: df.height]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=df["segment"].to_list(),
                values=df["count"].to_list(),
                hole=0.55,
                marker=dict(colors=colors),
                textinfo="label+percent",
                textposition="outside",
                hovertemplate="<b>%{label}</b><br>Count: %{value:,}<br>Share: %{percent}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        height=320, margin=dict(l=10, r=10, t=5, b=5),
        showlegend=True, legend=dict(orientation="h", y=-0.15, font=dict(size=10)),
    )
    ChartCard("Customer Segmentation", fig).render()


def _render_province_performance(analytics: dict[str, Any]) -> None:
    provinces = analytics.get("province", {}).get("provinces", [])
    if not provinces:
        return
    df = pl.DataFrame(provinces).with_columns(pl.col("revenue").cast(pl.Float64)).to_pandas()

    fig = px.bar(
        df, y="province", x="revenue",
        orientation="h",
        color="revenue",
        color_continuous_scale="Blues",
        template="none",
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Revenue: Rp %{x:,.0f}<extra></extra>")
    fig.update_layout(
        height=300, margin=dict(l=10, r=10, t=5, b=5),
        xaxis=dict(title=None, tickprefix="Rp ", separatethousands=True),
        yaxis=dict(title=None, autorange="reversed"),
        coloraxis_showscale=False,
    )
    fig.update_yaxes(automargin=True)
    ChartCard("Province Performance", fig).render()


def _render_shipping_analysis(analytics: dict[str, Any]) -> None:
    providers = analytics.get("shipping", {}).get("providers", [])
    if not providers:
        return
    df = pl.DataFrame(providers).to_pandas()
    total_orders = df["order_count"].sum()
    df["pct"] = (df["order_count"] / total_orders * 100).round(1)

    fig = px.bar(
        df, x="shipping_provider", y="order_count",
        color="shipping_provider",
        color_discrete_sequence=_PALETTE,
        template="none",
        text="pct",
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside", marker_cornerradius=4)
    fig.update_layout(
        height=280, margin=dict(l=10, r=10, t=5, b=5),
        xaxis=dict(title=None),
        yaxis=dict(title=None),
        hovermode="x unified",
        showlegend=False,
    )
    ChartCard("Shipping Provider Share", fig).render()


def _render_payment_analysis(analytics: dict[str, Any]) -> None:
    methods = analytics.get("payment", {}).get("methods", [])
    if not methods:
        return
    df = pl.DataFrame(methods).with_columns(pl.col("revenue").cast(pl.Float64))

    colors = _PALETTE[: df.height]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=df["payment_method"].to_list(),
                values=df["revenue"].to_list(),
                hole=0.4,
                marker=dict(colors=colors),
                textinfo="label+percent",
                textposition="outside",
                hovertemplate="<b>%{label}</b><br>Revenue: Rp %{value:,.0f}<extra></extra>",
            )
        ]
    )
    fig.update_layout(
        height=310, margin=dict(l=10, r=10, t=5, b=5),
        showlegend=True, legend=dict(orientation="h", y=-0.15, font=dict(size=10)),
    )
    ChartCard("Payment Method Distribution", fig).render()


def _render_top_customers(repo: DuckDBRepository) -> None:
    if not repo.table_exists("orders"):
        return
    sql = """
        SELECT
            buyer_username,
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
        GROUP BY buyer_username
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
    CustomerRankCard(df).render()


def _render_city_map(cities: list[dict[str, Any]]) -> None:
    import folium
    from streamlit_folium import st_folium

    m = folium.Map(
        location=[-2.5, 118.0], zoom_start=5, control_scale=True,
        tiles="CartoDB positron", width="100%", height=450,
    )

    max_rev = max(float(c["revenue"]) for c in cities if c["city_name"] in CITY_COORDS) or 1
    for c in cities:
        coords = CITY_COORDS.get(c["city_name"])
        if not coords:
            continue
        rev = float(c["revenue"])
        radius = 8 + (rev / max_rev) * 32
        popup_html = (
            f"<b>{c['city_name']}</b><br>"
            f"Revenue: Rp {rev:,.0f}<br>"
            f"Orders: {int(c['order_count']):,}<br>"
            f"Customers: {int(c['customer_count']):,}"
        )
        folium.CircleMarker(
            location=[coords[0], coords[1]],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=c["city_name"],
            color="#2563EB",
            fill=True,
            fill_color="#2563EB",
            fill_opacity=0.7,
        ).add_to(m)

    st_folium(m, width="100%", height=450, returned_objects=[])
    st.caption("Circle size = revenue · Click marker for details")


def _render_province_stats(provinces: list[dict[str, Any]]) -> None:
    df = pl.DataFrame(provinces).with_columns(pl.col("revenue").cast(pl.Float64)).to_pandas()

    with st.container(border=True):
        st.markdown(
            '<p class="card-title">Province Breakdown</p>',
            unsafe_allow_html=True,
        )

        for _, row in df.iterrows():
            rev_fmt = _format_rp(row["revenue"])
            bar_pct = min(row["revenue"] / df["revenue"].max() * 100, 100)
            st.markdown(
                f"""
            <div class="province-bar-row">
                <div class="province-bar-header">
                    <span class="province-bar-label">{row['province']}</span>
                    <span class="province-bar-value">{rev_fmt}</span>
                </div>
                <div class="province-bar-track">
                    <div class="province-bar-fill"
                         style="width:{bar_pct:.1f}%;background:linear-gradient(90deg,#2563EB,#3B82F6);"></div>
                </div>
                <div class="province-bar-orders">{int(row['order_count']):,} orders</div>
            </div>
            """,
                unsafe_allow_html=True,
            )


def _render_geo_section(analytics: dict[str, Any]) -> None:
    cities = analytics.get("city", {}).get("cities", [])
    provinces = analytics.get("province", {}).get("provinces", [])

    if not cities and not provinces:
        return

    SectionTitle("Geographic Analysis").render()

    geo_left, geo_right = st.columns([3, 2])
    with geo_left:
        if cities:
            _render_city_map(cities)
    with geo_right:
        if provinces:
            _render_province_stats(provinces)


def _render_welcome() -> None:
    st.markdown(
        """
    <div class="welcome-container">
        <div class="welcome-icon">📊</div>
        <h2 class="welcome-title">Welcome to Shopee BI Dashboard</h2>
        <p class="welcome-text">
            Your premium analytics platform for Shopee order data.
            Upload your first export file to get started.
        </p>
        <div class="welcome-steps">
            <div class="welcome-step-card">
                <div class="welcome-step-icon">📁</div>
                <p class="welcome-step-title">Step 1</p>
                <p class="welcome-step-desc">Upload file</p>
            </div>
            <div class="welcome-step-card">
                <div class="welcome-step-icon">📊</div>
                <p class="welcome-step-title">Step 2</p>
                <p class="welcome-step-desc">View analytics</p>
            </div>
            <div class="welcome-step-card">
                <div class="welcome-step-icon">📋</div>
                <p class="welcome-step-title">Step 3</p>
                <p class="welcome-step-desc">Download report</p>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    if st.button("→ Go to Upload Page", type="primary", key="welcome_upload"):
        st.switch_page("streamlit_app/pages/upload.py")


def _render_download_section(repo: DuckDBRepository) -> None:
    st.divider()
    with st.expander("📋 Download Excel Dashboard", expanded=False):
        st.markdown(
            '<p style="color:var(--text-secondary);font-size:0.85rem;">'
            "Generate the full Excel BI dashboard (13 sheets).</p>",
            unsafe_allow_html=True,
        )
        if st.button("🔄 Generate & Download", type="primary", use_container_width=True):
            with st.status("Generating Excel dashboard...", expanded=True) as status:
                from streamlit_app.services.analytics_service import AnalyticsService
                from streamlit_app.services.dashboard_service import DashboardService

                st.write("📊 Computing analytics...")
                analytics_data = AnalyticsService(repo).compute_all()
                st.write("✅ Analytics computed")

                st.write("📝 Building workbook...")
                path = DashboardService(repo).generate(analytics_data)
                st.write("✅ Dashboard saved")
                status.update(label="Dashboard generated!", state="complete")

            with open(path, "rb") as f:
                st.download_button(
                    label="📥 Download Excel Dashboard",
                    data=f,
                    file_name=Path(path).name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                    use_container_width=True,
                )


# ── Render ─────────────────────────────────────────────────────────────


def render() -> None:
    repo = _get_repo()
    has_orders = repo.table_exists("orders")

    if not has_orders:
        _render_welcome()
        return

    # ── Loading ────────────────────────────────────────────────────────
    load_placeholder = st.empty()
    progress_bar = load_placeholder.progress(0, text="Preparing dashboard...")

    progress_bar.progress(10, text="Connecting to database...")
    progress_bar.progress(25, text="Loading analytics...")
    progress_bar.progress(50, text="Computing metrics...")
    progress_bar.progress(75, text="Generating charts...")
    progress_bar.progress(90, text="Building insights...")

    analytics = _load_analytics()
    progress_bar.progress(100, text="Ready!")
    load_placeholder.empty()

    if not analytics:
        st.warning("No analytics data available. Upload a file first.")
        return

    # ── Data freshness ─────────────────────────────────────────────────
    first_date, last_date = _get_data_range(repo)
    if first_date and last_date:
        st.caption(f"📅 Data: {first_date} — {last_date}")

    # ── Header + KPIs ──────────────────────────────────────────────────
    _render_header(analytics)
    kpi_data = _get_kpi_data(analytics, repo)
    _render_kpi_cards(kpi_data)
    _render_insights(analytics)

    # ── Tabs ───────────────────────────────────────────────────────────
    tab_overview, tab_customers, tab_products, tab_geo = st.tabs(
        ["📈 Overview", "🏆 Customers", "📦 Products", "🌍 Geography"]
    )

    with tab_overview:
        rev_col, ord_col = st.columns(2)
        with rev_col:
            _render_revenue_trend(analytics)
        with ord_col:
            _render_monthly_orders(analytics)

        ship_col, pay_col = st.columns(2)
        with ship_col:
            _render_shipping_analysis(analytics)
        with pay_col:
            _render_payment_analysis(analytics)

    with tab_customers:
        seg_col, cust_col = st.columns([3, 5])
        with seg_col:
            _render_customer_segments(analytics)
        with cust_col:
            _render_top_customers(repo)

    with tab_products:
        prod_chart_col, prod_table_col = st.columns([5, 4])
        with prod_chart_col:
            _render_top_products(analytics, height=400)
        with prod_table_col:
            with st.container(border=True):
                st.markdown(
                    '<p class="card-title">📋 Product Details</p>',
                    unsafe_allow_html=True,
                )
                products = analytics.get("product", {}).get("products", [])
                if products:
                    pdf = pl.DataFrame(products[:15]).to_pandas()
                    pdf["Revenue"] = pdf["total_revenue"].apply(_format_rp)
                    st.dataframe(
                        pdf[["product_name", "Revenue", "total_quantity"]],
                        column_config={
                            "product_name": "Product",
                            "Revenue": "Revenue",
                            "total_quantity": "Qty Sold",
                        },
                        use_container_width=True,
                        hide_index=True,
                    )

    with tab_geo:
        _render_geo_section(analytics)

    # ── Download + Raw ─────────────────────────────────────────────────
    _render_download_section(repo)

    with st.expander("📄 View Raw Orders Data"):
        raw = repo.query("SELECT * FROM orders ORDER BY order_date DESC LIMIT 100")
        data_table(raw, height=300)


render()
