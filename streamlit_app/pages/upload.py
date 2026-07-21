"""
Upload page — file upload, preview, ETL trigger, and file management.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

import polars as pl
import streamlit as st

from config.config import CANONICAL_COLUMNS, COLUMN_MAP, INPUT_DIR
from database.connection import get_connection
from database.repository import DuckDBRepository
from etl.shopee.extractor import ShopeeExtractor
from etl.shopee.transformer import ShopeeTransformer
from streamlit_app.services.etl_service import ETLService


def _get_etl_service() -> ETLService:
    conn = get_connection()
    repo = DuckDBRepository(conn)
    return ETLService(repo)


def _validate_columns(df: pl.DataFrame) -> list[str]:
    rename_map = _build_rename_map(df)
    present = {v for v in rename_map.values() if v in CANONICAL_COLUMNS}
    return list(present)


def _build_rename_map(df: pl.DataFrame) -> dict[str, str]:
    from utils.helpers import safe_string

    rename_map = {}
    for col in df.columns:
        key = safe_string(col).lower()
        target = COLUMN_MAP.get(key, key)
        if target not in rename_map.values():
            rename_map[col] = target
    return rename_map


def _run_etl(file_path: str) -> dict:
    service = _get_etl_service()
    return service.run(file_path)


def _preview_file(file_bytes: bytes, filename: str) -> tuple[list[dict], pl.DataFrame] | None:
    """Preview an uploaded file. Returns (raw_rows, preview_df) or None on error."""
    try:
        with NamedTemporaryFile(delete=False, suffix=Path(filename).suffix) as tmp:
            tmp.write(file_bytes)
            tmp_path = tmp.name

        extractor = ShopeeExtractor()
        raw_rows = list(extractor.extract(tmp_path))
        preview_df = pl.from_dicts(raw_rows[:5]) if raw_rows else pl.DataFrame()

        Path(tmp_path).unlink(missing_ok=True)
        return raw_rows, preview_df
    except Exception as exc:
        st.error(f"Failed to read file: {exc}")
        return None


def _render_upload_section() -> None:
    """Upload new file, preview, and trigger ETL."""
    st.markdown("### Upload New File")
    st.markdown(
        "<p style='color:#64748b;'>Upload a Shopee order export file to save it to the input directory and process it.</p>",
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Choose a Shopee export file",
        type=["xlsx", "xls", "csv"],
        key="upload_page_file",
    )

    if not uploaded_file:
        return

    file_bytes = uploaded_file.getvalue()
    file_hash = hash(file_bytes)

    if st.session_state.get("file_hash") != file_hash:
        st.session_state["file_hash"] = file_hash
        st.session_state["etl_completed"] = False
        st.session_state["analytics_completed"] = False

    # ── Preview ──
    preview_result = _preview_file(file_bytes, uploaded_file.name)
    if preview_result is None:
        return
    raw_rows, preview_df = preview_result

    with st.expander("Preview raw data", expanded=True):
        if not preview_df.is_empty():
            st.dataframe(preview_df.to_pandas(), use_container_width=True, hide_index=True)
            st.caption(f"Showing first {min(5, len(raw_rows))} of {len(raw_rows)} rows")
        else:
            st.warning("No data could be read from this file.")
            return

        found_columns = _validate_columns(preview_df)
        st.markdown(f"**Columns recognized:** {len(found_columns)} / {len(CANONICAL_COLUMNS)}")

    # ── Save + Run ETL ──
    col1, col2 = st.columns([1, 3])
    with col1:
        run_etl = st.button("💾 Save & Run ETL", type="primary", use_container_width=True)

    if run_etl:
        with st.status("Saving and running ETL pipeline...", expanded=True) as status:
            st.write("📁 Saving file to input directory...")
            saved_path = ETLService.save_upload(file_bytes, uploaded_file.name)
            st.write(f"✅ Saved as `{saved_path.name}`")

            st.write("📂 Extracting data from file...")
            transformer = ShopeeTransformer()
            df = transformer.transform(raw_rows)
            st.write(f"✅ Extracted and transformed {len(df)} rows")

            st.write("🗄️ Loading into database...")
            result = _run_etl(str(saved_path))
            st.write(f"✅ Loaded {result['rows_loaded']} rows, warehouse built")

            status.update(label="ETL complete!", state="complete")

        st.session_state["etl_completed"] = True
        st.session_state["etl_result"] = result
        st.session_state["last_uploaded"] = uploaded_file.name

        st.success(f"File saved and processed — {result['rows_loaded']} rows loaded.")

        if st.button("→ Go to Dashboard", type="primary"):
            st.switch_page("app.py")


def _render_file_management() -> None:
    """List, delete, and re-run ETL on existing files in INPUT_DIR."""
    st.markdown("### Existing Files")
    st.markdown(
        "<p style='color:#64748b;'>Manage files in the input directory.</p>",
        unsafe_allow_html=True,
    )

    files = ETLService.list_files()

    col_refresh, col_clear = st.columns([1, 8])
    with col_refresh:
        refresh = st.button("🔄 Refresh", use_container_width=True)
    with col_clear:
        clear_all = st.button("🗑️ Clear All Files", type="secondary", use_container_width=True)
        if clear_all:
            count = ETLService.clear_all()
            st.success(f"Deleted {count} file(s).")
            st.rerun()

    if refresh:
        st.rerun()

    if not files:
        st.info("No files in input directory.", icon="📁")
        return

    # ── File table ──
    st.markdown(f"**{len(files)} file(s)** in `{INPUT_DIR}`")

    for f in files:
        mod_time = datetime.fromtimestamp(f["modified"]).strftime("%Y-%m-%d %H:%M:%S")
        cols = st.columns([3, 1, 1.5, 1.5, 1.5])
        with cols[0]:
            st.markdown(f"**{f['name']}**")
        with cols[1]:
            st.caption(f["size_display"])
        with cols[2]:
            st.caption(f"{mod_time}")
        with cols[3]:
            if st.button("▶ Run ETL", key=f"etl_{f['name']}", use_container_width=True):
                _run_etl_on_file(f["name"])
        with cols[4]:
            if st.button("🗑️ Delete", key=f"del_{f['name']}", use_container_width=True):
                ETLService.delete_file(f["name"])
                st.rerun()


def _run_etl_on_file(filename: str) -> None:
    """Run ETL on a file from the input directory."""
    file_path = str(INPUT_DIR / filename)
    with st.status(f"Running ETL on `{filename}`...", expanded=True) as status:
        st.write("📂 Processing file...")
        try:
            result = _run_etl(file_path)
            st.write(f"✅ Loaded {result['rows_loaded']} rows, warehouse built")
            status.update(label="ETL complete!", state="complete")

            st.session_state["etl_completed"] = True
            st.session_state["etl_result"] = result
            st.session_state["last_uploaded"] = filename

            st.success(f"ETL complete — {result['rows_loaded']} rows loaded.")
        except Exception as exc:
            st.error(f"ETL failed: {exc}")
            status.update(label="ETL failed", state="error")


def render() -> None:
    st.title("Upload Data")

    _render_file_management()
    st.divider()
    _render_upload_section()
