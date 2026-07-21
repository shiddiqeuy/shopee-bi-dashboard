"""CSS loader — reads main.css and injects into Streamlit app."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

_CSS_PATH = Path(__file__).resolve().parent / "main.css"


def load_css() -> None:
    """Inject global stylesheet + theme CSS variables into the app."""
    from streamlit_app.styles.themes import inject_theme_css
    css = _CSS_PATH.read_text(encoding="utf-8")
    st.markdown(inject_theme_css(), unsafe_allow_html=True)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
