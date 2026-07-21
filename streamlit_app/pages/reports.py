"""
Reports page — download generated Excel dashboard.
"""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import streamlit as st

from config.config import DASHBOARD_OUTPUT
from database.connection import get_connection
from database.repository import DuckDBRepository
from streamlit_app.services.analytics_service import AnalyticsService
from streamlit_app.services.dashboard_service import DashboardService


def _get_repo() -> DuckDBRepository:
    return DuckDBRepository(get_connection())


def render() -> None:
    st.title("Reports")

    repo = _get_repo()
    if not repo.table_exists("fact_sales"):
        st.info("No data yet. Upload data first on the **Upload** page.", icon="📁")
        return

    st.markdown(
        "<p style='color:#64748b;'>Generate and download the full Excel BI dashboard with all analytics sheets.</p>",
        unsafe_allow_html=True,
    )

    # Check if existing dashboard is still valid
    dashboard_exists = DASHBOARD_OUTPUT.exists()
    if dashboard_exists:
        mtime = datetime.fromtimestamp(DASHBOARD_OUTPUT.stat().st_mtime)
        st.info(f"Existing dashboard: {mtime.strftime('%Y-%m-%d %H:%M')}")

    col1, col2 = st.columns([1, 3])
    with col1:
        generate = st.button("🔄 Generate Dashboard", type="primary", use_container_width=True)

    if generate:
        with st.status("Generating Excel dashboard...", expanded=True) as status:
            st.write("📊 Computing analytics...")
            analytics_service = AnalyticsService(repo)
            analytics = analytics_service.compute_all()
            st.write("✅ Analytics computed")

            st.write("📝 Building Excel workbook...")
            dashboard_service = DashboardService(repo)
            path = dashboard_service.generate(analytics)
            st.write(f"✅ Dashboard saved")

            status.update(label="Dashboard generated!", state="complete")

        st.success(f"Dashboard saved to: {path}")

        # Read file for download
        with open(path, "rb") as f:
            st.download_button(
                label="📥 Download Excel Dashboard",
                data=f,
                file_name=Path(path).name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )

    if dashboard_exists and not generate:
        with open(DASHBOARD_OUTPUT, "rb") as f:
            st.download_button(
                label="📥 Download Latest Dashboard",
                data=f,
                file_name=DASHBOARD_OUTPUT.name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True,
            )
