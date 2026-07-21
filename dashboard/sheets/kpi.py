"""
KPI Summary sheet — comprehensive KPI table with all business metrics.
"""

from __future__ import annotations

from typing import Any

from core.interfaces import SheetWriter
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class KPISummarySheet(SheetWriter):
    """Comprehensive KPI summary table."""

    @property
    def sheet_name(self) -> str:
        return "KPI Summary"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:E2", "KPI Summary", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:B", 30)
        sheet.set_column("C:C", 20)
        sheet.set_column("D:D", 14)

        customer = analytics.get("customer", {})
        product = analytics.get("product", {})
        city = analytics.get("city", {})
        province = analytics.get("province", {})
        shipping = analytics.get("shipping", {})
        payment = analytics.get("payment", {})
        cancellation = analytics.get("cancellation", {})

        kpis = [
            ("Revenue & Orders", "", ""),
            ("Total Revenue", f"Rp {customer.get('total_revenue', 0):,.0f}", ""),
            ("Total Orders", f"{sum(c.get('order_count', 0) for c in city.get('cities', [])):,}", ""),
            ("Average Basket", f"Rp {customer.get('avg_basket', 0):,.0f}", ""),
            ("", "", ""),
            ("Customer Metrics", "", ""),
            ("Total Customers", f"{customer.get('total_customers', 0):,}", ""),
            ("Repeat Customers", f"{customer.get('repeat_customers', 0):,}", ""),
            ("New Customers", f"{customer.get('new_customers', 0):,}", ""),
            ("Repeat Rate", f"{customer.get('repeat_rate', 0):.1f}%", ""),
            ("Avg CLV", f"Rp {customer.get('avg_clv', 0):,.0f}", ""),
            ("", "", ""),
            ("Product Metrics", "", ""),
            ("Total Products", f"{product.get('total_products', 0):,}", ""),
            ("Fast Moving Products", f"{len(product.get('fast_moving', [])):,}", ""),
            ("", "", ""),
            ("Geographic Metrics", "", ""),
            ("Cities Covered", f"{len(city.get('cities', [])):,}", ""),
            ("Provinces Covered", f"{province.get('total_provinces', 0):,}", ""),
            ("", "", ""),
            ("Shipping Metrics", "", ""),
            ("Shipping Providers", f"{len(shipping.get('providers', [])):,}", ""),
            ("Total Shipping Orders", f"{shipping.get('total_orders', 0):,}", ""),
            ("", "", ""),
            ("Payment Metrics", "", ""),
            ("Payment Methods", f"{len(payment.get('methods', [])):,}", ""),
            ("", "", ""),
            ("Cancellation", "", ""),
            ("Cancellation Rate", f"{cancellation.get('cancellation_rate', 0):.1f}%", ""),
            ("Cancelled Orders", f"{cancellation.get('cancelled_orders', 0):,}", ""),
        ]

        row = 4
        for label, value, _ in kpis:
            if value == "" and label != "":
                sheet.write(row, 1, label, styles.section_header)
            elif label == "":
                row += 1
                continue
            else:
                sheet.write(row, 1, label, styles.table_cell)
                sheet.write(row, 2, value, styles.table_cell_alt)
            row += 1
