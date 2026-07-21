"""
Named XlsxWriter styles for the professional dashboard theme.

All styles derive from the THEME dict in config.
"""

from __future__ import annotations

from typing import Any

from config.config import THEME


class DashboardStyles:
    """Factory for named XlsxWriter format dicts."""

    def __init__(self, workbook: Any) -> None:
        self.wb = workbook
        self._cache: dict[str, Any] = {}

    def _fmt(self, **kwargs: Any) -> Any:
        """Create or retrieve a cached format."""
        key = str(sorted(kwargs.items()))
        if key not in self._cache:
            self._cache[key] = self.wb.add_format(kwargs)
        return self._cache[key]

    @property
    def title(self) -> Any:
        return self._fmt(
            bold=True,
            font_size=18,
            font_color=THEME["primary"],
            bottom=2,
            bottom_color=THEME["primary"],
        )

    @property
    def subtitle(self) -> Any:
        return self._fmt(
            font_size=11,
            font_color="#666666",
        )

    @property
    def kpi_card(self) -> Any:
        return self._fmt(
            bold=True,
            font_size=24,
            font_color=THEME["primary"],
            num_format="#,##0",
        )

    @property
    def kpi_label(self) -> Any:
        return self._fmt(
            font_size=10,
            font_color="#888888",
        )

    @property
    def kpi_currency(self) -> Any:
        return self._fmt(
            bold=True,
            font_size=24,
            font_color=THEME["primary"],
            num_format='Rp #,##0',
        )

    @property
    def table_header(self) -> Any:
        return self._fmt(
            bold=True,
            font_size=10,
            font_color=THEME["table_header_fg"],
            bg_color=THEME["table_header_bg"],
            border=1,
            border_color="#CCCCCC",
            text_wrap=True,
            valign="vcenter",
        )

    @property
    def table_cell(self) -> Any:
        return self._fmt(
            font_size=10,
            border=1,
            border_color="#E0E0E0",
        )

    @property
    def table_cell_alt(self) -> Any:
        return self._fmt(
            font_size=10,
            border=1,
            border_color="#E0E0E0",
            bg_color=THEME["table_alt_row"],
        )

    @property
    def currency_cell(self) -> Any:
        return self._fmt(
            font_size=10,
            num_format='Rp #,##0',
            border=1,
            border_color="#E0E0E0",
        )

    @property
    def currency_cell_alt(self) -> Any:
        return self._fmt(
            font_size=10,
            num_format='Rp #,##0',
            border=1,
            border_color="#E0E0E0",
            bg_color=THEME["table_alt_row"],
        )

    @property
    def pct_cell(self) -> Any:
        return self._fmt(
            font_size=10,
            num_format="0.00%",
            border=1,
            border_color="#E0E0E0",
        )

    @property
    def pct_cell_alt(self) -> Any:
        return self._fmt(
            font_size=10,
            num_format="0.00%",
            border=1,
            border_color="#E0E0E0",
            bg_color=THEME["table_alt_row"],
        )

    @property
    def section_header(self) -> Any:
        return self._fmt(
            bold=True,
            font_size=12,
            font_color=THEME["secondary"],
            bottom=1,
            bottom_color=THEME["secondary"],
        )

    @property
    def nav_button(self) -> Any:
        return self._fmt(
            font_size=10,
            font_color=THEME["primary"],
            underline=True,
        )

    @property
    def positive(self) -> Any:
        return self._fmt(
            font_size=10,
            font_color=THEME["positive"],
            num_format="0.00%",
        )

    @property
    def negative(self) -> Any:
        return self._fmt(
            font_size=10,
            font_color=THEME["negative"],
            num_format="0.00%",
        )

    @property
    def warning_fill(self) -> Any:
        return self._fmt(
            bg_color="#FFF3E0",
            font_size=10,
        )

    @property
    def insight_title(self) -> Any:
        return self._fmt(
            bold=True,
            font_size=11,
            font_color=THEME["secondary"],
        )

    @property
    def insight_body(self) -> Any:
        return self._fmt(
            font_size=10,
            text_wrap=True,
            valign="vtop",
        )

    @property
    def methodology_body(self) -> Any:
        return self._fmt(
            font_size=10,
            text_wrap=True,
        )
