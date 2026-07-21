"""
Province Performance sheet — province-level analytics table and chart.
"""

from __future__ import annotations

from typing import Any

from charts.excel_charts import ExcelChartBuilder
from core.interfaces import SheetWriter
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class ProvincePerformanceSheet(SheetWriter):
    """Province-level ranking with revenue, customers, and contribution."""

    @property
    def sheet_name(self) -> str:
        return "Province Performance"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        charts = ExcelChartBuilder(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:F2", "Province Performance", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:B", 22)
        sheet.set_column("C:E", 18)
        sheet.set_column("F:F", 14)

        provinces = analytics.get("province", {}).get("provinces", [])
        if not provinces:
            sheet.write(4, 1, "No province data available", styles.table_cell)
            return

        sorted_provinces = sorted(provinces, key=lambda p: p.get("revenue", 0), reverse=True)

        headers = ["Province", "Revenue", "Orders", "Customers", "Contribution"]
        for ci, h in enumerate(headers):
            sheet.write(4, 1 + ci, h, styles.table_header)

        for ri, p in enumerate(sorted_provinces[:30]):
            r = 5 + ri
            alt = ri % 2 == 1
            sheet.write(r, 1, p.get("province"), styles.table_cell_alt if alt else styles.table_cell)
            sheet.write(r, 2, float(p.get("revenue", 0)), styles.currency_cell if alt else styles.currency_cell_alt)
            sheet.write(r, 3, p.get("order_count"), styles.table_cell_alt if alt else styles.table_cell)
            sheet.write(r, 4, p.get("customer_count"), styles.table_cell_alt if alt else styles.table_cell)
            cont = p.get("contribution_pct", 0)
            sheet.write(r, 5, cont / 100, styles.pct_cell if alt else styles.pct_cell_alt)

        data_end = 5 + len(sorted_provinces[:30])
        top10 = sorted_provinces[:10]
        chart_row = data_end + 2
        for i, p in enumerate(top10):
            sheet.write(chart_row + i, 1, p.get("province"), styles.table_cell)
            sheet.write(chart_row + i, 2, float(p.get("revenue", 0)), styles.currency_cell)

        cat_ref = f"=B{chart_row + 1}:B{chart_row + len(top10)}"
        val_ref = f"=C{chart_row + 1}:C{chart_row + len(top10)}"
        chart = charts.top_province(sheet, cat_ref, val_ref)
        sheet.insert_chart(chart_row, 3, chart)
