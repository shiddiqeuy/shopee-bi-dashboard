"""Upload page — file upload, preview, ETL trigger, and file management."""

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
from streamlit_app.components.hero_header import HeroHeader
from streamlit_app.services.etl_service import ETLService


def _get_etl_service() -> ETLService:
    return ETLService(DuckDBRepository(get_connection()))


def _validate_columns(df: pl.DataFrame) -> list[str]:
    rename_map = _build_rename_map(df)
    return [v for v in rename_map.values() if v in CANONICAL_COLUMNS]


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
    return _get_etl_service().run(file_path)


def _preview_file(
    file_bytes: bytes, filename: str
) -> tuple[list[dict], pl.DataFrame] | None:
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
    st.markdown("### Upload Files")
    st.markdown(
        '<p style="color:var(--text-secondary);font-size:0.85rem;margin-bottom:0.75rem;">'
        "Upload one or more Shopee order export files. All files are saved to the input directory.</p>",
        unsafe_allow_html=True,
    )

    uploaded_files = st.file_uploader(
        "Choose Shopee export file(s)",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=True,
        key="upload_page_file",
    )

    if not uploaded_files:
        return

    new_files = [
        f for f in uploaded_files
        if hash(f.getvalue()) != st.session_state.get("file_hash")
    ]
    if not new_files:
        st.info("All files have already been processed. Select new files to upload.")
        if st.button("→ Go to Dashboard", type="primary"):
            st.switch_page("streamlit_app/app.py")
        return

    if st.button("💾 Save & Run ETL on All", type="primary", use_container_width=True):
        status_placeholder = st.status(
            f"Processing {len(new_files)} file(s)...", expanded=True
        )

        total_rows = 0
        success_count = 0
        file_results = []

        for i, uploaded_file in enumerate(new_files):
            file_bytes = uploaded_file.getvalue()

            with status_placeholder:
                st.write(f"**{i+1}/{len(new_files)}** — `{uploaded_file.name}`")
                st.write("📁 Saving file...")
                saved_path = ETLService.save_upload(file_bytes, uploaded_file.name)

                st.write("📂 Previewing...")
                result = _preview_file(file_bytes, uploaded_file.name)
                if result is None:
                    st.warning(f"Skipped `{uploaded_file.name}` — could not read file.")
                    continue

                st.write("🗄️ Running ETL...")
                etl_result = _run_etl(str(saved_path))
                total_rows += etl_result["rows_loaded"]
                success_count += 1
                file_results.append((uploaded_file.name, etl_result["rows_loaded"]))
                st.write(f"✅ `{uploaded_file.name}` — {etl_result['rows_loaded']} rows loaded")
                st.session_state["file_hash"] = hash(file_bytes)

        status_placeholder.update(
            label=f"Processed {success_count}/{len(new_files)} file(s), {total_rows} total rows",
            state="complete",
        )

        st.session_state["etl_completed"] = True
        st.cache_data.clear()
        st.session_state["last_uploaded"] = (
            f"{success_count} files (last: {new_files[-1].name})"
        )
        st.success(f"✅ {success_count} file(s) processed — {total_rows} rows loaded total.")

        for name, rows in file_results:
            st.caption(f"  • {name}: {rows} rows")

        if st.button("→ Go to Dashboard", type="primary"):
            st.switch_page("streamlit_app/app.py")


def _render_file_management() -> None:
    st.markdown("### Existing Files")
    st.markdown(
        '<p style="color:var(--text-secondary);font-size:0.85rem;margin-bottom:0.75rem;">'
        "Manage files in the input directory.</p>",
        unsafe_allow_html=True,
    )

    files = ETLService.list_files()

    col_refresh, col_clear = st.columns([1, 8])
    with col_refresh:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    with col_clear:
        if st.button("🗑️ Clear All Files", type="secondary", use_container_width=True):
            count = ETLService.clear_all()
            st.success(f"Deleted {count} file(s).")
            st.rerun()

    if not files:
        st.info("No files in input directory.", icon="📁")
        return

    st.markdown(
        f'<p style="font-size:0.8rem;font-weight:500;color:var(--text-secondary);'
        f'margin-bottom:0.5rem;">{len(files)} file(s) in <code>{INPUT_DIR}</code></p>',
        unsafe_allow_html=True,
    )

    for f in files:
        mod_time = datetime.fromtimestamp(f["modified"]).strftime("%Y-%m-%d %H:%M:%S")
        cols = st.columns([3, 1, 1.5, 1.5, 1.5])
        with cols[0]:
            st.markdown(f"**{f['name']}**")
        with cols[1]:
            st.caption(f["size_display"])
        with cols[2]:
            st.caption(mod_time)
        with cols[3]:
            if st.button("▶ Run ETL", key=f"etl_{f['name']}", use_container_width=True):
                _run_etl_on_file(f["name"])
        with cols[4]:
            if st.button("🗑️ Delete", key=f"del_{f['name']}", use_container_width=True):
                ETLService.delete_file(f["name"])
                st.rerun()


def _run_etl_on_file(filename: str) -> None:
    file_path = str(INPUT_DIR / filename)
    with st.status(f"Running ETL on `{filename}`...", expanded=True) as status:
        st.write("📂 Processing file...")
        try:
            result = _run_etl(file_path)
            st.write(f"✅ Loaded {result['rows_loaded']} rows, warehouse built")
            status.update(label="ETL complete!", state="complete")
            st.session_state["etl_completed"] = True
            st.cache_data.clear()
            st.session_state["etl_result"] = result
            st.session_state["last_uploaded"] = filename
            st.success(f"ETL complete — {result['rows_loaded']} rows loaded.")
        except Exception as exc:
            st.error(f"ETL failed: {exc}")
            status.update(label="ETL failed", state="error")


def render() -> None:
    HeroHeader(
        title="📁 Upload Data",
        subtitle="Upload Shopee export files, run ETL, and build the analytics warehouse.",
    ).render()

    _render_file_management()
    st.divider()
    _render_upload_section()


render()
