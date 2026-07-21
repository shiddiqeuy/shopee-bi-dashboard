"""
Warehouse builder — constructs the star-schema from the staging orders table.

Star schema:
    fact_sales  ←──  dim_customer
                      dim_product
                      dim_city
                      dim_date

The build process:
1  Truncate/reload dimension tables from staging data.
2  Build the calendar dimension (dim_date).
3  Build fact_sales joining dimensions via lookup.
"""

from __future__ import annotations

import duckdb

from utils.logger import get_logger

log = get_logger(__name__)


class WarehouseBuilder:
    """Constructs the dimensional data warehouse from staging data."""

    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self.conn = conn

    def build(self) -> None:
        log.info("Building warehouse star-schema...")
        self._build_dim_customer()
        self._build_dim_product()
        self._build_dim_city()
        self._build_dim_date()
        self._build_fact_sales()
        log.info("Warehouse build complete")

    def _build_dim_customer(self) -> None:
        self.conn.execute("""
            CREATE OR REPLACE TABLE dim_customer AS
            SELECT
                ROW_NUMBER() OVER (ORDER BY buyer_username) AS customer_key,
                buyer_username,
                ANY_VALUE(buyer_name) AS buyer_name,
                MIN(order_date)::DATE AS first_order_date,
                MAX(order_date)::DATE AS last_order_date,
                COUNT(DISTINCT order_id) AS total_orders,
                SUM(total_amount) AS total_revenue,
                ANY_VALUE(city) AS city,
                ANY_VALUE(province) AS province
            FROM orders
            WHERE order_status != 'cancelled'
            GROUP BY buyer_username
        """)
        log.info("Built dim_customer (%d rows)", self._count("dim_customer"))

    def _build_dim_product(self) -> None:
        self.conn.execute("""
            CREATE OR REPLACE TABLE dim_product AS
            SELECT
                ROW_NUMBER() OVER (ORDER BY product_name) AS product_key,
                product_name,
                ANY_VALUE(product_sku) AS product_sku,
                NULL AS category,
                ANY_VALUE(price) AS unit_price
            FROM orders
            GROUP BY product_name
        """)
        log.info("Built dim_product (%d rows)", self._count("dim_product"))

    def _build_dim_city(self) -> None:
        self.conn.execute("""
            CREATE OR REPLACE TABLE dim_city AS
            SELECT
                ROW_NUMBER() OVER (ORDER BY city) AS city_key,
                city AS city_name,
                ANY_VALUE(province) AS province
            FROM orders
            GROUP BY city
        """)
        log.info("Built dim_city (%d rows)", self._count("dim_city"))

    def _build_dim_date(self) -> None:
        self.conn.execute("""
            CREATE OR REPLACE TABLE dim_date AS
            WITH date_range AS (
                SELECT MIN(order_date)::DATE AS min_date,
                       MAX(order_date)::DATE AS max_date
                FROM orders
                WHERE order_date IS NOT NULL
            ),
            dates AS (
                SELECT generate_series AS date
                FROM generate_series(
                    (SELECT min_date FROM date_range),
                    (SELECT max_date FROM date_range),
                    INTERVAL 1 DAY
                )
            )
            SELECT
                CAST(STRFTIME(date, '%Y%m%d') AS INTEGER) AS date_key,
                date,
                EXTRACT(YEAR FROM date)::INTEGER AS year,
                EXTRACT(QUARTER FROM date)::INTEGER AS quarter,
                EXTRACT(MONTH FROM date)::INTEGER AS month,
                STRFTIME(date, '%B') AS month_name,
                EXTRACT(WEEK FROM date)::INTEGER AS week,
                EXTRACT(DAY FROM date)::INTEGER AS day,
                STRFTIME(date, '%A') AS day_name,
                CASE WHEN EXTRACT(DOW FROM date) IN (0, 6) THEN TRUE ELSE FALSE END AS is_weekend
            FROM dates
        """)
        log.info("Built dim_date (%d rows)", self._count("dim_date"))

    def _build_fact_sales(self) -> None:
        self.conn.execute("""
            CREATE OR REPLACE TABLE fact_sales AS
            SELECT
                ROW_NUMBER() OVER (ORDER BY o.order_id) AS sales_key,
                o.order_id,
                COALESCE(dc.customer_key, 0) AS customer_key,
                COALESCE(dp.product_key, 0) AS product_key,
                COALESCE(dci.city_key, 0) AS city_key,
                COALESCE(dd.date_key, 0) AS date_key,
                o.quantity,
                o.price,
                o.total_amount,
                o.shipping_cost,
                o.voucher_seller,
                o.voucher_shopee,
                o.payment_method,
                o.shipping_provider,
                o.order_status
            FROM orders o
            LEFT JOIN dim_customer dc ON o.buyer_username = dc.buyer_username
            LEFT JOIN dim_product dp ON o.product_name = dp.product_name
            LEFT JOIN dim_city dci ON o.city = dci.city_name
            LEFT JOIN dim_date dd ON o.order_date::DATE = dd.date
        """)
        log.info("Built fact_sales (%d rows)", self._count("fact_sales"))

    def _count(self, table: str) -> int:
        result = self.conn.execute(f"SELECT count(*) FROM {table}").fetchone()
        return result[0] if result else 0
