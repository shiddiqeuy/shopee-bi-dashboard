"""ChartCard component — wraps any chart inside a consistent container."""

from __future__ import annotations

from typing import Any, Optional

import streamlit as st


_DISPLAY_MODE_BAR = False


class ChartCard:
    """Chart container with title, optional helper text, and config.

    Usage:
        ChartCard("Revenue Trend", fig).render()
        ChartCard("Revenue Trend", fig, help_text="Monthly revenue in IDR").render()
    """

    def __init__(
        self,
        title: str,
        fig: Any,
        height: Optional[int] = None,
        help_text: Optional[str] = None,
    ) -> None:
        self.title = title
        self.fig = fig
        self.height = height
        self.help_text = help_text

    def render(self) -> None:
        st.markdown(
            f"""
        <div class="chart-container">
            <p class="chart-title">{self.title}</p>
        """,
            unsafe_allow_html=True,
        )
        if self.help_text:
            st.caption(self.help_text)
        st.plotly_chart(
            self.fig,
            use_container_width=True,
            config={"displayModeBar": _DISPLAY_MODE_BAR, "responsive": True},
        )
        st.markdown("</div>", unsafe_allow_html=True)
