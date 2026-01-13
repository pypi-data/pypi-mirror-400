# src/cdd/executors/registry.py
"""Executor discovery and registration via entry points."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Type

try:
    from importlib.metadata import entry_points
except ImportError:
    entry_points = None  # type: ignore

from cdd_tooling.executors.base import Executor


@dataclass
class ExecutorRegistry:
    """Registry of available executors."""
    executors: Dict[str, Type[Executor]]

    @classmethod
    def discover(cls) -> "ExecutorRegistry":
        """
        Load executors registered under entry-point group: 'cdd.executors'
        """
        out: Dict[str, Type[Executor]] = {}

        if entry_points is None:
            return cls(out)

        eps = entry_points()
        group = None

        # Compat across importlib.metadata versions
        if hasattr(eps, "select"):
            group = eps.select(group="cdd.executors")
        else:
            group = eps.get("cdd.executors", [])

        for ep in group:
            try:
                obj = ep.load()  # Expected: class implementing Executor Protocol
                out[ep.name] = obj
            except Exception:
                # Keep discovery robust; let caller decide how strict to be
                continue

        return cls(out)

    def create(self, name: str) -> Executor:
        """Create an instance of the named executor."""
        if name not in self.executors:
            raise KeyError(f"No executor registered for '{name}'")
        return self.executors[name]()  # type: ignore[call-arg]

    def available(self) -> list[str]:
        """List available executor names."""
        return list(self.executors.keys())
