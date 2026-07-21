"""
Analytics engine — registry pattern.

Each analytics module registers itself with a name.
The AnalyticsEngine calls every registered module, collects results,
and returns a unified dict.
"""

from __future__ import annotations

from typing import Any

from core.interfaces import AnalyticsModule, Repository
from utils.logger import get_logger

log = get_logger(__name__)


class AnalyticsEngine:
    """Orchestrates all registered analytics modules."""

    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self._modules: dict[str, AnalyticsModule] = {}

    def register(self, module: AnalyticsModule) -> None:
        name = module.register()
        self._modules[name] = module
        log.info("Registered analytics module: %s", name)

    def compute_all(self) -> dict[str, Any]:
        """Run every registered module and return a unified results dict."""
        results: dict[str, Any] = {}
        for name, module in self._modules.items():
            try:
                module_results = module.compute(self.repository)
                results[name] = module_results
                log.info("Analytics module '%s' completed", name)
            except Exception:
                log.exception("Analytics module '%s' failed", name)
                results[name] = {"error": True}
        results["_module_count"] = len(self._modules)
        results["_module_names"] = list(self._modules.keys())
        return results
