"""
Cancellation sheet — cancellation rate, by city, product, reason, and trend.
"""

from __future__ import annotations

from typing import Any

from core.interfaces import SheetWriter
from excel.conditional import add_data_bar
from excel.navigation import add_back_button
from excel.styles import DashboardStyles
from config.config import THEME


class CancellationSheet(SheetWriter):
    """Cancellation analytics and root cause breakdown."""

    @property
    def sheet_name(self) -> str:
        return "Cancellation"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:H2", "Cancellation Analytics", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:B", 14)
        sheet.set_column("C:D", 18)
        sheet.set_column("E:H", 22)

        cancel = analytics.get("cancellation", {})
        rate = cancel.get("cancellation_rate", 0)

        sheet.write(4, 1, "Cancellation Rate", styles.kpi_label)
        sheet.write(5, 1, f"{rate:.1f}%", styles.kpi_card)
        sheet.write(4, 3, "Cancelled Orders", styles.kpi_label)
        sheet.write(5, 3, f"{cancel.get('cancelled_orders', 0):,}", styles.kpi_card)
        sheet.write(4, 5, "Total Orders", styles.kpi_label)
        sheet.write(5, 5, f"{cancel.get('total_orders', 0):,}", styles.kpi_card)

        row = 8
        data_end = row
        prod_row = row

        by_reason = cancel.get("by_reason", [])
        if by_reason:
            sheet.write(row, 1, "Cancellation by Reason", styles.section_header)
            sheet.write(row + 1, 1, "Reason", styles.table_header)
            sheet.write(row + 1, 2, "Orders", styles.table_header)
            sheet.write(row + 1, 3, "Revenue Lost", styles.table_header)
            for i, r_item in enumerate(by_reason[:10]):
                r = row + 2 + i
                alt = i % 2 == 1
                sheet.write(r, 1, r_item.get("cancellation_reason"), styles.table_cell_alt if alt else styles.table_cell)
                sheet.write(r, 2, r_item.get("cancelled_orders"), styles.table_cell_alt if alt else styles.table_cell)
                sheet.write(r, 3, float(r_item.get("cancelled_revenue", 0)), styles.currency_cell if alt else styles.currency_cell_alt)

            data_end = row + 2 + len(by_reason[:10])
            add_data_bar(sheet, row + 2, data_end - 1, 2, THEME["negative"])

        by_product = cancel.get("by_product", [])
        if by_product:
            prod_row = max(row + 16, data_end + 2)
            sheet.write(prod_row, 1, "Top Cancelled Products", styles.section_header)
            sheet.write(prod_row + 1, 1, "Product", styles.table_header)
            sheet.write(prod_row + 1, 2, "Cancelled Orders", styles.table_header)
            sheet.write(prod_row + 1, 3, "Revenue Lost", styles.table_header)
            for i, p in enumerate(by_product[:10]):
                r = prod_row + 2 + i
                alt = i % 2 == 1
                sheet.write(r, 1, p.get("product_name"), styles.table_cell_alt if alt else styles.table_cell)
                sheet.write(r, 2, p.get("cancelled_orders"), styles.table_cell_alt if alt else styles.table_cell)
                sheet.write(r, 3, float(p.get("cancelled_revenue", 0)), styles.currency_cell if alt else styles.currency_cell_alt)

        by_city = cancel.get("by_city", [])
        if by_city:
            city_row = max(prod_row + 16, data_end + 18)
            sheet.write(city_row, 1, "Cancellation by City", styles.section_header)
            sheet.write(city_row + 1, 1, "City", styles.table_header)
            sheet.write(city_row + 1, 2, "Province", styles.table_header)
            sheet.write(city_row + 1, 3, "Cancelled Orders", styles.table_header)
            for i, c in enumerate(by_city[:10]):
                r = city_row + 2 + i
                alt = i % 2 == 1
                sheet.write(r, 1, c.get("city"), styles.table_cell_alt if alt else styles.table_cell)
                sheet.write(r, 2, c.get("province"), styles.table_cell_alt if alt else styles.table_cell)
                sheet.write(r, 3, c.get("cancelled_orders"), styles.table_cell_alt if alt else styles.table_cell)
