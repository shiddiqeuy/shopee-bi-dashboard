"""
Shopee BI Dashboard — Streamlit Application.

Entry point for the Streamlit app. Handles sidebar navigation,
session state initialization, and page routing.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from streamlit_app.pages import dashboard_page, upload, reports, settings

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

# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='margin-bottom:0;'>📊 Shopee BI</h2>"
        "<p style='color:#64748b; font-size:0.8rem; margin-top:0;'>Business Intelligence Dashboard</p>",
        unsafe_allow_html=True,
    )

    st.divider()

    pages = {
        "Dashboard": "📈",
        "Upload": "📁",
        "Reports": "📋",
        "Settings": "⚙️",
    }

    for name, icon in pages.items():
        if st.button(
            f"{icon} {name}",
            key=f"nav_{name}",
            use_container_width=True,
            type="secondary" if st.session_state.page != name else "primary",
        ):
            st.session_state.page = name
            st.rerun()

    st.divider()

    # Status section
    st.markdown("### Status")
    if st.session_state.get("etl_completed"):
        last = st.session_state.get("last_uploaded", "unknown")
        st.markdown(f"✅ **Data loaded**")
        st.caption(f"File: {last}")
    else:
        st.markdown("⏳ **No data**")
        st.caption("Upload a file to begin")

    st.divider()
    st.caption("v1.0.0")

# ── Page routing ───────────────────────────────────────────────────────
page = st.session_state.page

if page == "Dashboard":
    dashboard_page.render()
elif page == "Upload":
    upload.render()
elif page == "Reports":
    reports.render()
elif page == "Settings":
    settings.render()
