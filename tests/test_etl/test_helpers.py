"""
Tests for utility helper functions.
"""

from __future__ import annotations

from decimal import Decimal

from utils.helpers import (
    normalize_text,
    normalize_with_alias,
    parse_datetime,
    safe_decimal,
    safe_int,
    safe_divide,
)


def test_safe_decimal_none() -> None:
    assert safe_decimal(None) == Decimal("0")


def test_safe_decimal_string() -> None:
    assert safe_decimal("Rp 50,000") == Decimal("50000")


def test_safe_decimal_invalid() -> None:
    assert safe_decimal("not a number") == Decimal("0")


def test_safe_int() -> None:
    assert safe_int("100") == 100
    assert safe_int(None) == 0
    assert safe_int("not a number") == 0


def test_parse_datetime_iso() -> None:
    result = parse_datetime("2024-01-15 10:00:00")
    assert result == "2024-01-15 10:00:00"


def test_parse_datetime_dmy() -> None:
    result = parse_datetime("15/01/2024 10:00:00")
    assert result == "2024-01-15 10:00:00"


def test_parse_datetime_none() -> None:
    assert parse_datetime(None) is None


def test_normalize_text() -> None:
    assert normalize_text("  Hello  World  ") == "hello world"


def test_normalize_with_alias() -> None:
    aliases = {"jakarta pusat": "Jakarta Pusat"}
    assert normalize_with_alias("Jakarta Pusat", aliases) == "Jakarta Pusat"


def test_normalize_with_alias_default() -> None:
    assert normalize_with_alias(None, {}) == "Unknown"


def test_safe_divide() -> None:
    assert safe_divide(10, 2) == 5.0
    assert safe_divide(10, 0) == 0.0
