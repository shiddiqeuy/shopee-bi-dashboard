"""
Pure helper functions — no side effects, fully testable.

All functions are strongly typed with no dependency on global state.
"""

from __future__ import annotations

import re
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Optional

import numpy as np

_DATETIME_FORMATS = [
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
    "%d/%m/%Y %H:%M:%S",
    "%d/%m/%Y %H:%M",
    "%d/%m/%Y",
    "%m/%d/%Y %H:%M:%S",
    "%m/%d/%Y",
    "%d-%m-%Y %H:%M:%S",
    "%d-%m-%Y",
    "%Y/%m/%d %H:%M:%S",
    "%Y/%m/%d",
]

_WHITESPACE_RE = re.compile(r"\s+")


def safe_decimal(value: Any, default: Decimal = Decimal("0")) -> Decimal:
    """Convert *value* to Decimal safely."""
    if value is None:
        return default
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float)):
        return Decimal(str(value))
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "").replace("Rp", "").replace("rp", "")
        cleaned = _WHITESPACE_RE.sub("", cleaned)
        if cleaned in ("", "-", "--", "null", "none"):
            return default
        try:
            return Decimal(cleaned)
        except InvalidOperation:
            return default
    return default


def safe_int(value: Any, default: int = 0) -> int:
    """Convert *value* to int safely."""
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        if cleaned in ("", "-", "--", "null", "none"):
            return default
        try:
            return int(float(cleaned))
        except (ValueError, OverflowError):
            return default
    return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """Convert *value* to float safely."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "").replace("Rp", "").replace("rp", "")
        cleaned = _WHITESPACE_RE.sub("", cleaned)
        if cleaned in ("", "-", "--", "null", "none"):
            return default
        try:
            return float(cleaned)
        except ValueError:
            return default
    return default


def safe_string(value: Any, default: str = "") -> str:
    """Convert *value* to a stripped string safely."""
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (int, float, Decimal)):
        return str(value)
    return str(value).strip()


def parse_datetime(value: Any) -> Optional[str]:
    """Try to parse *value* and return ISO-8601 string, or None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, str):
        cleaned = value.strip()
        if not cleaned or cleaned in ("-", "--", "null", "none", "NaT"):
            return None
        for fmt in _DATETIME_FORMATS:
            try:
                return datetime.strptime(cleaned, fmt).strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                continue
    return None


def parse_date(value: Any) -> Optional[str]:
    """Parse and return date-only ISO string (YYYY-MM-DD)."""
    dt = parse_datetime(value)
    if dt:
        return dt[:10]
    return None


def normalize_text(text: Optional[str]) -> str:
    """Lowercase, strip, and collapse whitespace."""
    if not text:
        return ""
    return _WHITESPACE_RE.sub(" ", text.strip().lower())


def normalize_with_alias(
    value: Optional[str],
    alias_map: dict[str, str],
    default: str = "Unknown",
) -> str:
    """Look up *value* in *alias_map* after normalising, or return *default*."""
    key = normalize_text(value)
    if not key:
        return default
    return alias_map.get(key, value.strip() if value else default)


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Divide avoiding ZeroDivisionError."""
    if denominator == 0:
        return default
    return numerator / denominator


def to_list(value: Any) -> list:
    """Wrap non-list in a list; return empty list for None."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def is_nan(value: Any) -> bool:
    """Check for NaN across types."""
    if value is None:
        return False
    try:
        return np.isnan(float(value))
    except (TypeError, ValueError):
        return False
