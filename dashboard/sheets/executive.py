"""
Executive Dashboard sheet — top-level KPIs and summary charts.
"""

from __future__ import annotations

from typing import Any

from charts.excel_charts import ExcelChartBuilder
from core.interfaces import SheetWriter
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class ExecutiveSheet(SheetWriter):
    """Executive dashboard — first glance KPIs and trend chart."""

    @property
    def sheet_name(self) -> str:
        return "Executive Dashboard"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        charts = ExcelChartBuilder(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:H2", "Executive Dashboard", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:H", 16)

        customer = analytics.get("customer", {})
        product = analytics.get("product", {})
        cancellation = analytics.get("cancellation", {})

        row = 4
        kpis = [
            ("Total Revenue", f"Rp {customer.get('total_revenue', 0):,.0f}", styles.kpi_currency),
            ("Total Customers", f"{customer.get('total_customers', 0):,}", styles.kpi_card),
            ("Repeat Rate", f"{customer.get('repeat_rate', 0):.1f}%", styles.kpi_card),
            ("Total Products", f"{product.get('total_products', 0):,}", styles.kpi_card),
            ("Cancellation Rate", f"{cancellation.get('cancellation_rate', 0):.1f}%", styles.kpi_card),
        ]
        for i, (label, value, fmt) in enumerate(kpis):
            col = 1 + i * 1
            sheet.write(row, col, label, styles.kpi_label)
            sheet.write(row + 1, col, value, fmt)

        trend = analytics.get("trend", {})
        months = trend.get("months", [])
        if months:
            header_row = row + 4
            sheet.write(header_row, 1, "Monthly Revenue Trend", styles.section_header)
            data_start = header_row + 1
            for i, m in enumerate(months):
                sheet.write(data_start + i, 1, m.get("month", ""), styles.table_cell)
                rev = m.get("revenue", 0)
                sheet.write(data_start + i, 2, float(rev), styles.currency_cell)

            n = len(months)
            cat_ref = f"=B{data_start + 1}:B{data_start + n}"
            val_ref = f"=C{data_start + 1}:C{data_start + n}"
            chart = charts.revenue_trend(sheet, cat_ref, val_ref)
            sheet.insert_chart(data_start, 4, chart)
