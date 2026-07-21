"""InsightCard component — renders priority-coded business insight items."""

from __future__ import annotations

from typing import Any

import streamlit as st


class InsightCard:
    """Collapsible insight panel with priority badges.

    Usage:
        InsightCard(insights=[
            {"priority": "high", "title": "Stock Alert", "description": "...", "recommendation": "..."}
        ]).render()
    """

    def __init__(self, insights: list[dict[str, Any]]) -> None:
        self.insights = insights

    def render(self) -> None:
        try:
            if not self.insights:
                return

            high = [i for i in self.insights if i.get("priority") == "high"]
            medium = [i for i in self.insights if i.get("priority") == "medium"]

            if not high and not medium:
                return

            items = (high[:3] + medium[:2])[:4]

            rows = ""
            for ins in items:
                is_high = ins.get("priority") == "high"
                badge_color = "#DC2626" if is_high else "#D97706"
                badge_bg = "#FEF2F2" if is_high else "#FFFBEB"
                badge_label = "HIGH" if is_high else "MEDIUM"
                title = ins.get("title", "")
                desc = ins.get("description", "")
                rec = ins.get("recommendation", "")

                rows += (
                    f'<div class="insight-item">'
                    f'<div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.25rem;">'
                    f'<span class="insight-badge" style="background:{badge_bg};color:{badge_color};">'
                    f'{badge_label}</span>'
                    f'<span class="insight-title">{title}</span>'
                    f'</div>'
                    f'<p class="insight-desc">{desc}</p>'
                    f'{f"<p class=\"insight-recommendation\">💡 {rec}</p>" if rec else ""}'
                    f'</div>'
                )

            st.markdown(
                f"""
            <div class="card" style="margin-bottom:1.5rem;">
                <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem;">
                    <span style="font-size:1rem;">🧠</span>
                    <span class="card-title" style="margin:0;">Executive Insights</span>
                </div>
                {rows}
            </div>
            """,
                unsafe_allow_html=True,
            )
        except Exception as e:
            st.error(f"Failed to render InsightCard: {e}")
