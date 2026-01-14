"""This module gathers all classes and utilities used to work with sequence
of values (1D data).
"""
from .internal.core.values import (
    CommensurableValues,
    Value,
    Values,
    series_equals,
)

__all__ = ["CommensurableValues", "Value", "Values", "series_equals"]
