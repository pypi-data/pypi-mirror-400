"""This module gathers classes defining set functions.
"""
from __future__ import annotations

import sys
from abc import ABC
from math import factorial, isclose
from typing import Dict, List, Union

import numpy as np
from pandas import DataFrame, Series

from .utils import set_module

if sys.version_info >= (3, 11):  # pragma: nocover
    from typing import Self
else:
    from typing_extensions import Self


@set_module("mcda.set_functions")
class HashableSet(set):
    """This class adds the hashable property to a set object.

    It is intended as a replacement of the native set structure whenever
    a set needs to be hashed (e.g when using sets as dictionary keys).
    """

    def __hash__(self):
        """Return hash as the sum of all its elements' hash.

        :return:
        """
        return sum(hash(e) for e in self)

    def __str__(self) -> str:
        """Return str representation.

        :return:
        """
        return f"{{{', '.join(str(e) for e in self)}}}"

    @classmethod
    def from_index(
        cls, i: int, ensemble: Union[List, None] = None
    ) -> HashableSet:
        """Convert integer mask index into hashable set.

        :param i:
        :param ensemble:
            ensemble from which to build the set (its default value is
            :math:`\\mathbf{Z}^+`)
        :raise ValueError: if `i` is out of bounds for `ensemble`
        """
        ensemble = (
            [*range(int(np.ceil(np.log2(i + 1))))]
            if ensemble is None
            else ensemble
        )
        if i >= 2 ** len(ensemble):
            raise ValueError(
                f"index '{i}' is out of bounds for ensemble: {ensemble}"
            )
        res = cls()
        bit = 1
        for element in ensemble:
            if i & bit != 0:
                res.add(element)
            bit <<= 1
        return res

    @classmethod
    def from_mask(
        cls, mask: str, ensemble: Union[List, None] = None
    ) -> HashableSet:
        """Convert binary mask to hashable set.

        :param mask: contains only the binary mask read from left to right
        :param ensemble:
            ensemble from which to build the set (its default value is
            :math:`\\mathbf{Z}^+`)
        :return: binary set
        """
        return cls.from_index(int(mask, 2), ensemble)

    @classmethod
    def cardinal_range(cls, *args: int) -> List[int]:
        """Return range iterator ordered by cardinality and set content.

        This corresponds to the natural order in which to read a list of values

        :param args: argument available to built-in :func:`range` function
        :return:
        """
        return sorted(
            [i for i in range(*args)],
            key=lambda k: [
                len(HashableSet.from_index(k)),
                *sorted(HashableSet.from_index(k)),
            ],
        )

    @classmethod
    def natural_order(cls, ensemble: List) -> List[HashableSet]:
        """Return list of hashable sets in the natural order

        The natural order is by set cardinality first, ensemble order second.

        :return:
        """
        return [
            HashableSet.from_index(i, ensemble)
            for i in cls.cardinal_range(2 ** len(ensemble))
        ]

    @classmethod
    def logical_order(cls, ensemble: List) -> List[HashableSet]:
        """Return list of hashable sets in the logical order

        The logical order corresponds in the order of the integer
        representation of the sets binary masks.

        :return:
        """
        return [
            HashableSet.from_index(i, ensemble)
            for i in range(2 ** len(ensemble))
        ]


class ISetFunction(ABC):
    """This class represents a set function.

    :param values:
        values of the function as either:
            * a list ordered as a binary mask on the `ensemble`
            * a dictionary with :class:`HashableSet` as keys
            * another :class:`SetFunction` object (used for casting)
    :param ensemble:
        ensemble from which to build the set (its default value is
        :math:`\\mathbf{Z}^+`)
    :param validate:
        if ``True``, raises an error when building an invalid instance
    """

    def __init__(
        self,
        values: Union[List, Dict, ISetFunction],
        ensemble: Union[List, None] = None,
        validate: bool = True,
    ):
        if isinstance(values, ISetFunction):
            self._values = values.values
            self._ensemble = values.ensemble
        elif isinstance(values, dict):
            self._values = {HashableSet(k): v for k, v in values.items()}
            self._ensemble = (
                [*set.union(*self._values.keys())]
                if ensemble is None
                else ensemble
            )
        else:
            self._ensemble = (
                [*range(int(np.ceil(np.log2(len(values)))))]
                if ensemble is None
                else ensemble
            )
            self._values = {
                HashableSet.from_index(i, ensemble): v
                for i, v in enumerate(values)
            }
        if validate:
            self._validate()

    def _validate(self):
        """Validate the instance if it respects its properties.

        The properties are the following:
            * the set is defined on a subset of the ensemble

        :raise KeyError:
            if set function is defined on keys outside the ensemble
        """
        set_ = set.union(*self._values.keys())
        ensemble = set(self._ensemble)
        if set_ != ensemble and not set_.issubset(ensemble):
            raise KeyError(
                f"out of ensemble keys: {set_.difference(ensemble)}"
            )

    def __iter__(self):
        """Return an iterator on the set function values dictionary.

        :return:
        """
        return iter(self._values)

    def __contains__(self, item) -> bool:
        """Return ``True`` if the `item` is inside the set function ensemble.

        :return:
        """
        return item in self._ensemble

    def __len__(self) -> int:
        """Return length of set functions values dictionary.

        :return:
        """
        return len(self._values)

    @property
    def ensemble(self) -> List:
        """Return a copy of the ensemble of this set function.

        :return:
        """
        return self._ensemble.copy()

    @property
    def values(self) -> Dict:
        """Return a copy of the dictionary defining this set function.

        :return:
        """
        return self._values.copy()

    @property
    def size(self) -> int:
        """Return the size of the ensemble of this set function.

        :return:
        """
        return len(self._ensemble)

    @property
    def is_powerset_function(self) -> bool:
        """Check if the set function is defined on a power set.

        Check length of `set_function` is a power of `2`.

        :return:
        """
        n = np.log2(len(self._values))
        return np.ceil(n) == np.floor(n)

    @property
    def is_game(self) -> bool:
        """Check if the set function is a game.

        Check :math:`\\nu(\\emptyset) = 0`

        :return:
        """
        return self() == 0

    @property
    def is_monotonous(self) -> bool:
        """Check if the set function is monotonous.

        Check that
        :math:`\\forall S, T \\subseteq N, S \\subseteq T \\Rightarrow \\nu(S) \\leq \\nu(T)`

        :return:

        .. note:: use :func:`math.isclose` to add tolerance
        """  # noqa E503
        for k in self:
            # Compare capacity to capacity obtained by removing any one part
            for e in k:
                s = k.difference({e})
                if self(*k) < self(*s) and not isclose(self(*k), self(*s)):
                    return False
        return True

    @property
    def is_normal(self) -> bool:
        """Check if the set function is normalized.

        Check `set_function` is a capacity, and that :math:`\\nu(N) = 1`

        :return:

        .. note:: use :func:`math.isclose` to add tolerance
        """
        return HashableSet(self._ensemble) in self._values and isclose(
            self(*self._ensemble), 1
        )

    @property
    def is_additive(self) -> bool:
        """Check if the set function is additive or not.

        Check that
        :math:`\\forall S, T \\subseteq N, S \\cap T = \\emptyset, \\mu(S \\cup T) = \\mu(S) + \\mu(T)`

        :return:

        .. note:: use :func:`math.isclose` to add tolerance
        """  # noqa E503
        ordered_sets = [*self._values.keys()]
        for i, s in enumerate(ordered_sets):
            for t in ordered_sets[(i + 1) :]:
                if len(s.intersection(t)) > 0:
                    continue
                if not isclose(
                    self(*s.union(t)),
                    self(*s) + self(*t),
                ):
                    return False
        return True

    @property
    def is_cardinality_based(self) -> bool:
        """Check if the set function is cardinality-based.

        Check that :math:`\\forall T \\subseteq N, \\mu(T)` only depends on `T`
        cardinality.

        :return:

        .. note:: use :func:`math.isclose` to add tolerance
        """
        cardinal_values = {}
        for k, v in self._values.items():
            if len(k) not in cardinal_values:
                cardinal_values[len(k)] = v
            if not isclose(v, cardinal_values[len(k)]):
                return False
        return True

    @property
    def is_capacity(self) -> bool:
        """Check if the instance is a capacity.

        The properties are the following:
            * the set function is defined on a power set
            * the set function is a game
            * the set function is monotonous
            * the set function is normal

        :return: ``True`` if instance is a capacity, ``False`` otherwise
        """
        return (
            self.is_powerset_function
            and self.is_game
            and self.is_monotonous
            and self.is_normal
        )

    @property
    def as_capacity(self) -> Self:
        """Return the instance if it respects its properties.

        The properties are the following:
            * the set function is defined on a power set
            * the set function is a game
            * the set function is monotonous
            * the set function is normal

        :raise KeyError:
            * if set function is not defined on a power set
        :raise ValueError:
            * if set function is not a game
            * if set function is not monotonous
            * if set function is not normal
        """
        if not self.is_powerset_function:
            raise KeyError("function is not defined on a power set")
        if not self.is_game:
            raise ValueError(f"set function is not a game: {self()} != 0")
        if not self.is_monotonous:
            raise ValueError("set function is not monotonous")
        if not self.is_normal:
            raise ValueError("set function is not normal")
        return self

    @property
    def shapley(self) -> Series:
        """Return Shapley values.

        :return:

        .. note:: Formula is based on :cite:p:`grabisch2008review`.
        """
        return Series(
            {
                i: sum(
                    (
                        factorial(self.size - len(t) - 1)
                        * factorial(len(t))
                        * (self(*t, i) - self(*t))
                    )
                    for t in self
                    if i not in t
                )
                for i in self._ensemble
            }
        ) / factorial(self.size)

    @property
    def interaction_index(self) -> DataFrame:
        """Return interaction index matrix.

        :return:

        .. note:: Formula is based on :cite:p:`grabisch2008review`.
        """
        return DataFrame(
            [
                [
                    float("nan")
                    if i == j
                    else sum(
                        factorial(self.size - len(t) - 2)
                        * factorial(len(t))
                        * (
                            self(*t, i, j)
                            - self(*t, i)
                            - self(*t, j)
                            + self(*t)
                        )
                        for t in self
                        if i not in t and j not in t
                    )
                    for j in self._ensemble
                ]
                for i in self._ensemble
            ],
            index=self.ensemble,
            columns=self.ensemble,
        ) / factorial(self.size - 1)

    def __repr__(self) -> str:  # pragma: nocover
        """Return set function representation.

        :return:
        """
        return f"{self.__class__}({self._values})"

    def __call__(self, *args, **kwargs):
        """Call this set function on the set composed of all provided arguments

        :return: value
        """
        return self._values[HashableSet([*args])]


@set_module("mcda.set_functions")
class SetFunction(ISetFunction):
    """This class represents a set function.

    :param values:
        values of the function as either:
            * a list ordered as a binary mask on the `ensemble`
            * a dictionary with :class:`HashableSet` as keys
            * another :class:`SetFunction` object (used for casting)
    :param ensemble:
        ensemble from which to build the set (its default value is
        :math:`\\mathbf{Z}^+`)
    """

    @property
    def mobius(self) -> Mobius:
        """Return Möbius transform of a set function.

        :return:

        .. note:: Formula is based on :cite:p:`grabisch2008review`.
        """
        res = Mobius([0] * len(self), self.ensemble)
        for t, v in self._values.items():
            for s in self:
                if t.issubset(s):
                    res._values[s] += (-1) ** (len(s) - len(t)) * v
        return res

    def is_k_additive(self, k: int) -> bool:
        """Check if it is a k-additive capacity.

        :param k:
        :return:

        .. note:: use :func:`math.isclose` to add absolute tolerance
        """
        return self.mobius.is_k_additive(k)

    @staticmethod
    def uniform_capacity(ensemble: List) -> SetFunction:
        """Return uniform capacity of given ensemble.

        The uniform capacity on an ensemble `N` of size `size` is given by:

        .. math::

            \\mu^*(T) = t/n, \\forall T \\subseteq N

        :param ensemble:
        :return:

        .. note:: Formula is based on :cite:p:`grabisch2008review`.
        """
        res = SetFunction([0] * 2 ** len(ensemble), ensemble)
        res._values = {k: len(k) / res.size for k in res}
        return res


@set_module("mcda.set_functions")
class Mobius(ISetFunction):
    """This class represents the Möbius transform of a set function.

    :param values:
        values of the function as either:
            * a list ordered as a binary mask on the `ensemble`
            * a dictionary with :class:`HashableSet` as keys
            * another :class:`SetFunction` object (used for casting)
    :param ensemble:
        ensemble from which to build the set (its default value is
        :math:`\\mathbf{Z}^+`)
    """

    @property
    def is_monotonous(self) -> bool:
        """Check if this is the Möbius of a monotonous set function.

        Check `set_function` is a game, and that
        :math:`\\sum_{\\stackrel{T \\subseteq S}{T \\ni i}} m(T) \\geq 0, \\forall S \\subseteq N, \\forall i \\in S`

        :return:

        .. note:: use :func:`math.isclose` to add absolute tolerance
        """  # noqa E503
        for s in self:
            for e in s:
                res = 0.0
                for t in self:
                    if e not in t:
                        continue
                    if t.issubset(s) or s == t:
                        res += self(*t)
                if res < 0 and not isclose(res, 0, abs_tol=1e-9):
                    return False
        return True

    @property
    def is_normal(self) -> bool:
        """Check if the set function is a normalized Möbius.

        Check `set_function` is a möbius capacity, and that
        :math:`\\sum_{T \\subseteq N} m(T) = 1`

        :return:

        .. note:: use :func:`math.isclose` to add tolerance
        """
        return isclose(sum(self._values.values()), 1)

    @property
    def is_additive(self) -> bool:
        """Check if this is the Möbius of an additive set function.

        :return:

        .. note:: use :meth:`is_k_additive` for computation
        """
        return self.is_k_additive(1)

    @property
    def is_cardinality_based(self) -> bool:
        """Check if this is the Möbius of a cardinality-based set function.

        :return:
        """
        return self.set_function.is_cardinality_based

    def is_k_additive(self, k: int) -> bool:
        """Check if it is the Möbius of a k-additive set function.

        :param k:
        :return:

        .. note:: use :func:`math.isclose` to add absolute tolerance
        """
        ok = False
        for t in self:
            if not isclose(self(*t), 0, abs_tol=1e-9):
                if len(t) > k:
                    return False
                if len(t) == k:
                    ok = True
        return ok

    @property
    def shapley(self) -> Series:
        """Return Shapley values.

        :return:

        .. note:: Formula is based on :cite:p:`grabisch2008review`.
        """
        return Series(
            {
                i: sum(self(*t, i) / (len(t) + 1) for t in self if i not in t)
                for i in self._ensemble
            }
        )

    @property
    def interaction_index(self) -> DataFrame:
        """Return interaction index matrix.

        :return:

        .. note:: Formula is based on :cite:p:`grabisch2008review`.
        """
        return DataFrame(
            [
                [
                    float("nan")
                    if i == j
                    else sum(
                        self(*t, i, j) / (len(t) + 1)
                        for t in self
                        if i not in t and j not in t
                    )
                    for j in self._ensemble
                ]
                for i in self._ensemble
            ],
            index=self.ensemble,
            columns=self.ensemble,
        )

    @property
    def set_function(self) -> SetFunction:
        """Return set function from it Möbius transform.

        :return:

        .. note:: Formula is based on :cite:p:`grabisch2008review`.
        """
        res = SetFunction([0] * len(self), self.ensemble)
        for s, v in self._values.items():
            for t in self:
                if s.issubset(t) or s == t:
                    res._values[t] += v
        return res
