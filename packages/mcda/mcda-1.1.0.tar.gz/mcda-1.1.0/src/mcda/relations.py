"""This module gathers all classes used to represent binary relations
between alternatives (P, I, R) and the preference structure based on those.
"""
from .internal.core.relations import (
    IncomparableRelation,
    IndifferenceRelation,
    PreferenceRelation,
    PreferenceStructure,
)

P = PreferenceRelation
"""Type alias for user-friendly definition of :class:`PreferenceRelation`"""


I = IndifferenceRelation  # noqa: E741
"""Type alias for user-friendly definition of :class:`IndifferenceRelation`"""


R = IncomparableRelation
"""Type alias for user-friendly definition of :class:`IncomparableRelation`"""

__all__ = [
    "I",
    "IncomparableRelation",
    "IndifferenceRelation",
    "P",
    "PreferenceRelation",
    "PreferenceStructure",
    "R",
]
