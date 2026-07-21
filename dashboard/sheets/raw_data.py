"""
Raw Data sheet — exports the canonical orders table for reference.
"""

from __future__ import annotations

from typing import Any

from core.interfaces import SheetWriter
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class RawDataSheet(SheetWriter):
    """Raw orders data for reference and external analysis."""

    @property
    def sheet_name(self) -> str:
        return "Raw Data"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:H2", "Raw Orders Data", styles.title)
        sheet.set_column("A:A", 4)

        raw = analytics.get("raw_data", [])
        if not raw:
            sheet.write(4, 1, "No raw data available. Run ETL first.", styles.table_cell)
            return

        columns = list(raw[0].keys()) if raw else []
        if not columns:
            sheet.write(4, 1, "Empty raw data.", styles.table_cell)
            return

        col_widths = {
            "order_id": 20,
            "product_name": 30,
            "buyer_username": 18,
            "city": 18,
            "province": 18,
            "total_amount": 16,
            "order_date": 14,
        }

        for ci, col in enumerate(columns):
            width = col_widths.get(col, 14)
            col_idx = 1 + ci
            if col_idx <= 26:
                sheet.set_column(col_idx, col_idx, width)
            sheet.write(4, col_idx, col, styles.table_header)

        row = 5
        MAX_ROWS = 1000
        for ri, record in enumerate(raw[:MAX_ROWS]):
            alt = ri % 2 == 1
            for ci, col in enumerate(columns):
                val = record.get(col, "")
                if col in ("total_amount", "shipping_cost", "price"):
                    try:
                        val = float(val) if val else 0
                        sheet.write(
                            row, 1 + ci, val,
                            styles.currency_cell_alt if alt else styles.currency_cell,
                        )
                    except (ValueError, TypeError):
                        sheet.write(
                            row, 1 + ci, val,
                            styles.table_cell_alt if alt else styles.table_cell,
                        )
                else:
                    sheet.write(
                        row, 1 + ci, str(val),
                        styles.table_cell_alt if alt else styles.table_cell,
                    )
            row += 1

        total_row = row
        sheet.write(total_row, 1, f"Showing {min(len(raw), MAX_ROWS)} of {len(raw)} rows", styles.subtitle)
        sheet.freeze_panes(5, 1)
