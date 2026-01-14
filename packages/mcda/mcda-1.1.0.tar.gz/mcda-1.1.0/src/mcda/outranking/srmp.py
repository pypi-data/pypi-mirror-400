"""This module implements the SRMP algorithm,
as well as the preference elicitation algorithm and plot functions.

Implementation and naming conventions are taken from
:cite:p:`olteanu2022preference`.
"""
from ..internal.outranking.srmp import SRMP, ProfileWiseOutranking, SRMPLearner

__all__ = ["ProfileWiseOutranking", "SRMP", "SRMPLearner"]
