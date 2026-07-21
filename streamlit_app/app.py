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


# ── Sidebar HTML/CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
    .sidebar-header {
        font-size: 1.2rem; font-weight: 700; margin-bottom: 0;
    }
    .sidebar-sub {
        color: #64748b; font-size: 0.75rem; margin-top: 0; margin-bottom: 0.5rem;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button {
        justify-content: flex-start; text-align: left;
        padding: 0.4rem 0.75rem; border: none;
        box-shadow: none !important; font-size: 0.9rem;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button:hover {
        background: #f1f5f9; border: none;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="primary"] {
        background: #e0f2fe; color: #1B98F5; font-weight: 600;
    }
    section[data-testid="stSidebar"] div[data-testid="stButton"] button[kind="secondary"] {
        background: transparent; color: #334155;
    }
    .stSidebar .st-cb { display: none; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<p class="sidebar-header">📊 Shopee BI</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-sub">Business Intelligence Dashboard</p>', unsafe_allow_html=True)

    st.divider()

    # ── Navigation (custom HTML) ──
    pages = [
        ("📈", "Dashboard", "Analytics & charts"),
        ("📁", "Upload", "Upload & manage files"),
        ("⚙️", "Settings", "Configuration"),
    ]

    for icon, name, desc in pages:
        active = st.session_state.page == name
        klass = "nav-item active" if active else "nav-item"
        if st.button(
            f"{icon} {name}",
            key=f"nav_{name}",
            use_container_width=True,
            type="primary" if active else "secondary",
            help=desc,
        ):
            st.session_state.page = name
            st.rerun()

    st.divider()

    # ── Data Status ──
    has_data = st.session_state.get("etl_completed")
    if has_data:
        last = st.session_state.get("last_uploaded", "unknown")
        st.markdown("##### Data Status")
        last_short = last if len(str(last)) < 30 else str(last)[:27] + "..."
        st.markdown(f"✅ **Loaded**  \n{last_short}")
        freshness = _data_freshness_info()
        if freshness:
            st.caption(f"Last order: {freshness}")
    else:
        st.markdown("##### Getting Started")
        st.markdown("Upload a Shopee export file to begin.")

    st.divider()

    with st.expander("💡 Guide", expanded=False):
        st.markdown(
            """
**1.** Upload file(s) → auto ETL  
**2.** View KPIs, charts, insights  
**3.** Download Excel report (13 sheets)
"""
        )

    st.caption("v1.0.0")

# ── Page routing ───────────────────────────────────────────────────────
page = st.session_state.page

if page == "Dashboard":
    dashboard_page.render()
elif page == "Upload":
    upload.render()
elif page == "Settings":
    settings.render()
