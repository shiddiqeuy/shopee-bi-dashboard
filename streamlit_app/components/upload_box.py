"""
Upload box component — file upload with drag-and-drop and validation.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st


def upload_box(key: str = "file_upload") -> Optional[bytes]:
    """Render a styled file upload area for Shopee Excel exports.

    Returns the file bytes if uploaded, None otherwise.
    """
    return st.file_uploader(
        "Upload Shopee Order Export",
        type=["xlsx", "xls", "csv"],
        accept_multiple_files=False,
        key=key,
    )
