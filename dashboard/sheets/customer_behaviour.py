"""
Customer Behaviour sheet — segmentation, RFM, top customers, and loyalty.
"""

from __future__ import annotations

from typing import Any

from charts.excel_charts import ExcelChartBuilder
from core.interfaces import SheetWriter
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class CustomerBehaviourSheet(SheetWriter):
    """Customer analytics — segments, top customers, repeat behaviour."""

    @property
    def sheet_name(self) -> str:
        return "Customer Behaviour"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        charts = ExcelChartBuilder(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:G2", "Customer Behaviour", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:B", 20)
        sheet.set_column("C:D", 16)
        sheet.set_column("E:G", 18)

        customer = analytics.get("customer", {})

        row = 4
        kpis = [
            ("Total Customers", f"{customer.get('total_customers', 0):,}"),
            ("Repeat Customers", f"{customer.get('repeat_customers', 0):,}"),
            ("New Customers", f"{customer.get('new_customers', 0):,}"),
            ("Repeat Rate", f"{customer.get('repeat_rate', 0):.1f}%"),
            ("Avg CLV", f"Rp {customer.get('avg_clv', 0):,.0f}"),
            ("Avg Basket", f"Rp {customer.get('avg_basket', 0):,.0f}"),
        ]
        for i, (label, value) in enumerate(kpis):
            col = 1 + i
            sheet.write(row, col, label, styles.kpi_label)
            sheet.write(row + 1, col, value, styles.kpi_card)

        row = 8
        segments = customer.get("segments", [])
        if segments:
            sheet.write(row, 1, "Customer Segmentation", styles.section_header)
            sheet.write(row + 1, 1, "Segment", styles.table_header)
            sheet.write(row + 1, 2, "Count", styles.table_header)
            for i, seg in enumerate(segments):
                r = row + 2 + i
                sheet.write(r, 1, seg.get("segment"), styles.table_cell)
                sheet.write(r, 2, seg.get("count"), styles.table_cell_alt)

            seg_row = row + 2
            for i, seg in enumerate(segments):
                sheet.write(seg_row + i, 4, seg.get("segment"), styles.table_cell)
                sheet.write(seg_row + i, 5, seg.get("count"), styles.table_cell_alt)

            cat_ref = f"=E{seg_row + 1}:E{seg_row + len(segments)}"
            val_ref = f"=F{seg_row + 1}:F{seg_row + len(segments)}"
            chart = charts.customer_segmentation(sheet, cat_ref, val_ref)
            sheet.insert_chart(seg_row, 6, chart)

        top_customers = customer.get("top_customers", [])
        if top_customers:
            tc_row = row + 12
            sheet.write(tc_row, 1, "Top 10 Customers", styles.section_header)
            headers = ["Username", "Revenue", "Orders", "City"]
            for ci, h in enumerate(headers):
                sheet.write(tc_row + 1, 1 + ci, h, styles.table_header)
            for i, c in enumerate(top_customers[:10]):
                r = tc_row + 2 + i
                alt = i % 2 == 1
                sheet.write(r, 1, c.get("buyer_username"), styles.table_cell_alt if alt else styles.table_cell)
                rev = float(c.get("total_revenue", 0))
                sheet.write(r, 2, rev, styles.currency_cell if alt else styles.currency_cell_alt)
                sheet.write(r, 3, c.get("total_orders"), styles.table_cell_alt if alt else styles.table_cell)
                sheet.write(r, 4, c.get("city"), styles.table_cell_alt if alt else styles.table_cell)
