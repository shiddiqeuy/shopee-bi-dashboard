"""
Reusable KPI metric card component.

Renders a single KPI with label, value, and optional delta/trend.
"""

from __future__ import annotations

from typing import Optional


def metric_card(
    label: str,
    value: str,
    delta: Optional[str] = None,
    help_text: Optional[str] = None,
) -> None:
    """Render a styled KPI metric card.

    Parameters
    ----------
    label:
        Short description (e.g. "Total Revenue")
    value:
        Formatted value (e.g. "Rp 293,199,976")
    delta:
        Optional change indicator (e.g. "+12.5%")
    help_text:
        Optional tooltip.
    """
    import streamlit as st

    with st.container(border=True):
        cols = st.columns([1, 1])
        with cols[0]:
            st.markdown(
                f"<p style='color:#64748b; font-size:0.8rem; margin-bottom:4px;'>{label}</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='font-size:1.5rem; font-weight:700; margin:0;'>{value}</p>",
                unsafe_allow_html=True,
            )
            if delta:
                is_positive = delta.startswith("+")
                color = "#10b981" if is_positive else "#ef4444"
                st.markdown(
                    f"<p style='color:{color}; font-size:0.8rem; margin:0;'>{delta}</p>",
                    unsafe_allow_html=True,
                )
        with cols[1]:
            if help_text:
                st.caption(help_text)
