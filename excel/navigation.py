"""
Dashboard navigation — creates a navigation sheet with hyperlinks
and adds "Back to Navigation" buttons on every sheet.
"""

from __future__ import annotations

from typing import Any

from config.constants import SheetName
from excel.styles import DashboardStyles


def write_navigation_sheet(
    workbook: Any,
    styles: DashboardStyles,
) -> None:
    """Write the first sheet as a navigation index."""
    sheet = workbook.add_worksheet("Navigation")
    sheet.hide_gridlines()

    sheet.set_column("A:A", 60)
    sheet.set_column("B:B", 30)

    sheet.merge_range("A1:B1", "Shopee BI Dashboard", styles.title)
    sheet.write("A2", "Click a section to navigate", styles.subtitle)

    sheets = [
        SheetName.EXECUTIVE,
        SheetName.KPI,
        SheetName.CITY,
        SheetName.PROVINCE,
        SheetName.PRODUCT,
        SheetName.CUSTOMER,
        SheetName.TREND,
        SheetName.SHIPPING,
        SheetName.PAYMENT,
        SheetName.CANCELLATION,
        SheetName.INSIGHT,
        SheetName.RAW,
        SheetName.METHODOLOGY,
    ]

    for i, name in enumerate(sheets, start=4):
        url = f"internal:{name}"
        sheet.write_url(i, 0, url, styles.nav_button, name)
        sheet.write(i, 1, f"→ Go to {name}", styles.table_cell)


def add_back_button(
    sheet: Any,
    styles: DashboardStyles,
    row: int = 0,
    col: int = 0,
) -> None:
    """Add a 'Back to Navigation' hyperlink on a sheet."""
    url = "internal:Navigation"
    sheet.write_url(row, col, url, styles.nav_button, "← Back to Navigation")
