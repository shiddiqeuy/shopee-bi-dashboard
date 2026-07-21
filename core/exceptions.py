"""
Domain-specific exceptions.

Each exception carries structured context so upstream handlers can
log, report, or recover intelligently.
"""

from __future__ import annotations

from typing import Any, Optional


class ShopeeBIError(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str,
        context: Optional[dict[str, Any]] = None,
    ) -> None:
        self.context = context or {}
        super().__init__(message)


class InvalidOrderError(ShopeeBIError):
    """Raised when an order row fails validation."""


class DuplicateOrderError(ShopeeBIError):
    """Raised when a duplicate order_id is detected (before dedup)."""


class MissingColumnError(ShopeeBIError):
    """Raised when a required column is missing from source data."""


class SchemaMismatchError(ShopeeBIError):
    """Raised when source columns don't match expected schema."""


class ETLPipelineError(ShopeeBIError):
    """Raised when an ETL pipeline stage fails."""


class DatabaseError(ShopeeBIError):
    """Raised on database connection or query failure."""


class AnalyticsError(ShopeeBIError):
    """Raised when an analytics computation fails."""


class DashboardError(ShopeeBIError):
    """Raised during Excel dashboard generation."""


class ConfigurationError(ShopeeBIError):
    """Raised when configuration is invalid or missing."""


class NormalisationError(ShopeeBIError):
    """Raised when a value cannot be normalised."""


class InsightGenerationError(ShopeeBIError):
    """Raised when the insight engine encounters an error."""
