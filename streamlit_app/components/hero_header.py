"""HeroHeader component — gradient hero bar for page tops."""

from __future__ import annotations

from typing import Optional

import streamlit as st


class HeroHeader:
    """Gradient hero banner with title, subtitle, and optional right-side badge.

    Usage:
        HeroHeader(title="Dashboard", subtitle="Overview & analytics",
                   badge="Today").render()
    """

    def __init__(
        self,
        title: str,
        subtitle: str = "",
        badge: Optional[str] = None,
    ) -> None:
        self.title = title
        self.subtitle = subtitle
        self.badge = badge

    def render(self) -> None:
        badge_html = (
            f'<span class="hero-header-badge" '
            f'style="background:rgba(255,255,255,0.15);color:white;">'
            f"{self.badge}</span>"
            if self.badge
            else ""
        )
        st.markdown(
            f"""
        <div class="hero-header"
             style="background:linear-gradient(135deg,#2563EB,#1D4ED8);">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;flex-wrap:wrap;gap:1rem;">
                <div>
                    <p class="hero-header-overview" style="color:rgba(255,255,255,0.7);">
                        {self.subtitle.upper() if self.subtitle else ''}</p>
                    <h1 class="hero-header-title" style="color:white;">{self.title}</h1>
                    {f'<p class="hero-header-subtitle" style="color:rgba(255,255,255,0.6);">'
                     f'{self.subtitle}</p>' if self.subtitle and False else ''}
                </div>
                {f'<div style="text-align:right;">{badge_html}</div>' if self.badge else ''}
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
