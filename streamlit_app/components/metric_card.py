"""Reusable MetricCard component — renders a single KPI metric card."""

from __future__ import annotations

from typing import Optional

import streamlit as st

from config.config import THEME


class MetricCard:
    """Styled KPI metric card with accent bar, icon, label, value, and delta.

    Usage:
        MetricCard(icon="💰", label="Revenue", value="Rp 1.2M",
                   delta="+12.5%", delta_up=True, help_text="vs last period",
                   accent=THEME["primary"]).render()
    """

    def __init__(
        self,
        icon: str,
        label: str,
        value: str,
        delta: Optional[str] = None,
        delta_up: Optional[bool] = None,
        help_text: Optional[str] = None,
        accent: str = "",
    ) -> None:
        self.icon = icon
        self.label = label
        self.value = value
        self.delta = delta
        self.delta_up = delta_up
        self.help_text = help_text
        self.accent = accent or THEME["primary"]

    def render(self) -> None:
        try:
            delta_color = THEME["positive"] if self.delta_up else THEME["negative"]
            arrow = "↑" if self.delta_up else "↓" if self.delta_up is not None else ""
            delta_html = ""
            if self.delta:
                delta_html = (
                    f'<span class="metric-card-delta" style="color:{delta_color};">'
                    f"{arrow} {self.delta}</span>"
                )

            st.markdown(
                f"""
            <div class="metric-card">
                <div class="metric-card-accent" style="background:{self.accent};"></div>
                <div class="metric-card-header">
                    <span class="metric-card-label">{self.label}</span>
                    <span class="metric-card-icon">{self.icon}</span>
                </div>
                <div class="metric-card-value">{self.value}</div>
                <div class="metric-card-footer">
                    {delta_html}
                    {f'<span class="metric-card-help">{self.help_text}</span>' if self.help_text else ''}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Failed to render MetricCard: {e}")
