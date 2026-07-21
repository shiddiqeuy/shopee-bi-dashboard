"""
XlsxWriter engine — central workbook factory.

Creates the workbook, applies global settings, and returns
the workbook handle for downstream sheet writers.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import xlsxwriter

from config.config import DASHBOARD_OUTPUT, THEME
from excel.navigation import write_navigation_sheet
from excel.styles import DashboardStyles
from utils.logger import get_logger

log = get_logger(__name__)


class DashboardWorkbook:
    """Manages the XlsxWriter workbook lifecycle."""

    def __init__(self, output_path: str | Path | None = None) -> None:
        self.path = Path(output_path) if output_path else DASHBOARD_OUTPUT
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.workbook: Any = None
        self.styles: DashboardStyles | None = None

    def __enter__(self) -> "DashboardWorkbook":
        log.info("Creating workbook: %s", self.path)
        self.workbook = xlsxwriter.Workbook(
            str(self.path),
            {
                "strings_to_numbers": False,
                "default_format_properties": {
                    "font_name": "Calibri",
                    "font_size": 10,
                },
            },
        )
        self.styles = DashboardStyles(self.workbook)
        write_navigation_sheet(self.workbook, self.styles)
        return self

    def __exit__(self, *args: Any) -> None:
        if self.workbook:
            self.workbook.close()
            log.info("Workbook saved: %s", self.path)

    def add_sheet(self, name: str) -> Any:
        """Add a worksheet with standard settings."""
        sheet = self.workbook.add_worksheet(name)
        sheet.hide_gridlines()
        sheet.set_landscape()
        sheet.set_paper(9)  # A4
        sheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
        return sheet

    def write_table(
        self,
        sheet: Any,
        data: list[dict[str, Any]],
        columns: list[tuple[str, str]],
        start_row: int = 2,
        start_col: int = 0,
        alt_rows: bool = True,
    ) -> int:
        """Write a list of dicts as a formatted table.

        Parameters
        ----------
        columns:
            List of (key, header_label) tuples.
        """
        if not data or not columns:
            return start_row

        styles = self.styles
        if not styles:
            msg = "DashboardStyles not initialized; use 'with' block"
            raise RuntimeError(msg)

        header_keys = [c[0] for c in columns]

        for ci, (_, label) in enumerate(columns):
            sheet.write(start_row, start_col + ci, label, styles.table_header)

        for ri, row in enumerate(data):
            row_style = styles.table_cell_alt if (alt_rows and ri % 2 == 1) else styles.table_cell
            for ci, key in enumerate(header_keys):
                val = row.get(key, "")
                sheet.write(start_row + 1 + ri, start_col + ci, val, row_style)

        end_row = start_row + len(data)
        return end_row

    def auto_width(self, sheet: Any, data: list[dict[str, Any]], columns: list[str]) -> None:
        """Automatically set column widths based on content."""
        for ci, col in enumerate(columns):
            max_len = len(col) + 2
            for row in data:
                val = str(row.get(col, ""))
                max_len = max(max_len, min(len(val) + 4, 50))
            sheet.set_column(ci, ci, max_len)
