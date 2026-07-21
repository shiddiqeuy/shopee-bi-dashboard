"""
Settings page — configuration and system information.
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

from config.config import DB_PATH, INPUT_DIR, LOG_DIR, OUTPUT_DIR, ANALYTICS


def render() -> None:
    st.markdown(
        """
    <div style="background:linear-gradient(135deg,#2563EB,#1D4ED8);border-radius:16px;padding:1.5rem 2rem;margin-bottom:1.5rem;">
        <h1 style="color:white;font-size:1.4rem;font-weight:700;margin:0;">⚙️ Settings</h1>
        <p style="color:rgba(255,255,255,0.6);font-size:0.85rem;margin:0.25rem 0 0;">
            System configuration, data management, and analytics parameters.
        </p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # ── System Info ────────────────────────────────────────────────────
    st.markdown(
        "<h3 style='font-size:1rem;font-weight:600;color:var(--text);margin-bottom:0.75rem;'>System Information</h3>",
        unsafe_allow_html=True,
    )

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

    st.markdown(
        "<div style='background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem;margin-bottom:1.5rem;'>",
        unsafe_allow_html=True,
    )
    for label, value in info.items():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"<span style='font-size:0.8rem;font-weight:500;color:var(--text-secondary);'>{label}</span>", unsafe_allow_html=True)
        with col2:
            st.markdown(f"<span style='font-size:0.8rem;color:var(--text);'>{value}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Analytics Params ───────────────────────────────────────────────
    st.markdown(
        "<h3 style='font-size:1rem;font-weight:600;color:var(--text);margin:0 0 0.75rem;'>Analytics Parameters</h3>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem;margin-bottom:1.5rem;'>",
        unsafe_allow_html=True,
    )
    for key, value in ANALYTICS.items():
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown(f"<span style='font-size:0.8rem;font-weight:500;color:var(--text-secondary);'>{key}</span>", unsafe_allow_html=True)
        with col2:
            if isinstance(value, dict):
                st.json(value)
            else:
                st.markdown(f"<span style='font-size:0.8rem;color:var(--text);'>{value}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Data Management ────────────────────────────────────────────────
    st.markdown(
        "<h3 style='font-size:1rem;font-weight:600;color:var(--text);margin:0 0 0.75rem;'>Data Management</h3>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div style='background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:1rem;'>",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
            from database.connection import get_connection

            conn = get_connection()
            conn.execute("DELETE FROM orders")
            for tbl in ["fact_sales", "dim_customer", "dim_product", "dim_city", "dim_date"]:
                conn.execute(f"DROP TABLE IF EXISTS {tbl}")
            st.success("All data cleared.")
            st.rerun()

    with col3:
        if st.button("🔄 Reset Warehouse", type="secondary", use_container_width=True):
            from database.connection import get_connection
            from database.repository import DuckDBRepository

            repo = DuckDBRepository(get_connection())
            if repo.table_exists("orders"):
                repo.build_warehouse()
                st.success("Warehouse rebuilt.")
            else:
                st.warning("No data to rebuild from.")
    st.markdown("</div>", unsafe_allow_html=True)
