"""This module contains all functions related to matrices (2D and 3D).
"""
from .internal.core.matrices import (
    AdditivePerformanceTable,
    AdjacencyValueMatrix,
    PartialValueMatrix,
    PerformanceTable,
    create_outranking_matrix,
    dataframe_equals,
)

__all__ = [
    "AdditivePerformanceTable",
    "AdjacencyValueMatrix",
    "PartialValueMatrix",
    "PerformanceTable",
    "create_outranking_matrix",
    "dataframe_equals",
]
