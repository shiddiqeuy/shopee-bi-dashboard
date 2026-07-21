"""
Monthly Trend sheet — revenue, orders, customers, MoM growth, running total.
"""

from __future__ import annotations

from typing import Any

from charts.excel_charts import ExcelChartBuilder
from core.interfaces import SheetWriter
from excel.conditional import add_data_bar, add_highlight_negative
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class MonthlyTrendSheet(SheetWriter):
    """Monthly time-series performance with growth calculations."""

    @property
    def sheet_name(self) -> str:
        return "Monthly Trend"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        charts = ExcelChartBuilder(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:I2", "Monthly Trend", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:B", 12)
        sheet.set_column("C:H", 16)
        sheet.set_column("I:I", 16)

        months = analytics.get("trend", {}).get("months", [])
        if not months:
            sheet.write(4, 1, "No trend data available", styles.table_cell)
            return

        headers = ["Month", "Revenue", "Orders", "Customers", "MoM Rev %",
                    "MoM Ord %", "Running Revenue", "MA 3 Revenue"]
        for ci, h in enumerate(headers):
            sheet.write(4, 1 + ci, h, styles.table_header)

        for ri, m in enumerate(months):
            r = 5 + ri
            alt = ri % 2 == 1
            sheet.write(r, 1, m.get("month"), styles.table_cell_alt if alt else styles.table_cell)
            sheet.write(r, 2, float(m.get("revenue", 0)), styles.currency_cell if alt else styles.currency_cell_alt)
            sheet.write(r, 3, m.get("order_count"), styles.table_cell_alt if alt else styles.table_cell)
            sheet.write(r, 4, m.get("customer_count"), styles.table_cell_alt if alt else styles.table_cell)
            rev_mom = m.get("revenue_mom_pct", 0)
            sheet.write(r, 5, rev_mom / 100, styles.pct_cell if alt else styles.pct_cell_alt)
            ord_mom = m.get("orders_mom_pct", 0)
            sheet.write(r, 6, ord_mom / 100, styles.pct_cell if alt else styles.pct_cell_alt)
            sheet.write(r, 7, float(m.get("running_total_revenue", 0)), styles.currency_cell if alt else styles.currency_cell_alt)
            ma = m.get("ma_3_revenue", 0)
            sheet.write(r, 8, float(ma or 0), styles.currency_cell if alt else styles.currency_cell_alt)

        data_end = 5 + len(months)
        add_highlight_negative(sheet, workbook, 5, data_end - 1, 5)

        chart_row = data_end + 2
        for i, m in enumerate(months):
            sheet.write(chart_row + i, 1, m.get("month"), styles.table_cell)
            sheet.write(chart_row + i, 2, float(m.get("revenue", 0)), styles.currency_cell)

        cat_ref = f"=B{chart_row + 1}:B{chart_row + len(months)}"
        val_ref = f"=C{chart_row + 1}:C{chart_row + len(months)}"
        chart = charts.revenue_trend(sheet, cat_ref, val_ref)
        sheet.insert_chart(chart_row, 3, chart)

        chart_row2 = chart_row + 18
        for i, m in enumerate(months):
            sheet.write(chart_row2 + i, 1, m.get("month"), styles.table_cell)
            sheet.write(chart_row2 + i, 2, m.get("order_count"), styles.table_cell_alt)

        cat_ref2 = f"=B{chart_row2 + 1}:B{chart_row2 + len(months)}"
        val_ref2 = f"=C{chart_row2 + 1}:C{chart_row2 + len(months)}"
        chart2 = charts.monthly_orders(sheet, cat_ref2, val_ref2)
        sheet.insert_chart(chart_row2, 3, chart2)
