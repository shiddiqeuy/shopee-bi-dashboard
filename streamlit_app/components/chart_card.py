"""
Chart card component — wraps an Altair chart with a title.
"""

from __future__ import annotations

from typing import Any, Optional


def chart_card(title: str, chart: Any, height: int = 400) -> None:
    """Render an Altair chart inside a bordered container.

    Parameters
    ----------
    title:
        Chart title displayed above the chart.
    chart:
        Altair chart object.
    height:
        Chart height in pixels.
    """
    import streamlit as st

    with st.container(border=True):
        st.markdown(
            f"<p style='color:#1e293b; font-size:0.95rem; font-weight:600; margin-bottom:8px;'>{title}</p>",
            unsafe_allow_html=True,
        )
        st.altair_chart(chart, use_container_width=True)
