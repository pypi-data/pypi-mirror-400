"""This module gathers MAVT aggregators.
"""
from ..internal.core.aggregators import (
    OWA,
    TOPSIS,
    ULOWA,
    ChoquetIntegral,
    NormalizedWeightedSum,
    Sum,
    WeightedSum,
)

__all__ = [
    "OWA",
    "ULOWA",
    "ChoquetIntegral",
    "NormalizedWeightedSum",
    "Sum",
    "WeightedSum",
    "TOPSIS",
]
