"""
Shipping sheet — courier performance, method preference, costs.
"""

from __future__ import annotations

from typing import Any

from charts.excel_charts import ExcelChartBuilder
from core.interfaces import SheetWriter
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class ShippingSheet(SheetWriter):
    """Shipping provider and courier analytics."""

    @property
    def sheet_name(self) -> str:
        return "Shipping"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        charts = ExcelChartBuilder(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:F2", "Shipping Analytics", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:B", 20)
        sheet.set_column("C:F", 18)

        providers = analytics.get("shipping", {}).get("providers", [])
        if not providers:
            sheet.write(4, 1, "No shipping data available", styles.table_cell)
            return

        headers = ["Provider", "Method", "Orders", "Total Cost", "Avg Cost"]
        for ci, h in enumerate(headers):
            sheet.write(4, 1 + ci, h, styles.table_header)

        for ri, p in enumerate(providers):
            r = 5 + ri
            alt = ri % 2 == 1
            sheet.write(r, 1, p.get("shipping_provider"), styles.table_cell_alt if alt else styles.table_cell)
            sheet.write(r, 2, p.get("shipping_method", ""), styles.table_cell_alt if alt else styles.table_cell)
            sheet.write(r, 3, p.get("order_count"), styles.table_cell_alt if alt else styles.table_cell)
            sheet.write(r, 4, float(p.get("total_cost", 0)), styles.currency_cell if alt else styles.currency_cell_alt)
            sheet.write(r, 5, float(p.get("avg_cost", 0)), styles.currency_cell if alt else styles.currency_cell_alt)

        data_end = 5 + len(providers)
        chart_row = data_end + 2

        top_providers = sorted(providers, key=lambda p: p.get("order_count", 0), reverse=True)[:8]
        for i, p in enumerate(top_providers):
            sheet.write(chart_row + i, 1, p.get("shipping_provider"), styles.table_cell)
            sheet.write(chart_row + i, 2, p.get("order_count"), styles.table_cell_alt)

        if top_providers:
            cat_ref = f"=B{chart_row + 1}:B{chart_row + len(top_providers)}"
            val_ref = f"=C{chart_row + 1}:C{chart_row + len(top_providers)}"
            chart = charts.shipping_chart(sheet, cat_ref, val_ref)
            sheet.insert_chart(chart_row, 3, chart)
