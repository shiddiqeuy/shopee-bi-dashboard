"""DataTable component — styled table display for Polars DataFrames."""

from __future__ import annotations

from typing import Any, Optional

import polars as pl
import streamlit as st


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
        Optional section title.
    height:
        Maximum table height in pixels.
    """
    with st.container(border=True):
        if title:
            st.markdown(f'<p class="card-title">{title}</p>', unsafe_allow_html=True)
        st.dataframe(
            df.to_pandas(),
            use_container_width=True,
            height=height,
            hide_index=True,
        )
