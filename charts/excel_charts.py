"""
XlsxWriter chart builders — factory methods for each chart type.

Every chart returns a chart object ready to be inserted into a worksheet.
"""

from __future__ import annotations

from typing import Any, Optional

from charts.templates import (
    CHART_HEIGHT,
    CHART_SMALL_HEIGHT,
    CHART_SMALL_WIDTH,
    CHART_WIDTH,
    bar_chart_config,
    donut_chart_config,
    line_chart_config,
    pie_chart_config,
)
from config.config import THEME


class ExcelChartBuilder:
    """Builds XlsxWriter charts with consistent styling."""

    def __init__(self, workbook: Any) -> None:
        self.wb = workbook

    def revenue_trend(self, sheet: Any, categories: str, values: str) -> Any:
        chart = self.wb.add_chart({"type": "line"})
        chart.add_series({
            "name": "Revenue",
            "categories": categories,
            "values": values,
            "line": {"color": THEME["primary"], "width": 2.5},
            "marker": {"type": "circle", "size": 6, "fill": {"color": THEME["primary"]}},
        })
        chart.set_size({"width": CHART_WIDTH, "height": CHART_HEIGHT})
        chart.set_title({"name": "Monthly Revenue Trend"})
        chart.set_y_axis({"major_gridlines": {"visible": True, "line": {"color": "#E8E8E8"}}})
        chart.set_legend({"font": {"size": 9}})
        return chart

    def monthly_orders(self, sheet: Any, categories: str, values: str) -> Any:
        chart = self.wb.add_chart({"type": "column"})
        chart.add_series({
            "name": "Orders",
            "categories": categories,
            "values": values,
            "fill": {"color": THEME["accent"]},
        })
        chart.set_size({"width": CHART_WIDTH, "height": CHART_HEIGHT})
        chart.set_title({"name": "Monthly Orders"})
        chart.set_legend({"font": {"size": 9}})
        chart.set_y_axis({"major_gridlines": {"visible": True, "line": {"color": "#E8E8E8"}}})
        return chart

    def top_city(self, sheet: Any, categories: str, values: str) -> Any:
        chart = self.wb.add_chart({"type": "bar"})
        chart.add_series({
            "name": "Revenue",
            "categories": categories,
            "values": values,
            "fill": {"color": THEME["primary"]},
        })
        chart.set_size({"width": CHART_WIDTH, "height": CHART_SMALL_HEIGHT})
        chart.set_title({"name": "Top Cities by Revenue"})
        chart.set_legend({"font": {"size": 9}})
        chart.set_y_axis({"major_gridlines": {"visible": True, "line": {"color": "#E8E8E8"}}})
        return chart

    def top_province(self, sheet: Any, categories: str, values: str) -> Any:
        chart = self.wb.add_chart({"type": "bar"})
        chart.add_series({
            "name": "Revenue",
            "categories": categories,
            "values": values,
            "fill": {"color": THEME["secondary"]},
        })
        chart.set_size({"width": CHART_SMALL_WIDTH, "height": CHART_SMALL_HEIGHT})
        chart.set_title({"name": "Top Provinces"})
        chart.set_legend({"font": {"size": 9}})
        chart.set_y_axis({"major_gridlines": {"visible": True, "line": {"color": "#E8E8E8"}}})
        return chart

    def top_product(self, sheet: Any, categories: str, values: str) -> Any:
        chart = self.wb.add_chart({"type": "bar"})
        chart.add_series({
            "name": "Revenue",
            "categories": categories,
            "values": values,
            "fill": {"color": THEME["accent"]},
        })
        chart.set_size({"width": CHART_WIDTH, "height": CHART_HEIGHT})
        chart.set_title({"name": "Top Products by Revenue"})
        chart.set_legend({"font": {"size": 9}})
        chart.set_y_axis({"major_gridlines": {"visible": True, "line": {"color": "#E8E8E8"}}})
        return chart

    def pareto(self, sheet: Any, categories: str, values: str, cum_values: str) -> Any:
        chart = self.wb.add_chart({"type": "column"})
        chart.add_series({
            "name": "Revenue",
            "categories": categories,
            "values": values,
            "fill": {"color": THEME["primary"]},
        })
        line = chart.add_series({
            "name": "Cumulative %",
            "categories": categories,
            "values": cum_values,
            "line": {"color": THEME["negative"], "width": 2},
            "marker": {"type": "none"},
            "y2_axis": True,
        })
        chart.set_size({"width": CHART_WIDTH, "height": CHART_HEIGHT})
        chart.set_title({"name": "Pareto Analysis"})
        chart.set_legend({"font": {"size": 9}})
        chart.set_y_axis({"major_gridlines": {"visible": True, "line": {"color": "#E8E8E8"}}})
        chart.set_y2_axis({"major_gridlines": {"visible": False}})
        return chart

    def abc_classification(self, sheet: Any, categories: str, values: str) -> Any:
        chart = self.wb.add_chart({"type": "pie"})
        chart.add_series({
            "name": "ABC Classification",
            "categories": categories,
            "values": values,
            "data_labels": {
                "percentage": True,
                "category": True,
                "separator": "\n",
                "font": {"size": 9},
            },
        })
        chart.set_size({"width": CHART_SMALL_WIDTH, "height": CHART_SMALL_HEIGHT})
        chart.set_title({"name": "ABC Classification"})
        chart.set_legend({"font": {"size": 9}})
        return chart

    def customer_segmentation(self, sheet: Any, categories: str, values: str) -> Any:
        chart = self.wb.add_chart({"type": "doughnut"})
        chart.add_series({
            "name": "Customer Segments",
            "categories": categories,
            "values": values,
            "data_labels": {"percentage": True, "category": True, "font": {"size": 9}},
        })
        chart.set_size({"width": CHART_SMALL_WIDTH, "height": CHART_SMALL_HEIGHT})
        chart.set_title({"name": "Customer Segmentation"})
        chart.set_legend({"font": {"size": 8}})
        return chart

    def payment_chart(self, sheet: Any, categories: str, values: str) -> Any:
        chart = self.wb.add_chart({"type": "pie"})
        chart.add_series({
            "name": "Payment Methods",
            "categories": categories,
            "values": values,
            "data_labels": {"percentage": True, "category": True, "font": {"size": 9}},
        })
        chart.set_size({"width": CHART_SMALL_WIDTH, "height": CHART_SMALL_HEIGHT})
        chart.set_title({"name": "Payment Distribution"})
        chart.set_legend({"font": {"size": 9}})
        return chart

    def shipping_chart(self, sheet: Any, categories: str, values: str) -> Any:
        chart = self.wb.add_chart({"type": "column"})
        chart.add_series({
            "name": "Orders",
            "categories": categories,
            "values": values,
            "fill": {"color": THEME["primary"]},
        })
        chart.set_size({"width": CHART_SMALL_WIDTH, "height": CHART_SMALL_HEIGHT})
        chart.set_title({"name": "Shipping Provider Share"})
        chart.set_legend({"font": {"size": 9}})
        chart.set_y_axis({"major_gridlines": {"visible": True, "line": {"color": "#E8E8E8"}}})
        return chart
