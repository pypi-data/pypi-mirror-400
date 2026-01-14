"""This package contains MCDA algorithms and utilities.

Core features are directly accessible from this subpackage, while each family
of MCDA algorithms has its own subpackage.
"""
import warnings

from .matrices import PerformanceTable
from .transformers import normalize, transform

__all__ = ["PerformanceTable", "normalize", "transform"]


warnings.filterwarnings("default", category=DeprecationWarning)
