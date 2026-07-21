"""Shopee BI Dashboard — Streamlit Application.

Entry point. Loads CSS, inits session state, renders sidebar branding.
Pages are handled by Streamlit native multipage navigation.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from database.connection import get_connection
from database.repository import DuckDBRepository
from streamlit_app.styles.loader import load_css

st.set_page_config(
    page_title="Shopee BI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_css()

_DEFAULTS = {
    "file_hash": None,
    "etl_completed": False,
    "analytics_completed": False,
    "dashboard_generated": False,
    "last_uploaded": None,
    "etl_result": None,
    "dashboard_path": None,
    "dashboard_filename": None,
}
for key, value in _DEFAULTS.items():
    st.session_state.setdefault(key, value)


def _data_freshness_info() -> tuple[str, str]:
    try:
        repo = DuckDBRepository(get_connection())
        if repo.table_exists("orders"):
            df = repo.query(
                "SELECT MIN(order_date) AS first_order, MAX(order_date) AS last_order "
                "FROM orders WHERE order_date IS NOT NULL"
            )
            if df.height > 0:
                first_dt, last_dt = df["first_order"][0], df["last_order"][0]
                fmt = lambda d: d.strftime("%d %b %Y") if hasattr(d, "strftime") else str(d)[:10]
                return (fmt(first_dt) if first_dt else "", fmt(last_dt) if last_dt else "")
    except Exception:
        pass
    return ("", "")


# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-brand-icon">SB</div>
        <div>
            <p class="sidebar-brand-text">Shopee BI</p>
            <p class="sidebar-brand-sub">Business Intelligence</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    has_data = st.session_state.get("etl_completed")
    if has_data:
        last = st.session_state.get("last_uploaded", "unknown")
        last_short = str(last)[:30] + "..." if len(str(last)) > 30 else str(last)
        first_date, last_date = _data_freshness_info()
        status_html = f"""
        <div class="sidebar-status">
            <p class="sidebar-status-label">Data Status</p>
            <div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.25rem;">
                <span style="color:var(--success);font-size:0.85rem;">●</span>
                <span style="font-size:0.8rem;font-weight:500;">Data loaded</span>
            </div>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)
        st.caption(f"File: {last_short}")
        if last_date:
            st.caption(f"Period: {first_date} — {last_date}")
    else:
        status_html = """
        <div class="sidebar-status">
            <p class="sidebar-status-label">Data Status</p>
            <div style="display:flex;align-items:center;gap:0.4rem;margin-bottom:0.25rem;">
                <span style="color:var(--text-muted);font-size:0.85rem;">○</span>
                <span style="font-size:0.8rem;font-weight:500;">No data</span>
            </div>
        </div>
        """
        st.markdown(status_html, unsafe_allow_html=True)
        st.caption("Upload a file to begin")

    st.divider()
    st.caption("v2.0.0 · Premium")
