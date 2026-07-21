"""
Upload page — file upload, validation, preview, and ETL trigger.
"""

from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any, Optional

import polars as pl
import streamlit as st

from config.config import CANONICAL_COLUMNS, COLUMN_MAP
from etl.shopee.extractor import ShopeeExtractor
from etl.shopee.transformer import ShopeeTransformer
from streamlit_app.services.etl_service import ETLService


def _validate_columns(df: pl.DataFrame) -> list[str]:
    """Check which canonical columns are present after renaming."""
    rename_map = _build_rename_map(df)
    present = {v for v in rename_map.values() if v in CANONICAL_COLUMNS}
    return list(present)


def _build_rename_map(df: pl.DataFrame) -> dict[str, str]:
    """Simulate the extractor's column renaming."""
    from utils.helpers import safe_string

    rename_map = {}
    for col in df.columns:
        key = safe_string(col).lower()
        target = COLUMN_MAP.get(key, key)
        if target not in rename_map.values():
            rename_map[col] = target
    return rename_map


def _get_etl_service() -> ETLService:
    """Return cached ETL service."""
    from database.connection import get_connection

    conn = get_connection()
    from database.repository import DuckDBRepository

    repo = DuckDBRepository(conn)
    return ETLService(repo)


def _run_etl(file_path: str) -> dict:
    service = _get_etl_service()
    return service.run(file_path)


def render() -> None:
    st.title("Upload Data")
    st.markdown(
        "<p style='color:#64748b;'>Upload a Shopee order export file to process and analyze.</p>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a Shopee export file",
        type=["xlsx", "xls", "csv"],
        key="upload_page_file",
    )

    if not uploaded_file:
        st.info(
            "No file uploaded yet. Upload a Shopee order export (.xlsx, .xls, or .csv) to get started.",
            icon="📁",
        )
        return

    # File hash for cache invalidation
    file_bytes = uploaded_file.getvalue()
    file_hash = hash(file_bytes)

    if st.session_state.get("file_hash") != file_hash:
        st.session_state["file_hash"] = file_hash
        st.session_state["etl_completed"] = False
        st.session_state["analytics_completed"] = False

    # ── Preview ──
    with st.expander("Preview raw data", expanded=True):
        try:
            with NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp:
                tmp.write(file_bytes)
                tmp_path = tmp.name

            extractor = ShopeeExtractor()
            raw_rows = list(extractor.extract(tmp_path))
            preview_df = pl.from_dicts(raw_rows[:5]) if raw_rows else pl.DataFrame()
            if not preview_df.is_empty():
                st.dataframe(preview_df.to_pandas(), use_container_width=True, hide_index=True)
                st.caption(f"Showing first {min(5, len(raw_rows))} of {len(raw_rows)} rows")
            else:
                st.warning("No data could be read from this file.")
                Path(tmp_path).unlink(missing_ok=True)
                return

            found_columns = _validate_columns(preview_df)
            st.markdown(f"**Columns recognized:** {len(found_columns)} / {len(CANONICAL_COLUMNS)}")
        except Exception as exc:
            st.error(f"Failed to read file: {exc}")
            return

    # ── Run ETL ──
    col1, col2 = st.columns([1, 3])
    with col1:
        run_etl = st.button("▶ Run ETL", type="primary", use_container_width=True)

    status_placeholder = st.empty()

    if run_etl:
        status_placeholder.info("Processing...", icon="⚙️")

        try:
            with st.status("Running ETL pipeline...", expanded=True) as status:
                st.write("📂 Extracting data from file...")
                transformer = ShopeeTransformer()
                df = transformer.transform(raw_rows)
                st.write(f"✅ Extracted and transformed {len(df)} rows")

                st.write("🗄️ Loading into database...")
                result = _run_etl(tmp_path)
                st.write(f"✅ Loaded {result['rows_loaded']} rows, warehouse built")

                status.update(label="ETL complete!", state="complete")

            st.session_state["etl_completed"] = True
            st.session_state["etl_result"] = result
            st.session_state["last_uploaded"] = uploaded_file.name

            st.success(f"ETL complete — {result['rows_loaded']} rows loaded.")

            if st.button("→ Go to Dashboard", type="primary"):
                st.switch_page("app.py")

        except Exception as exc:
            status_placeholder.error(f"ETL failed: {exc}", icon="❌")
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    # Show previous ETL status
    if st.session_state.get("etl_completed") and not run_etl:
        st.success(
            f"Previously loaded: {st.session_state.get('etl_result', {}).get('rows_loaded', 0)} rows",
            icon="✅",
        )
