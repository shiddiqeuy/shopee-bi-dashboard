"""
Hidden Insight sheet — automatically generated business recommendations.
"""

from __future__ import annotations

from typing import Any

from core.interfaces import SheetWriter
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class HiddenInsightSheet(SheetWriter):
    """AI-generated business insights and recommendations."""

    @property
    def sheet_name(self) -> str:
        return "Hidden Insight"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:F2", "Hidden Insights & Recommendations", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:B", 18)
        sheet.set_column("C:C", 55)
        sheet.set_column("D:D", 50)
        sheet.set_column("E:E", 14)

        insights = analytics.get("insights", [])
        if not insights:
            sheet.write(4, 1, "No insights generated. Run analytics with sufficient data.", styles.table_cell)
            return

        headers = ["Type", "Finding", "Recommendation", "Priority"]
        for ci, h in enumerate(headers):
            sheet.write(4, 1 + ci, h, styles.table_header)

        row = 5
        for i, ins in enumerate(insights):
            alt = i % 2 == 1
            ins_type = ins.get("type", "").replace("_", " ").title()
            priority = ins.get("priority", "medium").upper()

            fmt_type = styles.insight_title if not alt else styles.insight_title
            fmt_body = styles.insight_body
            fmt_body_alt = styles.insight_body

            sheet.write(row, 1, ins_type, fmt_type)
            sheet.write(row, 2, ins.get("description", ""), fmt_body if not alt else fmt_body_alt)
            sheet.write(row, 3, ins.get("recommendation", ""), fmt_body if not alt else fmt_body_alt)
            sheet.write(row, 4, priority, styles.insight_body)

            sheet.set_row(row, 40)
            row += 1

        for priority_filter in ["HIGH", "MEDIUM", "LOW"]:
            count = sum(
                1 for ins in insights
                if ins.get("priority", "medium").upper() == priority_filter
            )
            if count:
                p_row = row + 2
                sheet.write(p_row, 1, f"{priority_filter} Priority Insights", styles.section_header)
                sheet.write(p_row, 2, f"{count} insights", styles.table_cell)
                row = p_row + 2
