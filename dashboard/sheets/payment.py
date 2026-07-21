"""
Payment sheet — payment method distribution, revenue, and regional preference.
"""

from __future__ import annotations

from typing import Any

from charts.excel_charts import ExcelChartBuilder
from core.interfaces import SheetWriter
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class PaymentSheet(SheetWriter):
    """Payment method analytics and regional preference."""

    @property
    def sheet_name(self) -> str:
        return "Payment"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        charts = ExcelChartBuilder(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:G2", "Payment Analytics", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:B", 20)
        sheet.set_column("C:F", 18)
        sheet.set_column("G:G", 18)

        methods = analytics.get("payment", {}).get("methods", [])
        if not methods:
            sheet.write(4, 1, "No payment data available", styles.table_cell)
            return

        headers = ["Method", "Orders", "Customers", "Revenue", "Avg Transaction", "Share"]
        for ci, h in enumerate(headers):
            sheet.write(4, 1 + ci, h, styles.table_header)

        for ri, m in enumerate(methods):
            r = 5 + ri
            alt = ri % 2 == 1
            sheet.write(r, 1, m.get("payment_method"), styles.table_cell_alt if alt else styles.table_cell)
            sheet.write(r, 2, m.get("order_count"), styles.table_cell_alt if alt else styles.table_cell)
            sheet.write(r, 3, m.get("customer_count"), styles.table_cell_alt if alt else styles.table_cell)
            rev = float(m.get("revenue", 0))
            sheet.write(r, 4, rev, styles.currency_cell if alt else styles.currency_cell_alt)
            sheet.write(r, 5, float(m.get("avg_transaction", 0)), styles.currency_cell if alt else styles.currency_cell_alt)
            share = m.get("share_pct", 0)
            sheet.write(r, 6, share / 100, styles.pct_cell if alt else styles.pct_cell_alt)

        data_end = 5 + len(methods)

        if methods:
            chart_row = data_end + 2
            for i, m in enumerate(methods):
                sheet.write(chart_row + i, 1, m.get("payment_method"), styles.table_cell)
                sheet.write(chart_row + i, 2, float(m.get("revenue", 0)), styles.currency_cell)

            cat_ref = f"=B{chart_row + 1}:B{chart_row + len(methods)}"
            val_ref = f"=C{chart_row + 1}:C{chart_row + len(methods)}"
            chart = charts.payment_chart(sheet, cat_ref, val_ref)
            sheet.insert_chart(chart_row, 3, chart)
