"""
ETL run log persistence.

Each ETL run writes a structured log record that can be queried
for auditing and monitoring.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from config.config import LOG_DIR


class ETLLogWriter:
    """Writes structured JSON log entries for each ETL run."""

    def __init__(self, log_dir: str | Path | None = None) -> None:
        self.log_dir = Path(log_dir) if log_dir else LOG_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._log_file = self.log_dir / "etl_runs.jsonl"

    def write_run(
        self,
        source_file: str,
        rows_extracted: int,
        rows_loaded: int,
        rows_invalid: int,
        status: str,
        error_message: Optional[str] = None,
        extra: Optional[dict[str, Any]] = None,
    ) -> None:
        """Append a single ETL run record."""
        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_file": source_file,
            "rows_extracted": rows_extracted,
            "rows_loaded": rows_loaded,
            "rows_invalid": rows_invalid,
            "status": status,
            "error_message": error_message,
            "extra": extra or {},
        }
        with open(self._log_file, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")

    def read_runs(self, limit: int = 100) -> list[dict[str, Any]]:
        """Return the most recent *limit* run records."""
        if not self._log_file.exists():
            return []
        records: list[dict[str, Any]] = []
        with open(self._log_file, "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return records[-limit:]
