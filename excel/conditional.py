"""
Conditional formatting rules for the Excel dashboard.

Applies data bars, colour scales, and icon sets
to make the dashboard visually scannable.
"""

from __future__ import annotations

from typing import Any


def add_data_bar(
    sheet: Any,
    first_row: int,
    last_row: int,
    col: int,
    color: str = "#1B98F5",
) -> None:
    """Add a data bar conditional format to a range."""
    cell_range = f"{chr(65 + col)}{first_row + 1}:{chr(65 + col)}{last_row + 1}"
    sheet.conditional_format(
        cell_range,
        {
            "type": "data_bar",
            "bar_color": color,
            "bar_solid": True,
            "min_type": "min",
            "max_type": "max",
        },
    )


def add_color_scale(
    sheet: Any,
    first_row: int,
    last_row: int,
    col: int,
    min_color: str = "#FF6B6B",
    mid_color: str = "#FFB74D",
    max_color: str = "#00C9A7",
) -> None:
    """Add a 3-color scale conditional format."""
    cell_range = f"{chr(65 + col)}{first_row + 1}:{chr(65 + col)}{last_row + 1}"
    sheet.conditional_format(
        cell_range,
        {
            "type": "3_color_scale",
            "min_color": min_color,
            "mid_color": mid_color,
            "max_color": max_color,
        },
    )


def add_highlight_negative(
    sheet: Any,
    workbook: Any,
    first_row: int,
    last_row: int,
    col: int,
) -> None:
    """Highlight negative values in red."""
    cell_range = f"{chr(65 + col)}{first_row + 1}:{chr(65 + col)}{last_row + 1}"
    neg_format = workbook.add_format({"font_color": "#FF6B6B"})
    sheet.conditional_format(
        cell_range,
        {
            "type": "cell",
            "criteria": "<",
            "value": 0,
            "format": neg_format,
        },
    )
