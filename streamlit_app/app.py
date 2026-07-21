"""
Shopee BI Dashboard — Streamlit Application.

Entry point for the Streamlit app. Handles sidebar navigation,
session state initialization, and page routing.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import streamlit as st

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from database.connection import get_connection
from database.repository import DuckDBRepository
from streamlit_app.pages import dashboard_page, upload, settings

st.set_page_config(
    page_title="Shopee BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ─────────────────────────────────────────────
_DEFAULTS = {
    "page": "Dashboard",
    "file_hash": None,
    "etl_completed": False,
    "analytics_completed": False,
    "dashboard_generated": False,
    "last_uploaded": None,
    "etl_result": None,
}
for key, value in _DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def _data_freshness_info() -> str:
    """Return last order date from DB, or empty string."""
    try:
        repo = DuckDBRepository(get_connection())
        if repo.table_exists("orders"):
            df = repo.query(
                "SELECT MAX(order_date) AS last_order FROM orders WHERE order_date IS NOT NULL"
            )
            if df.height > 0 and df["last_order"][0] is not None:
                dt = df["last_order"][0]
                if hasattr(dt, "strftime"):
                    return dt.strftime("%d %b %Y")
                return str(dt)[:10]
    except Exception:
        pass
    return ""


# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='margin-bottom:0;'>📊 Shopee BI</h2>"
        "<p style='color:#64748b; font-size:0.8rem; margin-top:0;'>Business Intelligence Dashboard</p>",
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Navigation ──
    pages = {
        "Dashboard": ("📈", "Analytics & charts"),
        "Upload": ("📁", "Upload & manage files"),
        "Settings": ("⚙️", "Configuration"),
    }

    for name, (icon, desc) in pages.items():
        active = st.session_state.page == name
        label = f"{icon} **{name}**" if not active else f"{icon} **{name}**"
        if st.button(
            label,
            key=f"nav_{name}",
            use_container_width=True,
            type="primary" if active else "secondary",
            help=desc,
        ):
            st.session_state.page = name
            st.rerun()

    st.divider()

    # ── Data Status ──
    st.markdown("##### Data Status")
    if st.session_state.get("etl_completed"):
        last = st.session_state.get("last_uploaded", "unknown")
        st.markdown(f"✅ **Loaded**")
        st.caption(f"File: {last}")
        freshness = _data_freshness_info()
        if freshness:
            st.caption(f"Last order: {freshness}")
    else:
        st.markdown("⏳ **No data**")
        st.caption("Upload a file to begin")

    st.divider()

    # ── Quick Guide ──
    with st.expander("💡 Quick Guide", expanded=False):
        st.markdown(
            """
**1. Upload** – Upload file(s) → auto ETL  
**2. Dashboard** – KPIs, charts, customer insights, download Excel  
**3. Settings** – System info, parameters, data management
"""
        )

    st.divider()
    st.caption("v1.0.0")

# ── Page routing ───────────────────────────────────────────────────────
page = st.session_state.page

if page == "Dashboard":
    dashboard_page.render()
elif page == "Upload":
    upload.render()
elif page == "Settings":
    settings.render()
