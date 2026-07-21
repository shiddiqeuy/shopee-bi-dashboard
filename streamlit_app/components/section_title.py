"""SectionTitle component — standardised section header."""

from __future__ import annotations

import streamlit as st


class SectionTitle:
    """Standard section header with title and optional subtitle.

    Usage:
        SectionTitle("Revenue Overview", "Monthly revenue breakdown").render()
    """

    def __init__(self, title: str, subtitle: str = "") -> None:
        self.title = title
        self.subtitle = subtitle

    def render(self) -> None:
        try:
            st.markdown(f'<h3 class="section-header">{self.title}</h3>', unsafe_allow_html=True)
            if self.subtitle:
                st.markdown(f'<p class="section-subtitle">{self.subtitle}</p>', unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Failed to render SectionTitle: {e}")
