"""
City Performance sheet — detailed city-level analytics table and charts.
"""

from __future__ import annotations

from typing import Any

from charts.excel_charts import ExcelChartBuilder
from config.config import THEME
from core.interfaces import SheetWriter
from excel.conditional import add_data_bar
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class CityPerformanceSheet(SheetWriter):
    """City-level performance with ranking, contribution, and growth metrics."""

    @property
    def sheet_name(self) -> str:
        return "City Performance"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        charts = ExcelChartBuilder(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:H2", "City Performance", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:B", 22)
        sheet.set_column("C:E", 18)
        sheet.set_column("F:F", 14)
        sheet.set_column("G:G", 14)
        sheet.set_column("H:H", 18)

        cities = analytics.get("city", {}).get("cities", [])
        if not cities:
            sheet.write(4, 1, "No city data available", styles.table_cell)
            return

        sorted_cities = sorted(cities, key=lambda c: c.get("revenue", 0), reverse=True)

        headers = ["City", "Revenue", "Orders", "Customers", "Repeat Rate", "Growth", "Top Product"]
        for ci, h in enumerate(headers):
            col = 1 + ci
            sheet.write(4, col if col <= 7 else col, h, styles.table_header)

        for ri, c in enumerate(sorted_cities[:50]):
            r = 5 + ri
            alt = ri % 2 == 1
            sheet.write(r, 1, c.get("city_name"), styles.table_cell_alt if alt else styles.table_cell)
            sheet.write(r, 2, float(c.get("revenue", 0)), styles.currency_cell if alt else styles.currency_cell_alt)
            sheet.write(r, 3, c.get("order_count"), styles.table_cell_alt if alt else styles.table_cell)
            sheet.write(r, 4, c.get("customer_count"), styles.table_cell_alt if alt else styles.table_cell)
            repeat = c.get("repeat_rate", 0)
            sheet.write(r, 5, repeat / 100 if repeat else 0, styles.pct_cell if alt else styles.pct_cell_alt)
            growth = c.get("growth_pct", 0)
            sheet.write(r, 6, growth / 100, styles.pct_cell if alt else styles.pct_cell_alt)
            top_3 = c.get("top_products", [])
            top_name = top_3[0] if top_3 else ""
            sheet.write(r, 7, top_name, styles.table_cell_alt if alt else styles.table_cell)

        data_end = 5 + len(sorted_cities[:50])
        add_data_bar(sheet, 5, data_end - 1, 2, THEME["primary"])

        if sorted_cities:
            chart_row = data_end + 2
            top10 = sorted_cities[:10]
            for i, c in enumerate(top10):
                sheet.write(chart_row + i, 1, c.get("city_name"), styles.table_cell)
                sheet.write(chart_row + i, 2, float(c.get("revenue", 0)), styles.currency_cell)

            cat_ref = f"=B{chart_row + 1}:B{chart_row + len(top10)}"
            val_ref = f"=C{chart_row + 1}:C{chart_row + len(top10)}"
            chart = charts.top_city(sheet, cat_ref, val_ref)
            sheet.insert_chart(chart_row, 3, chart)
