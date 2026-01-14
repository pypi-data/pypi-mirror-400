"""This module gathers all data scales and their features.
"""
from .internal.core.scales import (
    DiscreteQuantitativeScale,
    FuzzyScale,
    NominalScale,
    PreferenceDirection,
    QualitativeScale,
    QuantitativeScale,
    common_scale_type,
)

MIN = PreferenceDirection.MIN
"""User-friendly way to call :attr:`PreferenceDirection.MIN`"""


MAX = PreferenceDirection.MAX
"""User-friendly way to call :attr:`PreferenceDirection.MAX`"""

__all__ = [
    "MAX",
    "MIN",
    "DiscreteQuantitativeScale",
    "FuzzyScale",
    "NominalScale",
    "PreferenceDirection",
    "QualitativeScale",
    "QuantitativeScale",
    "common_scale_type",
]
