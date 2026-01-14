"""This module implements the Electre algorithms.

Implementation and naming conventions are taken from
:cite:p:`vincke1998electre`.
"""
from ..internal.outranking.electre import (
    Electre1,
    Electre2,
    Electre3,
    ElectreTri,
)

__all__ = [
    "Electre1",
    "Electre2",
    "Electre3",
    "ElectreTri",
]
