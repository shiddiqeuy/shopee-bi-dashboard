"""
Dashboard builder — orchestrates the full Excel generation.

Collects all registered sheet writers, requests analytics data,
and sequentially writes every sheet.
"""

from __future__ import annotations

from typing import Any

from core.interfaces import DashboardBuilder, Repository, SheetWriter
from utils.logger import get_logger

log = get_logger(__name__)


class ExcelDashboardBuilder(DashboardBuilder):
    """Builds the complete Excel BI dashboard."""

    def __init__(self, repository: Repository) -> None:
        self.repo = repository
        self._sheets: dict[str, SheetWriter] = {}

    def register(self, writer: SheetWriter) -> None:
        name = writer.sheet_name
        self._sheets[name] = writer
        log.info("Registered sheet writer: %s", name)

    def build(self, analytics: dict[str, Any]) -> str:
        from excel.writer import DashboardWorkbook

        with DashboardWorkbook() as dw:
            for name, writer in self._sheets.items():
                try:
                    sheet = dw.add_sheet(name)
                    writer.write(sheet, dw.workbook, analytics)
                    log.info("Wrote sheet: %s", name)
                except Exception:
                    log.exception("Failed to write sheet: %s", name)

        return str(dw.path)
