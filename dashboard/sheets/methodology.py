"""
Methodology sheet — explains the analytics approach and metrics definitions.
"""

from __future__ import annotations

from typing import Any

from core.interfaces import SheetWriter
from excel.navigation import add_back_button
from excel.styles import DashboardStyles


class MethodologySheet(SheetWriter):
    """Methodology documentation for the dashboard."""

    @property
    def sheet_name(self) -> str:
        return "Methodology"

    def write(self, sheet: Any, workbook: Any, analytics: dict[str, Any]) -> None:
        styles = DashboardStyles(workbook)
        add_back_button(sheet, styles)

        sheet.merge_range("B2:E2", "Methodology", styles.title)
        sheet.set_column("A:A", 4)
        sheet.set_column("B:B", 20)
        sheet.set_column("C:E", 40)

        sections = [
            ("Data Source", "",
             "Orders are exported from Shopee Seller Centre and processed through an automated ETL pipeline."),
            ("ETL Process", "",
             "1. Extract: Read all .xlsx files from the input/ directory.\n"
             "2. Transform: Normalise column names, city/province names, shipping providers, "
             "payment methods, and product names. Remove duplicates by order_id.\n"
             "3. Load: Insert into DuckDB warehouse (star schema)."),
            ("Data Warehouse", "",
             "The warehouse uses a star schema:\n"
             "- fact_sales: Transaction fact table\n"
             "- dim_customer: Customer dimension\n"
             "- dim_product: Product dimension\n"
             "- dim_city: Geographic city dimension\n"
             "- dim_date: Calendar date dimension"),
            ("Customer Metrics", "Repeat Rate", "Percentage of customers who placed more than 1 order."),
            ("", "CLV (Customer Lifetime Value)", "Average total revenue per customer."),
            ("", "RFM Score", "Recency, Frequency, Monetary scoring — higher is better."),
            ("", "Segmentation", "Customers grouped into: Champion, Loyal, Potential, At Risk, Needs Attention, Lost."),
            ("Product Metrics", "ABC Classification", "A = top 70% revenue, B = next 20%, C = bottom 10%."),
            ("", "Pareto 80/20", "Products contributing the top 80% of revenue."),
            ("", "Fast Moving", "Products with sales in the last 30 days."),
            ("", "Slow Moving", "Products with no sales in the last 90 days."),
            ("Geographic Metrics", "Opportunity Score", "Composite: revenue growth + customer growth + repeat rate + avg basket."),
            ("", "Growth Rate", "Period-over-period revenue change (latest month vs previous)."),
            ("Cancellation Metrics", "Cancellation Rate", "Cancelled orders / total orders × 100."),
            ("Insight Engine", "", "Automatically detects patterns, anomalies, and generates management recommendations."),
            ("Dashboard", "", "Built with Python + XlsxWriter. Professional green-blue theme. "
             "All sheets have navigation buttons, auto-width columns, and conditional formatting."),
            ("Future Roadmap", "",
             "- Shopee API integration\n- Tokopedia & TikTok Shop support\n"
             "- Streamlit interactive dashboard\n- Meta Ads & Google Ads cost data\n"
             "- ERP & CRM integration\n- Predictive analytics (prophet)"),
        ]

        row = 4
        for section, subtitle, body in sections:
            if section:
                sheet.write(row, 1, section, styles.section_header)
                row += 1
            if subtitle:
                sheet.write(row, 1, subtitle, styles.insight_title)
                sheet.merge_range(row, 2, row, 4, body, styles.methodology_body)
            else:
                sheet.merge_range(row, 1, row, 4, body, styles.methodology_body)
            sheet.set_row(row, max(30, body.count("\n") * 16 + 20))
            row += 1
