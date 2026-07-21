"""
Schema migrations for the DuckDB warehouse.

Tracks applied versions in a `_schema_version` table and applies
pending migrations in order.
"""

from __future__ import annotations

import duckdb

from utils.logger import get_logger

log = get_logger(__name__)

# Each migration is a (version, description, sql) tuple.
_MIGRATIONS: list[tuple[int, str, str]] = [
    (1, "Create orders staging table", """
    CREATE TABLE IF NOT EXISTS orders (
        order_id            VARCHAR,
        order_status        VARCHAR,
        product_name        VARCHAR,
        product_sku         VARCHAR,
        variation           VARCHAR,
        quantity            INTEGER,
        price               DECIMAL(18,2),
        total_amount        DECIMAL(18,2),
        buyer_name          VARCHAR,
        buyer_username      VARCHAR,
        city                VARCHAR,
        province            VARCHAR,
        shipping_provider   VARCHAR,
        shipping_method     VARCHAR,
        shipping_cost       DECIMAL(18,2),
        payment_method      VARCHAR,
        order_date          TIMESTAMP,
        payment_date        TIMESTAMP,
        shipping_date       TIMESTAMP,
        voucher_seller      DECIMAL(18,2),
        voucher_shopee      DECIMAL(18,2),
        cancellation_reason VARCHAR,
        _loaded_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """),
    (2, "Create dim_customer table", """
    CREATE TABLE IF NOT EXISTS dim_customer (
        customer_key       INTEGER PRIMARY KEY,
        buyer_username     VARCHAR UNIQUE,
        buyer_name         VARCHAR,
        first_order_date   DATE,
        last_order_date    DATE,
        total_orders       INTEGER,
        total_revenue      DECIMAL(18,2),
        city               VARCHAR,
        province           VARCHAR
    );
    """),
    (3, "Create dim_product table", """
    CREATE TABLE IF NOT EXISTS dim_product (
        product_key     INTEGER PRIMARY KEY,
        product_name    VARCHAR,
        product_sku     VARCHAR,
        category        VARCHAR,
        unit_price      DECIMAL(18,2)
    );
    """),
    (4, "Create dim_city table", """
    CREATE TABLE IF NOT EXISTS dim_city (
        city_key   INTEGER PRIMARY KEY,
        city_name  VARCHAR,
        province   VARCHAR
    );
    """),
    (5, "Create dim_date table", """
    CREATE TABLE IF NOT EXISTS dim_date (
        date_key    INTEGER PRIMARY KEY,
        date        DATE,
        year        INTEGER,
        quarter     INTEGER,
        month       INTEGER,
        month_name  VARCHAR,
        week        INTEGER,
        day         INTEGER,
        day_name    VARCHAR,
        is_weekend  BOOLEAN
    );
    """),
    (6, "Create fact_sales table", """
    CREATE TABLE IF NOT EXISTS fact_sales (
        sales_key       INTEGER PRIMARY KEY,
        order_id        VARCHAR,
        customer_key    INTEGER,
        product_key     INTEGER,
        city_key        INTEGER,
        date_key        INTEGER,
        quantity        INTEGER,
        price           DECIMAL(18,2),
        total_amount    DECIMAL(18,2),
        shipping_cost   DECIMAL(18,2),
        voucher_seller  DECIMAL(18,2),
        voucher_shopee  DECIMAL(18,2),
        payment_method  VARCHAR,
        shipping_provider VARCHAR,
        order_status    VARCHAR
    );
    """),
]


def _ensure_version_table(conn: duckdb.DuckDBPyConnection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _schema_version (
            version     INTEGER PRIMARY KEY,
            description VARCHAR,
            applied_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)


def _applied_versions(conn: duckdb.DuckDBPyConnection) -> set[int]:
    try:
        rows = conn.execute("SELECT version FROM _schema_version").fetchall()
        return {r[0] for r in rows}
    except Exception:
        return set()


def migrate(conn: duckdb.DuckDBPyConnection) -> None:
    """Apply all pending migrations in order."""
    _ensure_version_table(conn)
    applied = _applied_versions(conn)

    for version, description, sql in _MIGRATIONS:
        if version in applied:
            continue
        log.info("Applying migration %d: %s", version, description)
        try:
            conn.execute(sql)
            conn.execute(
                "INSERT INTO _schema_version (version, description) VALUES (?, ?)",
                [version, description],
            )
        except Exception:
            log.exception("Migration %d failed", version)
            raise
