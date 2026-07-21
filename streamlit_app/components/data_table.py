"""
Data table component — styled DataFrame display.
"""

from __future__ import annotations

from typing import Any, Optional

import polars as pl


def data_table(
    df: pl.DataFrame,
    title: Optional[str] = None,
    height: int = 400,
) -> None:
    """Render a Polars DataFrame as a styled table.

    Parameters
    ----------
    df:
        Data to display.
    title:
        Optional section title above the table.
    height:
        Maximum table height in pixels.
    """
    import streamlit as st

    with st.container(border=True):
        if title:
            st.markdown(
                f"<p style='color:#1e293b; font-size:0.95rem; font-weight:600; margin-bottom:8px;'>{title}</p>",
                unsafe_allow_html=True,
            )
        st.dataframe(
            df.to_pandas(),
            use_container_width=True,
            height=height,
            hide_index=True,
        )
