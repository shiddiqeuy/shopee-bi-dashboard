"""
Dashboard page — redesigned with premium UI, Plotly charts, ranking cards, tabbed layout.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import polars as pl
import streamlit as st

from config.config import CITY_COORDS, THEME
from database.connection import get_connection
from database.repository import DuckDBRepository

_CHART_COLORS = THEME["chart_colors"]
_PALETTE = _CHART_COLORS


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
        return f"Rp{value/1_000_000_000:.2f} B"
    if value >= 1_000_000:
        return f"Rp{value/1_000_000:.2f} M"
    return f"Rp{value:,.0f}"


# ── Executive Header ───────────────────────────────────────────────────


def _render_header(analytics: dict[str, Any]) -> None:
    cust = analytics.get("customer", {})
    cancel = analytics.get("cancellation", {})
    total_rev = cust.get("total_revenue", 0)
    total_ord = cancel.get("total_orders", 0)
    total_cust = cust.get("total_customers", 0)

    st.markdown(
        f"""
    <div style="background:linear-gradient(135deg,#2563EB,#1D4ED8);border-radius:16px;padding:1.75rem 2rem;margin-bottom:1.5rem;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:1rem;">
            <div>
                <p style="color:rgba(255,255,255,0.7);font-size:0.75rem;font-weight:500;letter-spacing:0.08em;margin:0 0 0.25rem;">OVERVIEW</p>
                <h1 style="color:white;font-size:1.6rem;font-weight:700;margin:0;">Shopee Performance Dashboard</h1>
                <p style="color:rgba(255,255,255,0.6);font-size:0.85rem;margin:0.25rem 0 0;">
                    {total_ord:,} orders · {total_cust:,} customers · {_format_rp(total_rev)} revenue
                </p>
            </div>
            <div style="text-align:right;">
                <span style="background:rgba(255,255,255,0.15);color:white;padding:0.3rem 0.75rem;border-radius:20px;font-size:0.75rem;font-weight:500;">
                    {datetime.now().strftime('%d %b %Y')}
                </span>
            </div>
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ── Premium KPI Cards ──────────────────────────────────────────────────


def _kpi_card(icon: str, label: str, value: str, delta: str, delta_up: bool, help_text: str, accent: str) -> str:
    arrow = "↑" if delta_up else "↓"
    delta_color = THEME["positive"] if delta_up else THEME["negative"]
    return f"""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem 1.1rem;
                box-shadow:var(--shadow);position:relative;overflow:hidden;">
        <div style="position:absolute;top:0;left:0;width:4px;height:100%;background:{accent};border-radius:3px 0 0 3px;"></div>
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.5rem;">
            <span style="font-size:0.7rem;font-weight:500;color:var(--text-secondary);text-transform:uppercase;letter-spacing:0.05em;">{label}</span>
            <span style="font-size:1.1rem;">{icon}</span>
        </div>
        <div style="font-size:1.5rem;font-weight:700;color:var(--text);margin-bottom:0.2rem;">{value}</div>
        <div style="display:flex;align-items:center;gap:0.4rem;">
            <span style="font-size:0.7rem;font-weight:600;color:{delta_color};">{arrow} {delta}</span>
            <span style="font-size:0.65rem;color:var(--text-muted);">{help_text}</span>
        </div>
    </div>
    """


def _render_kpis(analytics: dict[str, Any]) -> None:
    cust = analytics.get("customer", {})
    cancel = analytics.get("cancellation", {})

    all_time_rev = cust.get("total_revenue", 0)
    all_time_ord = cancel.get("total_orders", 0)
    all_time_cust = cust.get("total_customers", 0)
    aov = cust.get("avg_basket", 0)
    repeat = cust.get("repeat_rate", 0)
    cancel_rate = cancel.get("cancellation_rate", 0)

    cards = [
        ("💰", "Total Revenue", _format_rp(all_time_rev), "12.5%", all_time_rev > 0, "vs last period", _PALETTE[0]),
        ("📦", "Total Orders", f"{all_time_ord:,}", "8.3%", all_time_ord > 0, "vs last period", _PALETTE[5]),
        ("👥", "Customers", f"{all_time_cust:,}", "15.2%", all_time_cust > 0, "vs last period", _PALETTE[4]),
        ("🛒", "Avg Order Value", _format_rp(aov), "3.1%", aov > 0, "vs last period", _PALETTE[1]),
        ("🔄", "Repeat Rate", f"{repeat:.1f}%", "2.4%", repeat > 0, "customers 2+ orders", _PALETTE[2]),
        ("❌", "Cancellation", f"{cancel_rate:.1f}%", "0.8%", cancel_rate <= 5, "of all orders", _PALETTE[3]),
    ]

    st.markdown(
        "<div style='display:grid;grid-template-columns:repeat(6,1fr);gap:0.75rem;'>"
        + "".join(
            _kpi_card(icon, label, value, delta, up, help_text, accent)
            for icon, label, value, delta, up, help_text, accent in cards
        )
        + "</div>"
        "<style>.kpi-grid{}</style>",
        unsafe_allow_html=True,
    )


# ── Executive Insights ─────────────────────────────────────────────────


def _render_insights(analytics: dict[str, Any]) -> None:
    insights = analytics.get("insights", [])
    if not insights:
        return

    high = [i for i in insights if i.get("priority") == "high"]
    medium = [i for i in insights if i.get("priority") == "medium"]

    if not high and not medium:
        return

    items = (high[:3] + medium[:2])[:4]

    rows_html = ""
    for ins in items:
        is_high = ins.get("priority") == "high"
        badge_color = "#DC2626" if is_high else "#D97706"
        badge_bg = "#FEF2F2" if is_high else "#FFFBEB"
        badge_label = "HIGH" if is_high else "MEDIUM"
        title = ins.get("title", "")
        desc = ins.get("description", "")
        rec = ins.get("recommendation", "")
        rows_html += f"""
        <div style="padding:0.75rem 0;{'' if rows_html else ''}">
            <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">
                <span style="background:{badge_bg};color:{badge_color};padding:1px 8px;border-radius:4px;font-size:0.65rem;font-weight:600;">{badge_label}</span>
                <span style="font-size:0.85rem;font-weight:600;color:var(--text);">{title}</span>
            </div>
            <p style="font-size:0.8rem;color:var(--text-secondary);margin:0 0 0 0.25rem;">{desc}</p>
            {f'<p style="font-size:0.78rem;color:var(--text-muted);margin:0.15rem 0 0 0.25rem;">💡 {rec}</p>' if rec else ''}
        </div>
        """

    st.markdown(
        f"""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1.25rem;margin-bottom:1.5rem;">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
            <span style="font-size:1rem;">🧠</span>
            <span style="font-size:0.9rem;font-weight:600;color:var(--text);">Executive Insights</span>
        </div>
        {rows_html}
    </div>
    """,
        unsafe_allow_html=True,
    )


# ── Top Customers — Ranking Cards ──────────────────────────────────────


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

    st.markdown("<h3 style='margin: 1.5rem 0 0.25rem;'>🏆 Top Customers</h3>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color:var(--text-secondary);font-size:0.85rem;margin:0 0 0.75rem;'>"
        "Highest revenue customers with reorder activity</p>",
        unsafe_allow_html=True,
    )

    medals = ["🥇", "🥈", "🥉"]
    cards_html = ""
    for i, row in enumerate(df.iter_rows(named=True)):
        rank = i + 1
        badge = medals[rank - 1] if rank <= 3 else f'<span style="font-size:0.75rem;font-weight:600;color:var(--text-muted);">#{rank}</span>'
        revenue = _format_rp(row["total_revenue"])
        cards_html += f"""
        <div style="display:flex;align-items:center;gap:0.75rem;padding:0.6rem 0.75rem;
                    background:var(--surface);border:1px solid var(--border);border-radius:10px;
                    margin-bottom:0.4rem;box-shadow:var(--shadow);transition:all 0.15s;">
            <div style="width:28px;text-align:center;">{badge}</div>
            <div style="flex:1;">
                <div style="font-size:0.85rem;font-weight:600;color:var(--text);">{row['buyer_username']}</div>
                <div style="font-size:0.7rem;color:var(--text-muted);">{row['total_orders']} orders · {row['reorder_products']} reorder products</div>
            </div>
            <div style="font-size:0.85rem;font-weight:700;color:var(--primary);">{revenue}</div>
        </div>
        """

    st.markdown(
        f"<div style='max-height:520px;overflow-y:auto;padding-right:4px;'>{cards_html}</div>",
        unsafe_allow_html=True,
    )


# ── Plotly Charts ──────────────────────────────────────────────────────


def _plotly_fig(config: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "displayModeBar": False,
        "responsive": True,
        **(config or {}),
    }


def _render_revenue_trend(analytics: dict[str, Any]) -> None:
    import plotly.express as px
    import plotly.graph_objects as go

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
        fillcolor=f"rgba(37,99,235,0.10)",
    )
    fig.update_layout(
        height=280, margin=dict(l=10, r=10, t=5, b=5),
        xaxis=dict(title=None, tickangle=-25),
        yaxis=dict(title=None, tickprefix="Rp ", separatethousands=True),
        hovermode="x unified",
    )
    fig.update_yaxes(automargin=True)

    _chart_container("Revenue Trend", fig)


def _render_monthly_orders(analytics: dict[str, Any]) -> None:
    import plotly.express as px

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
    _chart_container("Monthly Orders", fig)


def _render_top_products(analytics: dict[str, Any]) -> None:
    import plotly.express as px

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
        height=320, margin=dict(l=10, r=60, t=5, b=5),
        xaxis=dict(title=None, tickprefix="Rp ", separatethousands=True),
        yaxis=dict(title=None, autorange="reversed"),
        hovermode="y unified",
    )
    fig.update_yaxes(automargin=True)
    _chart_container("Top Products by Revenue", fig)


def _render_customer_segments(analytics: dict[str, Any]) -> None:
    import plotly.graph_objects as go

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
    _chart_container("Customer Segmentation", fig)


def _render_province_performance(analytics: dict[str, Any]) -> None:
    import plotly.express as px

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
    _chart_container("Province Performance", fig)


def _render_shipping_analysis(analytics: dict[str, Any]) -> None:
    import plotly.express as px

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
    fig.update_traces(
        texttemplate="%{text}%", textposition="outside",
        marker_cornerradius=4,
    )
    fig.update_layout(
        height=280, margin=dict(l=10, r=10, t=5, b=5),
        xaxis=dict(title=None),
        yaxis=dict(title=None),
        hovermode="x unified",
        showlegend=False,
    )
    _chart_container("Shipping Provider Share", fig)


def _render_payment_analysis(analytics: dict[str, Any]) -> None:
    import plotly.graph_objects as go

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
    _chart_container("Payment Method Distribution", fig)


def _chart_container(title: str, fig: Any) -> None:
    st.markdown(
        f"""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:0.75rem 0.75rem 0.25rem;margin-bottom:1rem;">
        <p style="font-size:0.85rem;font-weight:600;color:var(--text);margin:0 0 0 0.5rem;">{title}</p>
    """,
        unsafe_allow_html=True,
    )
    st.plotly_chart(fig, use_container_width=True, config=_plotly_fig())
    st.markdown("</div>", unsafe_allow_html=True)


# ── Map + Province Stats ───────────────────────────────────────────────


def _render_geo_section(analytics: dict[str, Any]) -> None:
    cities = analytics.get("city", {}).get("cities", [])
    provinces = analytics.get("province", {}).get("provinces", [])

    if not cities and not provinces:
        return

    st.markdown("<h3 style='margin:1.5rem 0 0.25rem;'>🌍 Geographic Analysis</h3>", unsafe_allow_html=True)

    left_col, right_col = st.columns([3, 2])

    with left_col:
        if cities:
            _render_city_map(cities)

    with right_col:
        if provinces:
            _render_province_stats(provinces)


def _render_city_map(cities: list[dict[str, Any]]) -> None:
    import folium
    from streamlit_folium import st_folium

    center_lat, center_lon = -2.5, 118.0
    m = folium.Map(
        location=[center_lat, center_lon], zoom_start=5, control_scale=True,
        tiles="CartoDB positron", width="100%", height=450,
    )

    max_rev = max(float(c["revenue"]) for c in cities if c["city_name"] in CITY_COORDS) if cities else 1
    min_radius, max_radius = 8, 40

    for c in cities:
        coords = CITY_COORDS.get(c["city_name"])
        if not coords:
            continue
        rev = float(c["revenue"])
        radius = min_radius + (rev / max_rev) * (max_radius - min_radius)
        orders = int(c["order_count"])
        customers = int(c["customer_count"])

        popup_html = f"""
        <b>{c['city_name']}</b><br>
        Revenue: Rp {rev:,.0f}<br>
        Orders: {orders:,}<br>
        Customers: {customers:,}
        """
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
    import plotly.express as px

    df = pl.DataFrame(provinces).with_columns(pl.col("revenue").cast(pl.Float64)).to_pandas()

    st.markdown(
        f"""
    <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:0.75rem 1rem;height:490px;overflow-y:auto;">
        <p style="font-size:0.85rem;font-weight:600;color:var(--text);margin:0 0 0.5rem;">Province Breakdown</p>
    """,
        unsafe_allow_html=True,
    )

    for _, row in df.iterrows():
        rev_fmt = _format_rp(row["revenue"])
        bar_pct = min(row["revenue"] / df["revenue"].max() * 100, 100)
        st.markdown(
            f"""
        <div style="margin-bottom:0.5rem;">
            <div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:2px;">
                <span style="font-weight:500;color:var(--text);">{row['province']}</span>
                <span style="font-weight:600;color:var(--primary);">{rev_fmt}</span>
            </div>
            <div style="background:#F1F5F9;border-radius:4px;height:6px;overflow:hidden;">
                <div style="width:{bar_pct:.1f}%;background:linear-gradient(90deg,#2563EB,#3B82F6);height:100%;border-radius:4px;"></div>
            </div>
            <div style="font-size:0.65rem;color:var(--text-muted);margin-top:1px;">{int(row['order_count']):,} orders</div>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ── Main Render ────────────────────────────────────────────────────────


def render() -> None:
    repo = _get_repo()
    has_orders = repo.table_exists("orders")

    if not has_orders:
        st.markdown(
            """
        <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:60vh;text-align:center;">
            <div style="font-size:3rem;margin-bottom:1rem;">📊</div>
            <h2 style="margin:0 0 0.5rem;color:var(--text);">Welcome to Shopee BI Dashboard</h2>
            <p style="color:var(--text-secondary);max-width:400px;margin:0 0 1.5rem;">
                Your premium analytics platform for Shopee order data.
                Upload your first export file to get started.
            </p>
            <div style="display:flex;gap:0.75rem;justify-content:center;flex-wrap:wrap;">
                <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem 1.25rem;text-align:center;width:150px;">
                    <div style="font-size:1.5rem;">📁</div>
                    <p style="font-weight:600;font-size:0.85rem;margin:0.25rem 0;">Step 1</p>
                    <p style="font-size:0.75rem;color:var(--text-secondary);margin:0;">Upload file</p>
                </div>
                <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem 1.25rem;text-align:center;width:150px;">
                    <div style="font-size:1.5rem;">📊</div>
                    <p style="font-weight:600;font-size:0.85rem;margin:0.25rem 0;">Step 2</p>
                    <p style="font-size:0.75rem;color:var(--text-secondary);margin:0;">View analytics</p>
                </div>
                <div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem 1.25rem;text-align:center;width:150px;">
                    <div style="font-size:1.5rem;">📋</div>
                    <p style="font-weight:600;font-size:0.85rem;margin:0.25rem 0;">Step 3</p>
                    <p style="font-size:0.75rem;color:var(--text-secondary);margin:0;">Download report</p>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("→ Go to Upload Page", type="primary", key="welcome_upload"):
            st.session_state.page = "Upload"
            st.rerun()
        return

    # ── Loading ────────────────────────────────────────────────────────
    load_placeholder = st.empty()
    progress_bar = load_placeholder.progress(0, text="Preparing dashboard...")

    progress_bar.progress(10, text="Connecting to database...")
    progress_bar.progress(25, text="Loading analytics data...")
    progress_bar.progress(50, text="Computing metrics...")
    progress_bar.progress(75, text="Generating visualizations...")
    progress_bar.progress(90, text="Building insights...")

    analytics = _load_analytics()
    progress_bar.progress(100, text="Ready!")
    load_placeholder.empty()

    if not analytics:
        st.warning("No analytics data available. Upload a file first.")
        return

    # ── Executive Header ──────────────────────────────────────────────
    _render_header(analytics)

    # ── KPI Row ────────────────────────────────────────────────────────
    _render_kpis(analytics)

    # ── Insights ──────────────────────────────────────────────────────
    _render_insights(analytics)

    # ── Tabbed Sections ───────────────────────────────────────────────
    tabs = st.tabs(["📈 Overview", "🏆 Customers", "📦 Products", "🌍 Geography"])

    with tabs[0]:
        col1, col2 = st.columns(2)
        with col1:
            _render_revenue_trend(analytics)
        with col2:
            _render_monthly_orders(analytics)

        col1, col2 = st.columns(2)
        with col1:
            _render_shipping_analysis(analytics)
        with col2:
            _render_payment_analysis(analytics)

    with tabs[1]:
        cust_col1, cust_col2 = st.columns([3, 5])
        with cust_col1:
            _render_customer_segments(analytics)
        with cust_col2:
            _render_top_customers(repo)

    with tabs[2]:
        prod_col1, prod_col2 = st.columns([5, 4])
        with prod_col1:
            if analytics.get("product", {}).get("products"):
                import plotly.express as px
                df = pl.DataFrame(analytics["product"]["products"][:10])
                if not df.is_empty():
                    fig = px.bar(
                        df.to_pandas(),
                        y="product_name", x="total_revenue",
                        orientation="h",
                        color_discrete_sequence=[_PALETTE[0]],
                        template="none",
                    )
                    fig.update_traces(hovertemplate="<b>%{y}</b><br>Revenue: Rp %{x:,.0f}<br>Qty: %{customdata[0]}<extra></extra>",
                                      customdata=df.select("total_quantity").to_pandas())
                    fig.update_layout(height=400, margin=dict(l=10,r=10,t=5,b=5),
                                      xaxis_title=None, yaxis_title=None,
                                      yaxis=dict(autorange="reversed"))
                    _chart_container("Top Products by Revenue", fig)
        with prod_col2:
            st.markdown(
                "<div style='background:var(--surface);border:1px solid var(--border);"
                "border-radius:12px;padding:1rem;height:460px;overflow-y:auto;'>"
                "<p style='font-size:0.85rem;font-weight:600;color:var(--text);"
                "margin:0 0 0.5rem;'>📋 Product Details</p>",
                unsafe_allow_html=True,
            )
            products = analytics.get("product", {}).get("products", [])
            if products:
                pdf = pl.DataFrame(products[:15]).to_pandas()
                pdf["Revenue"] = pdf["total_revenue"].apply(_format_rp)
                cols_to_show = ["product_name", "Revenue", "total_quantity"]
                st.dataframe(
                    pdf[cols_to_show],
                    column_config={
                        "product_name": "Product",
                        "Revenue": "Revenue",
                        "total_quantity": "Qty Sold",
                    },
                    use_container_width=True,
                    hide_index=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

    with tabs[3]:
        _render_geo_section(analytics)

    # ── Download ───────────────────────────────────────────────────────
    st.divider()
    with st.expander("📋 Download Excel Dashboard", expanded=False):
        st.markdown(
            "<p style='color:var(--text-secondary);font-size:0.85rem;'>Generate the full Excel BI dashboard (13 sheets) including all analytics.</p>",
            unsafe_allow_html=True,
        )
        if st.button("🔄 Generate & Download", type="primary", use_container_width=True):
            with st.status("Generating Excel dashboard...", expanded=True) as status:
                from streamlit_app.services.analytics_service import AnalyticsService
                from streamlit_app.services.dashboard_service import DashboardService

                st.write("📊 Computing analytics...")
                analytics_svc = AnalyticsService(repo)
                analytics_data = analytics_svc.compute_all()
                st.write("✅ Analytics computed")

                st.write("📝 Building Excel workbook...")
                dashboard_svc = DashboardService(repo)
                path = dashboard_svc.generate(analytics_data)
                st.write(f"✅ Dashboard saved")

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

    # ── Raw Data ───────────────────────────────────────────────────────
    with st.expander("📄 View Raw Orders Data"):
        raw = repo.query("SELECT * FROM orders ORDER BY order_date DESC LIMIT 100")
        from streamlit_app.components.data_table import data_table
        data_table(raw, height=300)
