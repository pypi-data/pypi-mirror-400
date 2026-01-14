"""This module gathers type aliases used throughout the package."""
from __future__ import annotations

from typing import Any, Callable

Function = Callable[[Any], Any]
"""Type alias for single argument python functions (callables)."""

NumericFunction = Callable[[float], float]
"""Type alias for single argument python numeric functions (callables)."""
