from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Type, TypeVar, Union, cast

import numpy as np
from pandas import Series
from pandas.api.types import is_numeric_dtype

from .functions import FuzzyNumber, Interval
from .utils import set_module

if sys.version_info >= (3, 11):  # pragma: nocover
    from typing import Self
else:
    from typing_extensions import Self


@set_module("mcda.scales")
class PreferenceDirection(Enum):
    """Enumeration of MCDA preference directions."""

    MIN = "MIN"
    MAX = "MAX"

    @classmethod
    def has_value(cls, x: PreferenceDirection) -> bool:
        """Check if value is in enumeration.

        :param x:
        :return:
        """
        return isinstance(x, cls)

    @classmethod
    def content_message(cls) -> str:  # pragma: nocover
        """Return list of items and their values.

        :return:
        """
        s = ", ".join(f"{item}: {item.value}" for item in cls)
        return "PreferenceDirection only has following values " + s


@set_module("mcda.types")
class Scale(ABC):
    """Basic abstract class for MCDA scale.

    :attr preference_direction:
    """

    def __init__(self, **kwargs) -> None:
        self.preference_direction: Union[PreferenceDirection, None] = None

    @abstractmethod
    def __eq__(self, other) -> bool:  # pragma: nocover
        """Test equality of objects.

        :param other:
        :return:
        """
        pass

    @abstractmethod
    def __contains__(self, x: Any) -> bool:  # pragma: nocover
        """Check if values are inside scale.

        :param x:
        :return:
        """
        pass

    @abstractmethod
    def range(self, nb: Union[int, None] = None) -> List:  # pragma: nocover
        """Return range of value from scale.

        :param nb: number of values to return
        :return:
        """
        pass

    def is_better(self, x: Any, y: Any) -> bool:
        """Check if x is better than y according to this scale.

        :param x:
        :param y:
        :return:
        :raise TypeError: if scale is not ordinal
        """
        raise TypeError("non-ordinal scale cannot be used to order values")

    def is_better_or_equal(self, x: Any, y: Any) -> bool:
        """Check if x is better or equal to y according to this scale

        :param x:
        :param y:
        :param scale:
        :return:
        """
        return (x in self and x == y) or self.is_better(x, y)

    @classmethod
    def fit(cls, data: Series, **kwargs) -> Self:
        """Create a scale that fits the data.

        :param data:
        :return: scale
        """
        scale: Scale
        if is_numeric_dtype(data):
            scale = QuantitativeScale.fit(data, **kwargs)
        else:
            scale = NominalScale.fit(data, **kwargs)
        return cast(Self, scale)


@set_module("mcda.scales")
class NominalScale(Scale):
    """This class implements a MCDA nominal scale.

    :param labels:
    """

    def __init__(self, labels: List, **kwargs):
        """Constructor method"""
        super().__init__(**kwargs)
        self.labels = labels

    def __repr__(self) -> str:  # pragma: nocover
        """Return string representation of scale.

        :return:
        """
        return f"{self.__class__.__name__}(labels={str(self.labels)})"

    def __eq__(self, other) -> bool:
        """Test equality of nominal scales.

        Equality is defined as being the same scale types, and having
        the same set of :attr:`labels`.

        :param other:
        :return:
        """
        if type(other) != type(self):
            return False
        return set(self.labels) == set(cast(NominalScale, other).labels)

    def __contains__(self, x: Any) -> bool:
        """Check if values are inside scale.

        :param x:
        :return:
        """
        return x in self.labels

    def range(self, nb: Union[int, None] = None) -> List:
        """Return range of value from scale.

        :param nb: number of values to return (always ignored here)
        :return:
        """
        return self.labels

    @classmethod
    def fit(cls, data: Series, **kwargs) -> NominalScale:
        """Create a scale that fits the data.

        :param data:
        :return: scale
        """
        return cls(data.unique().tolist())


@set_module("mcda.types")
class OrdinalScale(Scale, ABC):
    """This class defines a MCDA ordinal scale.

    :param preference_direction:
    """

    def __init__(
        self,
        preference_direction: Union[PreferenceDirection, None] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.preference_direction = preference_direction

    @property
    @abstractmethod
    def interval(self) -> Interval:  # pragma: nocover
        """Return interval on which scale is defined."""
        pass

    @property
    @abstractmethod
    def numeric(self) -> QuantitativeScale:  # pragma: nocover
        """Return corresponding numeric scale."""
        pass

    @abstractmethod
    def value(self, x: Any) -> float:  # pragma: nocover
        """Return corresponding numeric value.

        :param x:
        :return:
        """
        pass

    @abstractmethod
    def label(self, x: float) -> Any:  # pragma: nocover
        """Return scale value corresponding to given number.

        :param x:
        :return:
        """
        pass

    def is_better(self, x: Any, y: Any) -> bool:
        """Check if x is better than y according to this scale.

        :param x:
        :param y:
        :return:
        """
        return (
            self.value(x) < self.value(y)
            if self.preference_direction == PreferenceDirection.MIN
            else self.value(x) > self.value(y)
        )

    @classmethod
    def fit(
        cls,
        data: Series,
        preference_direction: Union[PreferenceDirection, None] = None,
        **kwargs,
    ) -> Self:
        """Create a scale that fits the data.

        :param data:
        :param preference_direction:
        :return: scale
        """
        scale: OrdinalScale
        if is_numeric_dtype(data):
            scale = QuantitativeScale.fit(
                data, preference_direction=preference_direction, **kwargs
            )
        else:
            scale = QualitativeScale.fit(
                data, preference_direction=preference_direction, **kwargs
            )
        return cast(Self, scale)


@set_module("mcda.scales")
class QuantitativeScale(OrdinalScale):
    """Class for quantitative scale (interval based).

    :param arg1: min boundary of scale or complete interval
    :param dmax:
        max boundary of scale (only considered if `arg1` type is not interval)
    :param min_in: is min boundary inside scale or not
    :param max_in: is max boundary inside scale or not
    :param preference_direction:
    :raises ValueError: if `dmin` bigger than `dmax`
    """

    def __init__(
        self,
        arg1: Union[float, Interval] = -float("inf"),
        dmax: float = float("inf"),
        min_in: bool = True,
        max_in: bool = True,
        preference_direction: Union[PreferenceDirection, None] = None,
        **kwargs,
    ):
        if isinstance(arg1, Interval):
            self._interval = arg1
        else:
            self._interval = Interval(arg1, dmax, min_in=min_in, max_in=max_in)
        super().__init__(preference_direction=preference_direction, **kwargs)

    @property
    def interval(self) -> Interval:
        """Return interval on which scale is defined."""
        return self._interval

    @property
    def numeric(self) -> QuantitativeScale:
        """Return corresponding numeric scale."""
        return self

    @staticmethod
    def normal() -> NormalScale:
        """Return normal scale.

        :return:
        """
        return QuantitativeScale(0, 1)

    def __repr__(self) -> str:  # pragma: nocover
        """Return string representation of interval.

        :return:
        """
        if self.preference_direction:
            return (
                f"{self.__class__.__name__}(interval={self.interval}, "
                f"preference_direction={self.preference_direction})"
            )
        return f"{self.__class__.__name__}(interval={self.interval})"

    def __eq__(self, other) -> bool:
        """Test equality of quantitative scales.

        Equality is defined as being the same scale types, having the same
        :attr:`values`.

        :param other:
        :return:
        """
        if not isinstance(other, QuantitativeScale) or isinstance(
            other, DiscreteQuantitativeScale
        ):
            return False
        _scale = cast(QuantitativeScale, other)
        if self.preference_direction != _scale.preference_direction:
            return False
        return self.interval == _scale.interval

    def __contains__(self, x: Any) -> bool:
        """Check if values are inside scale.

        :param x:
        :return:
        """
        try:
            return cast(float, x) in self.interval
        except TypeError:
            return False

    def range(self, nb: Union[int, None] = None) -> List:
        """Return range of value from scale.

        :param nb: number of values to return
        :return:
        """
        nb = 2 if nb is None else nb
        return cast(
            List,
            np.linspace(self.interval.dmin, self.interval.dmax, nb).tolist(),
        )

    def value(self, x: Any) -> float:
        """Return corresponding numeric value.

        :param x:
        :return:
        :raise ValueError: if `x` is outside scale
        """
        if x not in self:
            raise ValueError(f"value outside scale: {x}")
        return cast(float, x)

    def label(self, x: float) -> Any:
        """Return scale value corresponding to given number.

        :param x:
        :return:
        :raise ValueError: if `x` is outside scale
        """
        if x not in self:
            raise ValueError(f"value outside scale: {x}")
        return x

    @classmethod
    def fit(
        cls,
        data: Series,
        preference_direction: Union[PreferenceDirection, None] = None,
        **kwargs,
    ) -> Self:
        """Create a scale that fits the data.

        :param data:
        :param preference_direction:
        :return: scale
        :raise TypeError: if `data` is not numeric
        """
        if not is_numeric_dtype(data):
            raise TypeError(f"{cls} can only fit numeric data")
        return cls(
            data.min(), data.max(), preference_direction=preference_direction
        )


NormalScale = QuantitativeScale
"""Type alias for normal scale"""


@set_module("mcda.scales")
class DiscreteQuantitativeScale(QuantitativeScale):
    """Class for discrete quantitative scale.

    :param values: numeric values that constitute the scale
    :param preference_direction:
    """

    def __init__(
        self,
        values: List[float],
        preference_direction: Union[PreferenceDirection, None] = None,
        **kwargs,
    ):
        self.values = sorted(set(values))
        super().__init__(
            min(self.values),
            max(self.values),
            preference_direction=preference_direction,
            **kwargs,
        )

    @staticmethod
    def binary() -> BinaryScale:
        """Return binary scale.

        :return:
        """
        return DiscreteQuantitativeScale([0, 1])

    def __repr__(self) -> str:  # pragma: nocover
        """Return string representation of scale.

        :return:
        """
        if self.preference_direction:
            return (
                f"{self.__class__.__name__}(values={self.values}, "
                f"preference_direction={self.preference_direction})"
            )
        return f"{self.__class__.__name__}(values={self.values})"

    def __eq__(self, other) -> bool:
        """Test equality of quantitative scales.

        Equality is defined as being the same scale types, having the same
        :attr:`values`.

        :param other:
        :return:
        """
        if not isinstance(other, DiscreteQuantitativeScale):
            return False
        _scale = cast(DiscreteQuantitativeScale, other)
        if self.preference_direction != _scale.preference_direction:
            return False
        return self.values == _scale.values

    def __contains__(self, x: Any) -> bool:
        """Check if values are inside scale.

        :param x:
        :return:
        """
        return cast(float, x) in self.values

    def range(self, nb: Union[int, None] = None) -> List:
        """Return range of value from scale.

        :param nb: number of values to return
        :return:
        """
        return cast(List, self.values)

    @classmethod
    def fit(
        cls,
        data: Series,
        preference_direction: Union[PreferenceDirection, None] = None,
        **kwargs,
    ) -> Self:
        """Create a scale that fits the data.

        :param data:
        :param preference_direction:
        :return: scale
        :raise TypeError: if `data` is not numeric
        """
        if not is_numeric_dtype(data):
            raise TypeError(f"{cls} can only fit numeric data")
        return cls(
            data.unique().tolist(), preference_direction=preference_direction
        )


BinaryScale = DiscreteQuantitativeScale
"""Type alias for binary scale"""


@set_module("mcda.scales")
class QualitativeScale(OrdinalScale, NominalScale):
    """This class implements a MCDA qualitative scale.

    :param values: numeric series with labels as index
    :param preference_direction:
    :raises TypeError:
        * if `values` contains non-numeric values

    .. warning::
        This scale contains `labels` not `values`. `values` are only here to
        define a corresponding quantitative scale for default scale
        transformation. After calling :meth:`transform_to` with no associated
        scale, the data is no longer considered inside the qualitative scale.
    """

    def __init__(
        self,
        values: Series,
        preference_direction: Union[PreferenceDirection, None] = None,
        **kwargs,
    ):
        values = Series(values)
        if not is_numeric_dtype(values):
            raise TypeError("QualitativeScale must have numeric values")
        self.values = values
        self._quantitative: QuantitativeScale = DiscreteQuantitativeScale(
            self.values.tolist(), preference_direction=preference_direction
        )
        super().__init__(
            labels=self.values.index.tolist(),
            preference_direction=preference_direction,
            **kwargs,
        )

    @property
    def numeric(self) -> QuantitativeScale:
        """Return corresponding numeric scale."""
        return self._quantitative

    def __repr__(self) -> str:  # pragma: nocover
        """Return string representation of interval.

        :return:
        """
        if self.preference_direction:
            return (
                f"{self.__class__.__name__}(values={dict(self.values)}, "
                f"preference_direction={self.preference_direction})"
            )
        return f"{self.__class__.__name__}(values={dict(self.values)})"

    def __eq__(self, other) -> bool:
        """Test equality of qualitative scales.

        Equality is defined as having the same types, having the same set of
        :attr`labels` and corresponding :attr:`values`, and having the same
        interval.

        :param other:
        :return:
        """
        if type(other) != type(self):
            return False
        _scale = cast(QualitativeScale, other)
        if self.preference_direction != _scale.preference_direction:
            return False
        if dict(self.values) == dict(_scale.values):
            return True
        return False

    @property
    def interval(self) -> Interval:
        """Return interval on which scale is defined."""
        return self._quantitative.interval

    def label(self, x: float) -> Any:
        """Return label corresponding to given number.

        :param x:
        :raises ValueError: if `x` corresponds to no label
        :return:
        """
        if x not in self.values.values:
            raise ValueError(f"value outside scale: {x}")
        return self.values[self.values == x].index[0]

    def value(self, x: Any) -> float:
        """Return corresponding numeric value.

        :param x:
        :return:
        """
        if x not in self:
            raise ValueError(f"value outside scale: {x}")
        return cast(float, self.values[x])

    @classmethod
    def fit(
        cls,
        data: Series,
        preference_direction: Union[PreferenceDirection, None] = None,
        **kwargs,
    ) -> Self:
        """Create a scale that fits the data.

        :param data:
        :param preference_direction:
        :return: scale
        """
        uniques = data.unique()
        return cls(
            Series(list(range(len(uniques))), index=uniques),
            preference_direction,
        )


@set_module("mcda.scales")
class FuzzyScale(QualitativeScale):
    """This class implements a MCDA fuzzy qualitative scale.

    :param fuzzy:
    :param preference_direction:
    :param defuzzify_method:
    :raises TypeError:
        * if `fuzzy` contains non-fuzzy numbers
    """

    def __init__(
        self,
        fuzzy: Series,
        preference_direction: Union[PreferenceDirection, None] = None,
        defuzzify_method: str = "centre_of_gravity",
        **kwargs,
    ):
        fuzzy = Series(fuzzy)
        dmin, dmax = float("inf"), -float("inf")
        for fz in fuzzy.values:
            if type(fz) is not FuzzyNumber:
                raise TypeError("fuzzy scales can only contains fuzzy numbers")
            dmin = min(min(fz.abscissa), dmin)
            dmax = max(max(fz.abscissa), dmax)
        self.fuzzy = fuzzy
        self.defuzzify_method = defuzzify_method
        super().__init__(
            values=self.defuzzify(),
            preference_direction=preference_direction,
            **kwargs,
        )
        self._quantitative = QuantitativeScale(
            dmin, dmax, preference_direction=preference_direction
        )

    def __eq__(self, other) -> bool:
        """Test equality of fuzzy scales.

        Equality is defined as having the same types, having the same set of
        :attr`labels` and corresponding :attr:`fuzzy`, and having the same
        interval.

        :param other:
        :return:
        """
        if type(other) != type(self):
            return False
        _scale = cast(FuzzyScale, other)
        if not QualitativeScale.__eq__(self, _scale):
            return False
        for k, f in zip(self.labels, self.fuzzy):
            if f != _scale.fuzzy[k]:
                return False
        return True

    def __repr__(self) -> str:  # pragma: nocover
        """Return string representation of interval.

        :return:
        """
        if self.preference_direction:
            return (
                f"{self.__class__.__name__}(fuzzy={dict(self.fuzzy)}, "
                f"preference_direction={self.preference_direction})"
            )
        return f"{self.__class__.__name__}(values={self.values})"

    def defuzzify(self, method: Union[str, None] = None) -> Series:
        """Defuzzify all fuzzy numbers using given method.

        :param method:
            method used to defuzzify
            (from :class:`mcda.core.functions.FuzzyNumber` numeric methods)
        """
        method = self.defuzzify_method if method is None else method
        return self.fuzzy.apply(lambda x, m=method: getattr(x, m))

    @property
    def is_fuzzy_partition(self) -> bool:
        """Test whether the scale define a fuzzy partition.

        :return:
        """
        indexes = self.values.sort_values().index
        fuzzy_sets = [self.fuzzy[i] for i in indexes]
        for i in range(len(fuzzy_sets) - 1):
            for j in range(2):
                if (
                    fuzzy_sets[i].abscissa[j + 2]
                    != fuzzy_sets[i + 1].abscissa[j]
                ):
                    return False
        return True

    def similarity(self, fuzzy1: FuzzyNumber, fuzzy2: FuzzyNumber) -> float:
        """Returns similarity between both fuzzy numbers w.r.t this scale.

        :param fuzzy1:
        :param fuzzy2:
        :return:

        .. note:: implementation based on :cite:p:`isern2010ulowa`
        """
        a = [self.interval.normalize(v) for v in fuzzy1.abscissa]
        b = [self.interval.normalize(v) for v in fuzzy2.abscissa]
        res = [2 - abs(aa - bb) for aa, bb in zip(a, b)]
        prod = 1.0
        for r in res:
            prod *= r
        return prod ** (1 / 4) - 1

    def fuzziness(self, fuzzy: FuzzyNumber) -> float:
        """Returns the fuzziness of given fuzzy number w.r.t this scale.

        :param fuzzy:
        :return:
        """
        return self.interval.normalize(
            (
                fuzzy.abscissa[1]
                + fuzzy.abscissa[3]
                - fuzzy.abscissa[0]
                - fuzzy.abscissa[2]
            )
            / 2,
        )

    def specificity(self, fuzzy: FuzzyNumber) -> float:
        """Returns the specificity of given fuzzy number w.r.t this scale.

        :param fuzzy:
        :return:

        .. todo::
            check whether normalization should be done before computing area
        """
        return 1 - self.interval.normalize(fuzzy.area)

    def ordinal_distance(self, a: Any, b: Any) -> float:
        """Returns the ordinal distance between the labels
        (sorted by defuzzified values).

        :param a:
        :param b:
        :return:
        :raises ValueError: if `a` or `b` is not inside the scale
        """
        if a not in self or b not in self:
            raise ValueError("both labels must be inside the fuzzy scale")
        labels = self.values.sort_values().index.tolist()
        return abs(labels.index(a) - labels.index(b))

    def label(self, x: float) -> Any:
        """Return label associated to given number.

        :param x:
        :raises ValueError: if `x` corresponds to no label
        :return: most probable label associated to given value
        """

        confidences = self.fuzzy.apply(lambda f, xx=x: f(xx))
        confidences.sort_values(ascending=False)

        if confidences.iloc[0] <= 0:
            raise ValueError(f"value outside scale: {x}")
        return confidences.index.tolist()[0]

    @classmethod
    def fit(
        cls,
        data: Series,
        preference_direction: PreferenceDirection | None = None,
        **kwargs,
    ) -> Self:
        """Create a scale that fits the data.

        :param data:
        :param preference_direction:
        :return: scale
        """
        uniques = data.unique()
        points = np.linspace(0, 1, num=2 * len(uniques) + 2)
        fuzzys = []
        for i, _ in enumerate(uniques):
            fuzzys.append(FuzzyNumber(points[2 * i : 2 * i + 4].tolist()))
        return cls(Series(fuzzys, index=uniques), preference_direction)


S = TypeVar("S", bound=Scale, covariant=True)


def common_scale_type(scale_types: List[Type[S]]) -> Type[S]:
    """Determine common type between scale types.

    :param scale_types:
    :return: common scale type
    """
    stype = scale_types[0] if len(scale_types) > 0 else cast(S, Scale)
    for s in scale_types[1:]:
        while not issubclass(s, stype):
            # This works as intended if scale classes declare deepest
            # parent class first (otherwise it will use too basic classes)
            stype = stype.__base__
    return stype
