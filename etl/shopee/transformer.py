"""
Shopee order data transformer.

Normalises cities, provinces, products, shipping providers, payment
methods, and datetimes. Converts raw dicts into a canonical Polars DataFrame.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from typing import Any

import polars as pl

from config.config import (
    CANONICAL_COLUMNS,
    CITY_ALIASES,
    PAYMENT_ALIASES,
    PRODUCT_ALIASES,
    PROVINCE_ALIASES,
    SHIPPING_ALIASES,
    STATUS_ALIASES,
)
from core.interfaces import Transformer
from etl.validator import validate_rows
from utils.helpers import (
    normalize_with_alias,
    parse_datetime,
    safe_decimal,
    safe_int,
    safe_string,
)
from utils.logger import get_logger

log = get_logger(__name__)


class ShopeeTransformer(Transformer):
    """Transform Shopee raw dicts into canonical DataFrame."""

    def transform(self, rows: Sequence[dict[str, Any]]) -> pl.DataFrame:
        validated = validate_rows(list(rows))
        if not validated:
            log.warning("No valid rows after validation")
            return pl.DataFrame(schema=self._schema())

        normalised = [self._normalize_row(r) for r in validated]
        df = pl.DataFrame(normalised, schema=self._schema())
        log.info("Transformed %d rows into canonical schema", len(df))
        return df

    def _schema(self) -> dict[str, type]:
        return {col: pl.Utf8 for col in CANONICAL_COLUMNS}

    def _normalize_row(self, row: dict[str, Any]) -> dict[str, Any]:
        return {
            "order_id": safe_string(row.get("order_id")),
            "order_status": normalize_with_alias(
                row.get("order_status"), STATUS_ALIASES, default="unknown"
            ),
            "product_name": self._normalize_product_name(
                safe_string(row.get("product_name"))
            ),
            "product_sku": safe_string(row.get("product_sku")),
            "variation": safe_string(row.get("variation")),
            "quantity": str(safe_int(row.get("quantity"))),
            "price": str(safe_decimal(row.get("price"))),
            "total_amount": str(safe_decimal(row.get("total_amount"))),
            "buyer_name": safe_string(row.get("buyer_name")),
            "buyer_username": self._normalize_username(
                safe_string(row.get("buyer_username"))
            ),
            "city": normalize_with_alias(
                row.get("city"), CITY_ALIASES, default="Unknown City"
            ),
            "province": normalize_with_alias(
                row.get("province"), PROVINCE_ALIASES, default="Unknown Province"
            ),
            "shipping_provider": normalize_with_alias(
                row.get("shipping_provider"), SHIPPING_ALIASES
            ),
            "shipping_method": safe_string(row.get("shipping_method")),
            "shipping_cost": str(safe_decimal(row.get("shipping_cost"))),
            "payment_method": normalize_with_alias(
                row.get("payment_method"), PAYMENT_ALIASES
            ),
            "order_date": parse_datetime(row.get("order_date")) or None,
            "payment_date": parse_datetime(row.get("payment_date")) or None,
            "shipping_date": parse_datetime(row.get("shipping_date")) or None,
            "voucher_seller": str(safe_decimal(row.get("voucher_seller"))),
            "voucher_shopee": str(safe_decimal(row.get("voucher_shopee"))),
            "cancellation_reason": safe_string(row.get("cancellation_reason")),
        }

    @staticmethod
    def _normalize_username(username: str) -> str:
        """Lowercase, strip, and remove common prefixes."""
        name = username.lower().strip()
        for prefix in ("buyer: ", "buyer:", "user: ", "user:"):
            if name.startswith(prefix):
                name = name[len(prefix):]
        return name.strip()

    @staticmethod
    def _normalize_product_name(name: str) -> str:
        """Normalize product name via alias map or clean it."""
        cleaned = name.strip()
        key = cleaned.lower()
        if key in PRODUCT_ALIASES:
            return PRODUCT_ALIASES[key]
        return cleaned
