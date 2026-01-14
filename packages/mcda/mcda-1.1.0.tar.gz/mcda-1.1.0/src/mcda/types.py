"""This module gathers types used throughout the package."""
import mcda.internal.core.aliases
import mcda.internal.core.scales

from .internal.core.relations import Relation
from .internal.core.scales import OrdinalScale, Scale

Function = mcda.internal.core.aliases.Function
"""Type alias for single argument python functions (callables)."""

NumericFunction = mcda.internal.core.aliases.NumericFunction
"""Type alias for single argument python numeric functions (callables)."""

BinaryScale = mcda.internal.core.scales.BinaryScale
"""Type alias for binary scale"""

NormalScale = mcda.internal.core.scales.NormalScale
"""Type alias for normal scale"""

__all__ = [
    "Relation",
    "BinaryScale",
    "NormalScale",
    "OrdinalScale",
    "Scale",
    "Function",
    "NumericFunction",
]
