from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from functools import total_ordering
from typing import (
    Any,
    Generic,
    Iterator,
    List,
    Mapping,
    Type,
    TypeVar,
    Union,
    cast,
)

from deprecated.sphinx import versionchanged
from pandas import Series

from .scales import OrdinalScale, QuantitativeScale, Scale, common_scale_type
from .utils import set_module

if sys.version_info >= (3, 11):  # pragma: nocover
    from typing import Self
else:
    from typing_extensions import Self


def series_equals(s1: Series, s2: Series) -> bool:
    """Check if two series have the same values.

    It will realign the indexes if they are ordered differently.

    :param s1:
    :param s2:
    :return:
    """
    return dict(s1) == dict(s2)


class IVector(ABC):
    """This class is a wrapper around :class:`pandas.Series`.

    It is intended to be used for all classes across the package that uses
    a Series as their internal data representation.

    :param data: series containing the data
    :raise KeyError: if some labels are duplicated

    :attr data: internal representation of data
    """

    def __init__(self, data: Series):
        self.data = Series(data)
        if self.data.index.has_duplicates:
            raise KeyError(
                "some labels are duplicated: "
                f"{self.data.index[self.data.index.duplicated()].tolist()}"
            )

    def __eq__(self, other: Any) -> bool:
        """Check if both values have the same data

        :return:

        .. note:: values order does not matter
        """
        if type(other) != type(self):
            return False
        return series_equals(self.data, other.data)

    @property
    def name(self) -> Any:
        """Return the name of the :attr:`data` attribute."""
        return self.data.name

    @property
    def labels(self) -> List:
        """Return the data labels."""
        return self.data.index.tolist()

    def __mul__(self, other: Union[IVector, float]) -> Self:
        """Return product.

        :param other:
        :return:
        """
        coeff = other.data.values if isinstance(other, IVector) else other
        return self.__class__(self.data * coeff)

    def __add__(self, other: Any) -> Self:
        """Return addition.

        :param other:
        :return:
        """
        added = other.data if isinstance(other, IVector) else other
        return self.__class__(self.data + added)

    def __sub__(self, other: Any) -> Self:
        """Return subtraction.

        :param other:
        :return:
        """
        subtracted = other.data if isinstance(other, IVector) else other
        return self.__class__(self.data - subtracted)

    def sum(self) -> float:
        """Return the sum of the data.

        :return:

        .. warning::
            it will raise a :class:`TypeError` if data contains numeric
            and non-numeric values
        """
        return sum(self.data)

    @abstractmethod
    def copy(self) -> Self:  # pragma: nocover
        """Return a copy of the object"""
        pass


S = TypeVar("S", bound=Scale, covariant=True)


@total_ordering
@set_module("mcda.values")
class Value(Generic[S]):
    """This class define a single value along its scale.

    Those instances are comparable with each other, as long as they share a
    common :attr:`scale`, and can be compared to raw values.
    In the latter case, the :attr:`scale` is assumed as beign the scale of the
    raw value.

    :param value:
    :param scale:

    .. note::
        This class is not intended for general use, it is only intended for
        the inspection of :class:`Values` cells.
    """

    def __init__(self, value: Any, scale: S):
        self.value = value
        self.scale = scale

    def __gt__(self, other: Any) -> bool:
        """Check if this value is greater than another.

        :param other: either a raw value or a :class:`Value`
        :raises ValueError:
            if `other` is a :class:`Value` but have a different scale
        :raises TypeError: if `other` is not a :class:`Value` instance
        :return:
            ``True`` if this value is greater than the other, else ``False``
        """
        if not isinstance(other, Value):
            raise TypeError("cannot compare with a scale-less object")
        if self.scale != other.scale:
            raise ValueError("cannot compare values of different scales")
        return self.scale.is_better(self.value, other.value)

    def __eq__(self, other: Any) -> bool:
        """Check if this value is equal to another.

        :param other: either a raw value or a :class:`Value`
        :raises ValueError:
            if `other` is a :class:`Value` but have a different scale
        :raises TypeError: if `other` is not a :class:`Value` instance
        :return:
            ``True`` if this value is equal to the other, else ``False``
        """
        if not isinstance(other, Value):
            raise TypeError("cannot compare with a scale-less object")
        if self.scale != other.scale:
            raise ValueError("cannot compare values of different scales")
        return self.value == other.value

    def __repr__(self) -> str:  # pragma: nocover
        """Representation of the object"""
        return f"<Value value={self.value} scale={repr(self.scale)}>"

    def __str__(self) -> str:  # pragma: nocover
        """Convert object to string"""
        return f"Value(value={self.value}, scale={str(self.scale)})"


@set_module("mcda.values")
class Values(IVector, Mapping[Any, Value[S]], Generic[S]):
    """This class associates a data :class:`pandas.Series` with their
    multiple :class:`mcda.core.Scale`.

    Instances are also immutable mapping of labels and :class:`Value` objects
    and can be accessed, iterated over, as such.

    :param data: series containing the data
    :param scales:
        data scale(s) (one per value or one shared, will be inferred from data
        if absent using :meth:`Scale.fit`)
    :param stype: scales type used
    :raise KeyError: if some labels are duplicated
    :raise TypeError: if `stype` and `scales` types mismatch

    :attr data: internal representation of data
    """

    def __init__(
        self,
        data: Series,
        scales: Union[S, Mapping[Any, S], None] = None,
        stype: Union[Type[S], None] = None,
    ):
        super().__init__(data)
        self.scales: Mapping[Any, S] = {}
        _stype = cast(Type[S], Scale if stype is None else stype)
        bounds = None
        for c in self.labels:
            if isinstance(scales, Mapping) and c in scales:
                self.scales[c] = scales[c]
            elif isinstance(scales, Scale):
                self.scales[c] = cast(S, scales)
            else:
                if bounds is None:
                    bounds = _stype.fit(self.data)
                self.scales[c] = bounds
            if stype and not isinstance(self.scales.get(c), stype):
                raise TypeError("'stype' and 'scales' types mismatch")
        self.stype = (
            cast(
                Type[S],
                common_scale_type([type(s) for s in self.scales.values()]),
            )
            if stype is None
            else stype
        )

    def __len__(self) -> int:
        """Return number of values.

        :return:
        """
        return len(self.data)

    def __iter__(self) -> Iterator:
        """Return an iterator over the labels."""
        return iter(self.labels)

    def __getitem__(self, item: Any) -> Value[S]:
        """Return the value of the data at a specific label.

        :return:
        """
        return Value[S](self.data[item], self.scales[item])

    def __eq__(self, other: Any) -> bool:
        """Check equality of scale values.

        Equality is defines as having the same set of scales, and having the
        same data.

        :return: ``True`` if both are equal
        """
        if not super().__eq__(other):
            return False
        _values = cast(Values, other)
        return self.scales == _values.scales

    @property
    def bounds(self) -> S:
        """Infer one common scale from the data.

        It uses :attr:`stype` and call its :meth:`mcda.core.scales.Scale.fit`
        method.

        :return: inferred scale
        """
        return self.stype.fit(self.data)

    @property
    def within_scales(self) -> Series:
        """Return a series indicating which values are within their
        respective scale.

        :return:
        """
        return Series({k: v in self.scales[k] for k, v in self.data.items()})

    @property
    def is_within_scales(self) -> bool:
        """Check whether all values are within their respective scales.

        :return:
        """
        return self.within_scales.all()

    @property
    def is_numeric(self) -> bool:
        """Check whether values are numeric.

        :return:
        :rtype: bool
        """
        return issubclass(self.stype, QuantitativeScale)

    @property
    def is_ordinal(self) -> bool:
        """Check whether scales are all ordinal.

        :return:
        """
        return issubclass(self.stype, OrdinalScale)

    @property
    def to_numeric(self) -> Values[QuantitativeScale]:
        """Return numeric conversion of ordinal values.

        :raise TypeError: if :attr:`scales` are not ordinal
        """
        if self.is_numeric:
            return cast(Values[QuantitativeScale], self.copy())
        if not self.is_ordinal:
            raise TypeError("cannot convert to numerics nominal values")
        return Values(
            Series(
                {
                    c: cast(OrdinalScale, self.scales[c]).value(v)
                    for c, v in self.data.items()
                }
            ),
            {c: cast(OrdinalScale, s).numeric for c, s in self.scales.items()},
        )

    def sort(self, ascending: bool = False) -> Self:
        """Return sorted data in new instance.

        Numeric values are used to determine the sorting order.

        :param ascending: if ``True``, will sort in ascending order
        :return:
        :raise TypeError: if values are not ordinal

        .. warning:: :attr:`scales` are not taken into account
        """
        if not self.is_ordinal:
            raise TypeError("cannot sort non-ordinal values")
        numerics = self.to_numeric
        copy = self.copy()
        copy.data = self.data[
            numerics.data.sort_values(ascending=ascending).index
        ]
        return copy

    def dominate(self, other: Values) -> bool:
        """Check whether the ranking dominates an other one.

        :param other:
        :return:
            ``True`` if this object dominates ``other``, ``False`` otherwise
        :raise TypeError: if values are not ordinal

        .. note:: this is done according to this object :attr:`scales`
        """
        if not self.is_ordinal:
            raise TypeError("cannot sort non-ordinal values")
        strict_dominance = False
        for criterion, scale in self.scales.items():
            if scale.is_better(other.data[criterion], self.data[criterion]):
                return False
            if scale.is_better(self.data[criterion], other.data[criterion]):
                strict_dominance = True
        return strict_dominance

    def dominate_strongly(self, other: Values) -> bool:
        """Check whether the ranking dominates strongly an other one.

        :param other:
        :return:
            ``True`` if this object dominates strongly ``other``, ``False``
            otherwise
        :raise TypeError: if values are not ordinal

        .. note:: this is done according to this object :attr:`scales`
        """
        if not self.is_ordinal:
            raise TypeError("cannot sort non-ordinal values")
        for criterion, scale in self.scales.items():
            if not scale.is_better(
                self.data[criterion], other.data[criterion]
            ):
                return False
        return True

    def copy(self) -> Self:
        """Return a copy of the object."""
        return self.__class__(self.data.copy(), dict(self.scales), self.stype)


@set_module("mcda.values")
class CommensurableValues(Values[S], Generic[S]):
    """This class describes values with a single scale.

    Instances are also immutable mapping of labels and :class:`Value` objects
    and can be accessed, iterated over, as such.

    :param data:
    :param scale:
    :param stype: scales type used
    :raise KeyError: if some labels are duplicated
    :raise TypeError: if `stype` and `scale` type mismatch

    :attr data: internal representation of data
    """

    def __init__(
        self,
        data: Series,
        scale: S | None = None,
        stype: Union[Type[S], None] = None,
    ):
        super().__init__(data, scale, stype)
        scale = self.stype.fit(self.data) if scale is None else scale
        self.scale = scale

    def __eq__(self, other: Any) -> bool:
        """Check equality of criterion values.

        Equality is defines as having the same scale, and having the
        same data.

        :return: ``True`` if both are equal
        """
        if not IVector.__eq__(self, other):
            return False
        _values = cast(CommensurableValues, other)
        return self.scale == _values.scale

    @property
    def to_numeric(self) -> CommensurableValues[QuantitativeScale]:
        """Return numeric conversion of ordinal values.

        :raise TypeError: if :attr:`scales` are not ordinal
        """
        if self.is_numeric:
            return cast(CommensurableValues[QuantitativeScale], self.copy())
        if not self.is_ordinal:
            raise TypeError("cannot convert to numerics nominal values")
        return CommensurableValues(
            Series(
                {
                    c: cast(OrdinalScale, self.scales[c]).value(v)
                    for c, v in self.data.items()
                }
            ),
            cast(OrdinalScale, self.scale).numeric,
        )

    @versionchanged(
        "original order between equal values is conserved (less surprising)",
        "1.1.0",
    )
    def sort(self, ascending: bool = False) -> Self:
        """
        Return sorted data in new instance.

        Numeric values are used to determine the sorting order.

        :param ascending: if ``True``, will sort in ascending order
        :return:
        :raise TypeError: if values are not ordinal

        .. note:: in case of equal values, original order is conserved

        .. warning:: :attr:`scales` are not taken into account
        """
        if not self.is_ordinal:
            raise TypeError("cannot sort non-ordinal values")
        copy = self.copy()
        ordered_ilocs = sorted(
            list(range(len(copy))),
            key=lambda i: (copy[copy.labels[i]], i),
            reverse=not ascending,
        )
        # Next line is valid according to pandas doc but
        # type stubs seem not to work correctly
        copy.data = self.data.iloc[ordered_ilocs]  # type: ignore
        return copy

    def copy(self) -> Self:
        """Return a copy of the object."""
        return self.__class__(self.data.copy(), self.scale, self.stype)


Ranking = CommensurableValues[OrdinalScale]
"""Type alias for all ranking objects."""
