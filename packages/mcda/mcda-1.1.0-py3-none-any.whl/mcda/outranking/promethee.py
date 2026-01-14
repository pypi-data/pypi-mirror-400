"""This module implements Promethee algorithms in a heavily modular way.
"""
from ..internal.outranking.promethee import (
    Promethee1,
    Promethee2,
    PrometheeGaia,
    criteria_flows,
    negative_flows,
    net_outranking_flows,
    positive_flows,
)

__all__ = [
    "Promethee1",
    "Promethee2",
    "PrometheeGaia",
    "criteria_flows",
    "negative_flows",
    "net_outranking_flows",
    "positive_flows",
]
