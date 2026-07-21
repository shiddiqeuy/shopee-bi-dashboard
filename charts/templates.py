"""
Chart templates — reusable chart configuration presets.

Each template controls colors, sizing, fonts, and layout.
"""

from __future__ import annotations

from typing import Any

from config.config import THEME

# Default chart dimensions
CHART_WIDTH = 580
CHART_HEIGHT = 380
CHART_SMALL_WIDTH = 420
CHART_SMALL_HEIGHT = 300


def line_chart_config(title: str) -> dict[str, Any]:
    return {
        "title": title,
        "title_font": {"color": THEME["secondary"], "size": 11, "bold": True},
        "legend_font": {"size": 9},
        "line": {"width": 2.5},
        "marker": {"size": 6},
        "y_axis": {"major_gridlines": {"visible": True, "line": {"color": "#E8E8E8"}}},
        "x_axis": {"major_gridlines": {"visible": False}},
        "chartarea": {"border": {"none": True}},
        "plotarea": {"border": {"none": True}},
    }


def bar_chart_config(title: str) -> dict[str, Any]:
    return {
        "title": title,
        "title_font": {"color": THEME["secondary"], "size": 11, "bold": True},
        "legend_font": {"size": 9},
        "y_axis": {"major_gridlines": {"visible": True, "line": {"color": "#E8E8E8"}}},
        "x_axis": {"major_gridlines": {"visible": False}},
        "chartarea": {"border": {"none": True}},
        "plotarea": {"border": {"none": True}},
    }


def pie_chart_config(title: str) -> dict[str, Any]:
    return {
        "title": title,
        "title_font": {"color": THEME["secondary"], "size": 11, "bold": True},
        "legend_font": {"size": 9},
        "chartarea": {"border": {"none": True}},
        "plotarea": {"border": {"none": True}},
        "data_labels": {
            "percentage": True,
            "separator": "\n",
            "font": {"size": 9},
        },
    }


def donut_chart_config(title: str) -> dict[str, Any]:
    return {
        "title": title,
        "title_font": {"color": THEME["secondary"], "size": 11, "bold": True},
        "legend_font": {"size": 8},
        "chartarea": {"border": {"none": True}},
        "plotarea": {"border": {"none": True}},
        "data_labels": {"percentage": True, "font": {"size": 9}},
    }
