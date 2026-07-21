"""
Tests for row-level validation.
"""

from __future__ import annotations

from etl.validator import validate_row, validate_rows


def test_valid_row() -> None:
    row = {
        "order_id": "ORD-001",
        "order_status": "completed",
        "product_name": "Product A",
        "quantity": 2,
        "total_amount": "100000",
        "buyer_username": "budi01",
    }
    assert validate_row(row, 0) is None


def test_missing_order_id() -> None:
    row = {
        "order_id": "",
        "order_status": "completed",
        "product_name": "Product A",
        "quantity": 2,
        "total_amount": "100000",
        "buyer_username": "budi01",
    }
    error = validate_row(row, 0)
    assert error is not None
    assert "missing required field" in str(error)


def test_negative_quantity() -> None:
    row = {
        "order_id": "ORD-001",
        "order_status": "completed",
        "product_name": "Product A",
        "quantity": -1,
        "total_amount": "100000",
        "buyer_username": "budi01",
    }
    error = validate_row(row, 0)
    assert error is not None
    assert "negative quantity" in str(error)


def test_valid_rows_filtering() -> None:
    rows = [
        {
            "order_id": "ORD-001",
            "order_status": "completed",
            "product_name": "Product A",
            "quantity": 2,
            "total_amount": "100000",
            "buyer_username": "budi01",
        },
        {
            "order_id": "",
            "order_status": "completed",
            "product_name": "Product B",
            "quantity": 1,
            "total_amount": "50000",
            "buyer_username": "ani89",
        },
    ]
    clean = validate_rows(rows)
    assert len(clean) == 1
    assert clean[0]["order_id"] == "ORD-001"
