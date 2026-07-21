"""
Product Performance sheet — product ranking, ABC, Pareto, and affinity.
"""

from __future__ import annotations

from typing import Any

from charts.excel_charts import ExcelChartBuilder
from core.interfaces import SheetWriter
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class ProductPerformanceSheet(SheetWriter):
    """Product-level analytics with full performance metrics."""

    @property
    def sheet_name(self) -> str:
        return "Product Performance"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        charts = ExcelChartBuilder(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:H2", "Product Performance", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:B", 30)
        sheet.set_column("C:F", 16)
        sheet.set_column("G:H", 14)

        products = analytics.get("product", {}).get("products", [])
        abc = analytics.get("product", {}).get("abc", [])
        affinity = analytics.get("product", {}).get("affinity", [])

        row = 4
        if products:
            headers = ["Product", "Revenue", "Orders", "Quantity", "Revenue %", "Cumulative %"]
            for ci, h in enumerate(headers):
                sheet.write(row, 1 + ci, h, styles.table_header)

            for ri, p in enumerate(products[:30]):
                r = row + 1 + ri
                alt = ri % 2 == 1
                sheet.write(r, 1, p.get("product_name"), styles.table_cell_alt if alt else styles.table_cell)
                rev = float(p.get("total_revenue", 0))
                sheet.write(r, 2, rev, styles.currency_cell if alt else styles.currency_cell_alt)
                sheet.write(r, 3, p.get("order_count"), styles.table_cell_alt if alt else styles.table_cell)
                sheet.write(r, 4, p.get("total_quantity"), styles.table_cell_alt if alt else styles.table_cell)
                sheet.write(r, 5, p.get("revenue_pct", 0) / 100, styles.pct_cell if alt else styles.pct_cell_alt)
                sheet.write(r, 6, p.get("cumulative_pct", 0) / 100, styles.pct_cell if alt else styles.pct_cell_alt)

            data_end = row + 1 + len(products[:30])
            chart_row = data_end + 1

            top10 = products[:10]
            for i, p in enumerate(top10):
                sheet.write(chart_row + i, 1, p.get("product_name"), styles.table_cell)
                sheet.write(chart_row + i, 2, float(p.get("total_revenue", 0)), styles.currency_cell)

            cat_ref = f"=B{chart_row + 1}:B{chart_row + len(top10)}"
            val_ref = f"=C{chart_row + 1}:C{chart_row + len(top10)}"
            chart = charts.top_product(sheet, cat_ref, val_ref)
            sheet.insert_chart(chart_row, 3, chart)
        else:
            sheet.write(row + 1, 1, "No product data available", styles.table_cell)

        if abc:
            abc_row = row + 24
            sheet.write(abc_row, 1, "ABC Classification", styles.section_header)
            sheet.write(abc_row + 1, 1, "Class", styles.table_header)
            sheet.write(abc_row + 1, 2, "Count", styles.table_header)
            sheet.write(abc_row + 1, 3, "Revenue", styles.table_header)
            for i, a in enumerate(abc):
                r = abc_row + 2 + i
                sheet.write(r, 1, a.get("classification"), styles.table_cell)
                sheet.write(r, 2, a.get("count"), styles.table_cell_alt)
                sheet.write(r, 3, float(a.get("revenue", 0)), styles.currency_cell)

        if affinity:
            aff_row = row + 30
            sheet.write(aff_row, 1, "Cross-Selling Affinity", styles.section_header)
            sheet.write(aff_row + 1, 1, "Product A", styles.table_header)
            sheet.write(aff_row + 1, 2, "Product B", styles.table_header)
            sheet.write(aff_row + 1, 3, "Co-occurrence", styles.table_header)
            for i, a in enumerate(affinity[:15]):
                r = aff_row + 2 + i
                alt = i % 2 == 1
                sheet.write(r, 1, a.get("product_a"), styles.table_cell_alt if alt else styles.table_cell)
                sheet.write(r, 2, a.get("product_b"), styles.table_cell_alt if alt else styles.table_cell)
                sheet.write(r, 3, a.get("co_occurrence"), styles.table_cell_alt if alt else styles.table_cell)
