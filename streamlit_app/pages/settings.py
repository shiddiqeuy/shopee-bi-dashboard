"""
Settings page — configuration and system information.
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from config.config import DB_PATH, INPUT_DIR, LOG_DIR, OUTPUT_DIR, ANALYTICS


def render() -> None:
    st.title("Settings")

    st.markdown("### System Information")

    db_size = DB_PATH.stat().st_size if DB_PATH.exists() else 0
    input_files = list(INPUT_DIR.glob("*.*")) if INPUT_DIR.exists() else []
    log_files = list(LOG_DIR.glob("*.log*")) if LOG_DIR.exists() else []

    info = {
        "Database": str(DB_PATH),
        "Database Size": f"{db_size / 1024:.1f} KB",
        "Input Directory": str(INPUT_DIR),
        "Input Files": str(len(input_files)),
        "Output Directory": str(OUTPUT_DIR),
        "Log Files": str(len(log_files)),
    }

    for label, value in info.items():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**{label}**")
        with col2:
            st.markdown(value)

    st.divider()
    st.markdown("### Analytics Parameters")

    for key, value in ANALYTICS.items():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"**{key}**")
        with col2:
            if isinstance(value, dict):
                st.json(value)
            else:
                st.markdown(str(value))

    st.divider()
    st.markdown("### Data Management")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Clear All Data", type="secondary"):
            from database.connection import get_connection

            conn = get_connection()
            conn.execute("DELETE FROM orders")
            for tbl in ["fact_sales", "dim_customer", "dim_product", "dim_city", "dim_date"]:
                conn.execute(f"DROP TABLE IF EXISTS {tbl}")
            st.success("All data cleared.")
            st.rerun()

    with col3:
        if st.button("🔄 Reset Warehouse", type="secondary"):
            from database.connection import get_connection
            from database.repository import DuckDBRepository

            repo = DuckDBRepository(get_connection())
            if repo.table_exists("orders"):
                repo.build_warehouse()
                st.success("Warehouse rebuilt.")
            else:
                st.warning("No data to rebuild from.")
