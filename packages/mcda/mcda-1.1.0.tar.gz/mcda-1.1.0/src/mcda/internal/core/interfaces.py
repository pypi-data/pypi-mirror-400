"""This module is used to gather core interfaces and encourage their use for
a more coherent API.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Sequence, TypeVar, Union

from .matrices import OutrankingMatrix
from .relations import PreferenceStructure
from .values import CommensurableValues, Ranking

T = TypeVar("T")


class Learner(Generic[T], ABC):
    """This interface describes a generic learner."""

    @abstractmethod
    def learn(self) -> T:  # pragma: nocover
        """Learn and return an object.

        :return:
        """
        pass


class Ranker(ABC):
    """Interface to implement ranking MCDA algorithms."""

    @abstractmethod
    def rank(
        self, **kwargs
    ) -> Union[
        PreferenceStructure, OutrankingMatrix, Ranking
    ]:  # pragma: nocover
        """Rank alternatives.

        :return: ranking
        """
        pass


class Assignator(ABC):
    """Interface to implement assignment MCDA algorithms."""

    @abstractmethod
    def assign(self, **kwargs) -> CommensurableValues:  # pragma: nocover
        """Assign alternatives to categories.

        :return: assignment of each alternative
        """
        pass


class Selector(ABC):
    """Interface to implement selection MCDA algorithms."""

    @abstractmethod
    def select(self, **kwargs) -> Sequence:  # pragma: nocover
        """Select a subset of alternatives.

        :return: selected alternatives
        """
        pass


class Sorter(ABC):
    """Interface to implement clustering/sorting MCDA algorithms."""

    @abstractmethod
    def sort(self, **kwargs) -> CommensurableValues:  # pragma: nocover
        """Sort alternatives in clusters.

        :return: cluster of each alternative
        """
        pass
