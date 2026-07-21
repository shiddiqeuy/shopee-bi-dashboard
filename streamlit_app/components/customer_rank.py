"""CustomerRankCard — ranking card list for top customers."""

from __future__ import annotations

from typing import Any

import polars as pl
import streamlit as st

from streamlit_app.components.section_title import SectionTitle


class CustomerRankCard:
    """Renders a list of top customers as visual ranking cards.

    Usage:
        CustomerRankCard(df=pl.DataFrame(...), title="Top Customers").render()
    """

    def __init__(self, df: pl.DataFrame, title: str = "Top Customers") -> None:
        self.df = df
        self.title = title

    @staticmethod
    def _format_rp(value: float) -> str:
        if value >= 1_000_000_000:
            return f"Rp{value/1_000_000_000:.2f} B"
        if value >= 1_000_000:
            return f"Rp{value/1_000_000:.2f} M"
        return f"Rp{value:,.0f}"

    def render(self) -> None:
        if self.df.is_empty():
            return

        SectionTitle(self.title, "Highest revenue customers with reorder activity").render()

        medals = ["🥇", "🥈", "🥉"]
        cards = ""
        for i, row in enumerate(self.df.iter_rows(named=True)):
            rank = i + 1
            badge = (
                medals[rank - 1]
                if rank <= 3
                else f'<span style="font-size:0.75rem;font-weight:600;color:var(--text-muted);">#{rank}</span>'
            )
            revenue = self._format_rp(row["total_revenue"])
            cards += f"""
            <div class="customer-rank-card">
                <div class="customer-rank-badge">{badge}</div>
                <div class="customer-rank-info">
                    <div class="customer-rank-name">{row['buyer_username']}</div>
                    <div class="customer-rank-meta">{row['total_orders']} orders · {row['reorder_products']} reorder products</div>
                </div>
                <div class="customer-rank-revenue">{revenue}</div>
            </div>
            """

        st.markdown(
            f"<div style='max-height:520px;overflow-y:auto;padding-right:4px;'>{cards}</div>",
            unsafe_allow_html=True,
        )
