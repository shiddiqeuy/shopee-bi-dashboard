"""
Row-level validation for incoming order data.

Validates required fields, data types, and business rules.
Returns a list of (row_index, error_message) tuples for invalid rows.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional

from core.exceptions import InvalidOrderError
from utils.helpers import safe_decimal, safe_int, safe_string

_REQUIRED_FIELDS = [
    "order_id",
    "product_name",
    "quantity",
    "total_amount",
    "buyer_username",
    "order_status",
]


def validate_row(row: dict[str, Any], index: int) -> Optional[InvalidOrderError]:
    """Validate a single raw row dict. Returns None if valid."""

    # ── Required fields ────────────────────────────────────────────────
    for field in _REQUIRED_FIELDS:
        value = row.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            return InvalidOrderError(
                f"Row {index}: missing required field '{field}'",
                context={"row_index": index, "field": field, "value": value},
            )

    # ── order_id must not be empty ─────────────────────────────────────
    order_id = safe_string(row.get("order_id"))
    if not order_id:
        return InvalidOrderError(
            f"Row {index}: empty order_id",
            context={"row_index": index},
        )

    # ── quantity must be positive ──────────────────────────────────────
    qty = safe_int(row.get("quantity"))
    if qty < 0:
        return InvalidOrderError(
            f"Row {index}: negative quantity ({qty})",
            context={"row_index": index, "quantity": qty},
        )

    # ── total_amount must not be negative (allow zero for free items) ──
    total = safe_decimal(row.get("total_amount"))
    if total < Decimal("0"):
        return InvalidOrderError(
            f"Row {index}: negative total_amount ({total})",
            context={"row_index": index, "total_amount": str(total)},
        )

    # ── order_status should not be empty ───────────────────────────────
    status = safe_string(row.get("order_status"))
    if not status:
        return InvalidOrderError(
            f"Row {index}: empty order_status",
            context={"row_index": index},
        )

    return None


def validate_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter out invalid rows and log errors. Returns clean rows."""
    clean: list[dict[str, Any]] = []
    for i, row in enumerate(rows):
        error = validate_row(row, i)
        if error:
            continue
        clean.append(row)
    return clean
