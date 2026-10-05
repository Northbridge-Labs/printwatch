"""Minimal dependency-injection container (~30 lines, dict-based providers).

Usage::

    from apps.common.container import container

    container.register("job_ingestion", JobIngestionFacade(repo, ...))
    svc = container.resolve("job_ingestion")

Providers are singletons by default; pass ``singleton=False`` for factories.
Tests can override registrations without monkeypatching.
"""
from __future__ import annotations

from typing import Any, Callable


class Container:
    def __init__(self) -> None:
        self._factories: dict[str, Callable[..., Any]] = {}
        self._singletons: dict[str, Any] = {}
        self._is_singleton: dict[str, bool] = {}

    def register(
        self,
        name: str,
        factory: Callable[..., Any],
        *,
        singleton: bool = True,
    ) -> None:
        self._factories[name] = factory
        self._singletons.pop(name, None)
        self._is_singleton[name] = singleton

    def resolve(self, name: str) -> Any:
        if self._is_singleton.get(name, True):
            if name not in self._singletons:
                self._singletons[name] = self._factories[name]()
            return self._singletons[name]
        return self._factories[name]()

    def reset(self) -> None:
        """Clear all cached singletons (used in tests)."""
        self._singletons.clear()


container = Container()