"""This module gathers aggregators
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from math import log
from typing import (
    Any,
    Dict,
    Generic,
    List,
    Mapping,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from deprecated.sphinx import versionadded
from numpy.linalg import norm
from pandas import DataFrame, Series

from ..core.aliases import Function
from ..core.criteria_functions import CriteriaFunctions, CriterionFunction
from ..core.functions import FuzzyNumber
from ..core.matrices import (
    AdditivePerformanceTable,
    AdjacencyValueMatrix,
    IValueMatrix,
    PartialValueMatrix,
    PerformanceTable,
)
from ..core.scales import (
    FuzzyScale,
    NormalScale,
    OrdinalScale,
    QuantitativeScale,
    Scale,
    common_scale_type,
)
from ..core.set_functions import ISetFunction, Mobius
from ..core.values import CommensurableValues, Values
from .compatibility import dataframe_map
from .utils import set_module

I_S = TypeVar("I_S", bound=Scale, covariant=True)
O_S = TypeVar("O_S", bound=Scale, covariant=True)
I_OS = TypeVar("I_OS", bound=OrdinalScale, covariant=True)


@versionadded("a more generic aggregator as common parent class", "1.1.0")
class BaseAggregator(Generic[I_S, O_S], ABC):
    """This abstract class represents a basic aggregator.

    :param in_scales: input scales (inferred from input if not provided)
    :param out_scale: output scales (inferred from output if not provided)
    :param in_stype: input stype (inferred from input if not provided)
    :param out_stype: output stype (inferred from output if not provided)
    :raise TypeError:
        * if `in_scales` is not consistent with `in_stype` (and both are set)
        * if `out_scale` is not an instance of `out_stype` (and both are set)

    .. note::
        :attr:`out_scale` is only used as the scale for
        returned aggregation results.
    .. warning::
        :attr:`in_scales` is only declarative, and not used
        for checking/transforming data.
    """

    def __init__(
        self,
        in_scales: Union[I_S, Mapping[Any, I_S], None] = None,
        out_scale: Union[O_S, None] = None,
        in_stype: Union[Type[I_S], None] = None,
        out_stype: Union[Type[O_S], None] = None,
    ):
        if in_stype:
            if isinstance(in_scales, Mapping):
                if len(in_scales) > 0 and not issubclass(
                    common_scale_type(
                        [cast(Type[I_S], type(s)) for s in in_scales.values()]
                    ),
                    in_stype,
                ):
                    raise TypeError("input stype and scale are not compatible")
            elif in_scales is not None and not isinstance(
                cast(I_S, in_scales), in_stype
            ):
                raise TypeError("input stype and scale are not compatible")
        if out_stype and out_scale and not isinstance(out_scale, out_stype):
            raise TypeError("output stype and scale are not compatible")
        self.in_stype = in_stype
        self.out_stype = out_stype
        self.in_scales: Union[I_S, Mapping[Any, I_S], None] = in_scales
        self.out_scale = out_scale

    def within_in_scales(self, data: IValueMatrix[I_S]) -> bool:
        """Check potential input is inside input scales.

        :param data:
        :return: ``True`` if `data` is within :attr:`in_scales`
        """
        m = PerformanceTable(
            data.data, scales=self.in_scales, stype=self.in_stype
        )
        return m.is_within_scales

    @abstractmethod
    def __call__(
        self, data: IValueMatrix[I_S], *args, **kwargs
    ) -> CommensurableValues[O_S]:  # pragma: nocover
        """Apply aggregation method to input data.

        :param data:
        :return: aggregation result

        .. note:: aggregation is applied for each row in case of tabular data
        """
        pass


class Aggregator(BaseAggregator[I_S, O_S], ABC):
    """This abstract class represents a typical aggregator.

    :param in_scales: input scales (inferred from input if not provided)
    :param out_scale: output scales (inferred from output if not provided)
    :param in_stype: input stype (inferred from input if not provided)
    :param out_stype: output stype (inferred from output if not provided)
    :raise TypeError:
        * if `in_scales` is not consistent with `in_stype` (and both are set)
        * if `out_scale` is not an instance of `out_stype` (and both are set)

    .. note::
        For all subclasses, :attr:`out_scale` is only used as the scale for
        returned aggregation results.
    .. warning::
        For all subclasses, :attr:`in_scales` is only declarative, and not use
        for checking/transforming data.
    """

    def within_in_scales(
        self,
        data: Union[
            Series,
            Values[I_S],
            DataFrame,
            IValueMatrix[I_S],
            PartialValueMatrix[I_S],
        ],
    ) -> bool:
        """Check potential input is inside input scales.

        :param data:
        :return: ``True`` if `data` is within :attr:`in_scales`
        """
        if isinstance(data, Series):
            v = Values(data, scales=self.in_scales, stype=self.in_stype)
            return v.is_within_scales
        if isinstance(data, Values):
            v = Values(data.data, scales=self.in_scales, stype=self.in_stype)
            return v.is_within_scales
        if isinstance(data, DataFrame):
            m = PerformanceTable(
                data, scales=self.in_scales, stype=self.in_stype
            )
            return m.is_within_scales
        if isinstance(data, PartialValueMatrix):
            return PartialValueMatrix(
                data.data, scales=self.in_scales, stype=self.in_stype
            ).is_within_scales
        return super().within_in_scales(cast(IValueMatrix[I_S], data))

    @abstractmethod
    def _aggregate_series(
        self, series: Series, *args, **kwargs
    ) -> Any:  # pragma: nocover
        """Apply aggregation method to a pandas Series.

        :param series:
        """
        pass

    def _aggregate_values(self, values: Values[I_S], *args, **kwargs) -> Any:
        """Apply aggregation method to a values object.

        :param values:
        """
        return self._aggregate_series(values.data)

    def _aggregate_dataframe(self, df: DataFrame, *args, **kwargs) -> Series:
        """Apply aggregation method to a pandas DataFrame.

        :param df:
        :return: aggregated rows
        """
        return Series(
            {
                alternative: self._aggregate_series(
                    df.loc[alternative], *args, **kwargs
                )
                for alternative in df.index.tolist()
            }
        )

    def _aggregate_value_matrix(
        self, matrix: IValueMatrix[I_S], *args, **kwargs
    ) -> CommensurableValues[O_S]:
        """Apply aggregation method to a value matrix object.

        :param matrix:
        :return: aggregated criteria values per alternative
        """
        return CommensurableValues(
            self._aggregate_dataframe(matrix.data, *args, **kwargs),
            scale=self.out_scale,
            stype=self.out_stype,
        )

    def _aggregate_partial_values(
        self, partial_values: PartialValueMatrix[I_S], *args, **kwargs
    ) -> AdjacencyValueMatrix[O_S]:
        """Apply aggregation method to each cell of a partial values matrix.

        :param partial_values:
        :return: aggregated partial values for each cell
        """
        return AdjacencyValueMatrix(
            dataframe_map(partial_values.data, self._aggregate_series),
            scale=self.out_scale,
            stype=self.out_stype,
        )

    @overload
    def __call__(
        self, data: Series, *args, **kwargs
    ) -> Any:  # pragma: nocover
        ...

    @overload
    def __call__(
        self, data: Values[I_S], *args, **kwargs
    ) -> Any:  # pragma: nocover
        ...

    @overload
    def __call__(
        self, data: DataFrame, *args, **kwargs
    ) -> Series:  # pragma: nocover
        ...

    @overload
    def __call__(
        self, data: IValueMatrix[I_S], *args, **kwargs
    ) -> CommensurableValues[O_S]:  # pragma: nocover
        ...

    @overload
    def __call__(
        self, data: PartialValueMatrix[I_S], *args, **kwargs
    ) -> AdjacencyValueMatrix[O_S]:  # pragma: nocover
        ...

    def __call__(
        self,
        data: Union[
            PartialValueMatrix[I_S],
            IValueMatrix[I_S],
            DataFrame,
            Series,
            Values[I_S],
        ],
        *args,
        **kwargs,
    ) -> Union[
        Any, Series, CommensurableValues[O_S], AdjacencyValueMatrix[O_S]
    ]:
        """Apply aggregation method to input data.

        :param data:
        :return: aggregation result

        .. note:: aggregation is applied for each row in case of tabular data
        """
        if isinstance(data, PartialValueMatrix):
            return self._aggregate_partial_values(data, *args, **kwargs)
        if isinstance(data, IValueMatrix):
            return self._aggregate_value_matrix(data, *args, **kwargs)
        if isinstance(data, DataFrame):
            return self._aggregate_dataframe(data, *args, **kwargs)
        if isinstance(data, Values):
            return self._aggregate_values(data, *args, **kwargs)
        return self._aggregate_series(data, *args, **kwargs)


@set_module("mcda.mavt.aggregators")
class Sum(Aggregator[QuantitativeScale, QuantitativeScale]):
    """This class represents a simple sum aggregator.

    :param in_scales: input scales (inferred from input if not provided)
    :param out_scale: output scales (inferred from output if not provided)
    """

    def _aggregate_series(self, series: Series, *args, **kwargs) -> float:
        """Return weighted sum of the input.

        :param series:
        :return:
        """
        return series.sum()


@set_module("mcda.mavt.aggregators")
class WeightedSum(Sum):
    """This class represents a weighted sum aggregator.

    :param criteria_weights:
    :param in_scales: input scales (inferred from input if not provided)
    :param out_scale: output scales (inferred from output if not provided)

    :attr weight_function: functions applying weights without aggregation
    """

    def __init__(
        self,
        criteria_weights: Union[Dict[Any, float], Series],
        in_scales: Union[
            QuantitativeScale, Mapping[Any, QuantitativeScale], None
        ] = None,
        out_scale: Union[QuantitativeScale, None] = None,
    ):
        self.criteria_weights = Series(criteria_weights)
        super().__init__(
            in_scales=in_scales,
            out_scale=out_scale,
            in_stype=QuantitativeScale,
            out_stype=QuantitativeScale,
        )
        self.weight_functions = CriteriaFunctions(
            {
                c: cast(
                    Function, lambda v, crit=c: self.criteria_weights[crit] * v
                )
                for c in self.criteria_weights.keys()
            },
            self.in_scales,
            self.out_scale,
            QuantitativeScale,
            QuantitativeScale,
        )

    def _aggregate_series(self, series: Series, *args, **kwargs) -> float:
        """Return weighted sum of the input.

        :param series:
        :return:
        """
        return super()._aggregate_series(series * self.criteria_weights)


@set_module("mcda.mavt.aggregators")
class NormalizedWeightedSum(WeightedSum):
    """This class represents a normalized weighted sum aggregator.

    :param criteria_weights:
    :param in_scales: input scales (inferred from input if not provided)
    :param out_scale: output scales (inferred from output if not provided)

    :attr weight_function: functions applying weights without aggregation
    """

    def _aggregate_series(self, series: Series, *args, **kwargs) -> float:
        return (
            super()._aggregate_series(series, *args, **kwargs)
            / self.criteria_weights.sum()
        )


@set_module("mcda.mavt.aggregators")
class ChoquetIntegral(Aggregator[QuantitativeScale, QuantitativeScale]):
    """This class represents a Choquet integral aggregator.

    :param capacity:
        capacity used for aggregation (either in regular or Möbius
        representation)
    :param in_scales: input scales (inferred from input if not provided)
    :param out_scale: output scales (inferred from output if not provided)

    .. note:: Implementation is based on :cite:p:`grabisch2008review`.
    """

    def __init__(
        self,
        capacity: ISetFunction,
        in_scales: Union[
            QuantitativeScale, Mapping[Any, QuantitativeScale], None
        ] = None,
        out_scale: Union[QuantitativeScale, None] = None,
    ):
        self.capacity = capacity.as_capacity
        super().__init__(
            in_scales=in_scales,
            out_scale=out_scale,
            in_stype=QuantitativeScale,
            out_stype=QuantitativeScale,
        )

    def _choquet_integral_capacity(self, series: Series) -> float:
        """Return Choquet integral using a capacity.

        :param series:
        :return:

        .. note:: Implementation is based on :cite:p:`grabisch2008review`.
        """
        res = series.sort_values()
        criteria = res.index.tolist()
        return sum(
            res[criterion]
            * (
                self.capacity(*criteria[i:])
                - self.capacity(*criteria[(i + 1) :])
            )
            for i, criterion in enumerate(criteria)
        )

    def _choquet_integral_mobius(self, series: Series) -> float:
        """Return Choquet integral using a möbius.

        :param series:
        :return:

        .. note:: Implementation is based on :cite:p:`grabisch2008review`.
        """
        return sum(
            m * series[list(t)].min()
            for t, m in self.capacity.values.items()
            if len(t) > 0
        )

    def _aggregate_series(self, series: Series, *args, **kwargs) -> float:
        """Return Choquet integral of the pandas Series.

        :param series:
        :return:
        """
        if isinstance(self.capacity, Mobius):
            return self._choquet_integral_mobius(series)
        return self._choquet_integral_capacity(series)


@set_module("mcda.mavt.aggregators")
class OWA(Aggregator[QuantitativeScale, QuantitativeScale]):
    """This class represents an Ordered Weighted Aggregator (OWA).

    :param weights:
    :param in_scales: input scales (inferred from input if not provided)
    :param out_scale: output scales (inferred from output if not provided)

    .. note:: Implementation is based on :cite:p:`grabisch2008review`.
    """

    def __init__(
        self,
        weights: List[float],
        in_scales: Union[
            QuantitativeScale, Mapping[Any, QuantitativeScale], None
        ] = None,
        out_scale: Union[QuantitativeScale, None] = None,
    ):
        self.weights = weights
        super().__init__(
            in_scales=in_scales,
            out_scale=out_scale,
            in_stype=QuantitativeScale,
            out_stype=QuantitativeScale,
        )

    @property
    def orness(self) -> float:
        """Return *orness* measure of OWA weights.

        :return:

        .. note:: *orness* as defined in :cite:p:`yager1988owa`
        """
        return sum(
            (len(self.weights) - i - 1) * w for i, w in enumerate(self.weights)
        ) / (len(self.weights) - 1)

    @property
    def andness(self) -> float:
        """Return *andness* measure of OWA weights.

        :return:

        .. note:: *andness* as defined in :cite:p:`yager1988owa`
        """
        return 1 - self.orness

    @property
    def dispersion(self) -> float:
        """Return OWA weights dispersion (also called entropy).

        :return:

        .. note:: dispersion as defined in :cite:p:`yager1988owa`
        """
        return -sum(w * log(w) if w > 0 else 0 for w in self.weights)

    @property
    def divergence(self) -> float:
        """Return OWA weights divergence.

        :return:

        .. note:: divergence as defined in :cite:p:`yager2002heavy`
        """
        addition = 0.0
        j = 1
        n = len(self.weights)
        orness = self.orness
        for w in self.weights:
            operation = (((n - j) / (n - 1)) - orness) ** 2
            j = j + 1
            addition = addition + w * operation
        return addition

    @property
    def balance(self) -> float:
        """Return OWA weights balance.

        :return:

        .. note:: balance as defined in :cite:p:`yager1996constrainedowa`
        """
        addition = 0.0
        j = 1
        n = len(self.weights)
        for w in self.weights:
            operation = (n + 1 - 2 * j) / (n - 1)
            j = j + 1
            addition = addition + w * operation
        return addition

    @property
    def quantifier(self) -> List[float]:
        """Return quantifier corresponding to OWA weights.

        :return:

        .. note:: quantifier as defined in :cite:p:`yager1988owa`
        """
        return [
            sum(w for w in self.weights[:i])
            for i in range(len(self.weights) + 1)
        ]

    def _aggregate_series(self, series: Series, *args, **kwargs) -> float:
        """Return Ordered Weighted Aggregation of values.

        :param series:
        :return:

        .. note:: Implementation is based on :cite:p:`yager1988owa`
        """
        return (series.sort_values(ascending=False) * self.weights).sum()

    @classmethod
    def from_quantifier(cls, quantifier: List[float]) -> "OWA":
        """Return OWA aggregator corresponding to given quantifier.

        :param quantifier:
        :return:

        .. note:: quantifier as defined in :cite:p:`yager1988owa`
        """
        return cls(
            [q - q_1 for q, q_1 in zip(quantifier[1:], quantifier[:-1])]
        )

    @classmethod
    def and_aggregator(cls, size: int) -> "OWA":
        """Return *and* OWA aggregator of given weights size.

        :param size:
        :return:

        .. note:: :math:`W_*` as defined in :cite:p:`yager1988owa`
        """
        return cls(cast(List[float], [0] * (size - 1) + [1]))

    @classmethod
    def or_aggregator(cls, size: int) -> "OWA":
        """Return *or* OWA aggregator of given weights size.

        :param size:
        :return:

        .. note:: :math:`W^*` as defined in :cite:p:`yager1988owa`
        """
        return cls(cast(List[float], [1] + [0] * (size - 1)))


@set_module("mcda.mavt.aggregators")
class ULOWA(Aggregator[FuzzyScale, FuzzyScale]):
    """This class represents an Unbalanced Linguistic Weighted Average (ULOWA)
    aggregator.

    :param weights:
    :param scale: fuzzy scale used for the average

    .. note:: implementation based on :cite:p:`isern2010ulowa`
    """

    def __init__(self, weights: List[float], scale: FuzzyScale):
        self.scale = scale
        self.weights = weights
        super().__init__(
            in_scales=scale,
            out_scale=scale,
            in_stype=FuzzyScale,
            out_stype=FuzzyScale,
        )

    def delta(self, a: Any, b: Any, weight: float) -> float:
        """Returns ULOWA delta value.

        :param a: worst value
        :param b: best value
        :param weight: ULOWA weight
        :return:
        """
        xa = self.scale.value(a)
        xb = self.scale.value(b)
        return xa + weight * (xb - xa)

    def most_similar(self, a: Any, b: Any, ref_fuzzy: FuzzyNumber) -> Any:
        """Returns label which fuzzy number is the most similar to the
        reference (between `a` and `b` labels).

        :param a:
        :param b:
        :param ref_fuzzy: fuzzy number that is being compared to
        :return:
        """
        if self.scale.ordinal_distance(a, b) == 1:
            _labels = [a, b]
        else:
            _labels = sorted(
                self.scale.labels,
                key=lambda v: self.scale.value(v),
                reverse=True,
            )
            lmin = min(_labels.index(a), _labels.index(b))
            lmax = max(_labels.index(a), _labels.index(b))
            _labels = _labels[lmin : lmax + 1]
        sims = [
            self.scale.similarity(self.scale.fuzzy[v], ref_fuzzy)
            for v in _labels
        ]
        return _labels[max(range(len(_labels)), key=lambda i: sims[i])]

    def _aggregate_series(
        self, series: Series, *args, weights=None, **kwargs
    ) -> Any:
        """Returns Unbalanced Linguistic Weighted Average of values.

        :param values:
        :param weights:
        :return:
        :raise ValueError: if `values` contains less than 2 items

        .. note:: implementation based on :cite:p:`isern2010ulowa`

        .. warning::
            this function is intended for use with a fuzzy scale defining a
            fuzzy partition
        """

        if len(series) == 0:
            raise ValueError("ULOWA needs at least one value")
        if len(series) == 1:
            return series.iloc[0]
        values = CommensurableValues(series, self.scale).sort().data.values
        weights = self.weights.copy() if weights is None else weights
        denominator = weights[-2] + weights[-1]
        weight = 0 if denominator == 0 else weights[-2] / denominator
        delta = self.delta(values[-1], values[-2], weight)
        values[-2] = self.most_similar(
            values[-1], values[-2], FuzzyNumber([delta] * 4)
        )
        weights[-2] += weights[-1]
        return self._aggregate_series(
            Series(values[:-1]), weights=weights[:-1]
        )


@set_module("mcda.functions")
class AdditiveValueFunctions(CriteriaFunctions[I_S, QuantitativeScale]):
    """This class represents multi-attribute additive value functions.

    :param functions: either :class:`CriterionFunction` or functions
    :param in_scales:
        input scales (ignored if :class:`CriterionFunction` supplied)
    :param out_scales:
        output scales (ignored if :class:`CriterionFunction` supplied)
    :param aggregator_scale:
        scale of aggregated results (inferred if not provided)
    :param in_stype:
    :raise TypeError:
        * if `in_stype` is not consistent with at least one criterion function
        * if `out_stype` is not consistent with at least one criterion function

    .. note::
        `functions` are defined for the provided scales, so when
        applying functions you must provide correctly scaled values
    """

    def __init__(
        self,
        functions: Mapping[
            Any, CriterionFunction[I_S, QuantitativeScale] | Function
        ],
        in_scales: Mapping[Any, I_S] | I_S | None = None,
        out_scales: Mapping[Any, QuantitativeScale]
        | QuantitativeScale
        | None = None,
        aggregator_scale: Union[QuantitativeScale, None] = None,
        in_stype: Type[I_S] | None = None,
        **kwargs,
    ):
        super().__init__(
            functions=functions,
            in_scales=in_scales,
            out_scales=out_scales,
            in_stype=in_stype,
            out_stype=QuantitativeScale,
            **kwargs,
        )
        self.aggregator_scale = aggregator_scale
        self._aggregator = Sum(
            in_scales=self.out_scales,
            out_scale=self.aggregator_scale,
            in_stype=self.out_stype,
            out_stype=QuantitativeScale,
        )

    def _apply_performance_table(
        self, performance_table: PerformanceTable[I_S]
    ) -> AdditivePerformanceTable:
        """Apply each scale function to its corresponding column.

        :param performance_table:
        :return: resulting performance table

        .. note::
            This method is called when calling object as a function with a
            :class:`PerformanceTable` input.
        """
        return AdditivePerformanceTable(
            self._apply_dataframe(performance_table.data),
            scales=self.out_scales,
            stype=self.out_stype,
            aggregated_scale=self.aggregator_scale,
        )

    @overload
    def aggregate(
        self, data: Series, *args, **kwargs
    ) -> Any:  # pragma: nocover
        ...

    @overload
    def aggregate(
        self, data: Values[QuantitativeScale], *args, **kwargs
    ) -> Any:  # pragma: nocover
        ...

    @overload
    def aggregate(
        self, data: DataFrame, *args, **kwargs
    ) -> Series:  # pragma: nocover
        ...

    @overload
    def aggregate(
        self, data: IValueMatrix[QuantitativeScale], *args, **kwargs
    ) -> CommensurableValues[QuantitativeScale]:  # pragma: nocover
        ...

    @overload
    def aggregate(
        self, data: PartialValueMatrix[QuantitativeScale], *args, **kwargs
    ) -> AdjacencyValueMatrix[QuantitativeScale]:  # pragma: nocover
        ...

    def aggregate(
        self,
        data: Union[
            PartialValueMatrix[QuantitativeScale],
            IValueMatrix[QuantitativeScale],
            DataFrame,
            Series,
            Values[QuantitativeScale],
        ],
        *args,
        **kwargs,
    ) -> Union[
        Any,
        Series,
        CommensurableValues[QuantitativeScale],
        AdjacencyValueMatrix[QuantitativeScale],
    ]:
        """Apply aggregation method to input data.

        :param data:
        :return: aggregation result

        .. note:: aggregation is applied for each row in case of tabular data
        """
        return self._aggregator(data, *args, **kwargs)


@set_module("mcda.mavt.aggregators")
@versionadded(version="1.1.0")
class TOPSIS(BaseAggregator[QuantitativeScale, NormalScale]):
    """
    This class implements the TOPSIS algorithm.

    (Technique for Order of Preference by Similarity to Ideal Solution).

    It gives a score to alternatives based on comparison with
    ideal positive and negative values.

    :param criteria_weights:
        weights applied to each criteria, are normalized internally before
        applying the algorithm.

    .. note:: Implementation is based on :cite:p:`chakraborty2022topsis`.

    **Example**

    First you need to create or import ordinal data, and make them
    quantitative:

    >>> from mcda import PerformanceTable
    >>> from mcda.scales import (QuantitativeScale, QualitativeScale,
    ... PreferenceDirection)
    >>> data = [
    ...    [9500, 4.2, "**", "blue", 450],
    ...    [15600, 4.5, "****", "black", 900],
    ...    [6800, 4.1, "***", "grey", 700],
    ...    [10200, 5.6, "****", "black", 850],
    ...    [8100, 5.2, "***", "red", 750],
    ...    [12000, 4.9, "****", "grey", 850]
    ... ]
    >>> alternatives = ["Fiat 500", "Peugeot 309", "Renault Clio",
    ... "Opel Astra", "Honda Civic", "Toyota Corolla"]
    >>> criteria = ["cost", "fuel consumption", "comfort", "color",
    ... "range"]
    >>> scale1 = QuantitativeScale(6000, 20000,
    ... preference_direction=PreferenceDirection.MIN)
    >>> scale2 = QuantitativeScale(4, 6,
    ... preference_direction=PreferenceDirection.MIN)
    >>> scale3 = QualitativeScale({"*": 1, "**": 2, "***": 3,
    ... "****": 4})
    >>> scale4 = QualitativeScale({"red": 1, "blue": 2, "black": 3,
    ... "grey": 4}, preference_direction=PreferenceDirection.MIN)
    >>> scale5 = QuantitativeScale(400, 1000)
    >>> scales = {
    ...    criteria[0]: scale1,
    ...    criteria[1]: scale2,
    ...    criteria[2]: scale3,
    ...    criteria[3]: scale4,
    ...    criteria[4]: scale5
    ... }
    >>> table = PerformanceTable(data, alternatives=alternatives,
    ... criteria=criteria, scales=scales)
    >>> numeric_table = table.to_numeric

    Then, you can setup the weights for TOPSIS and score each alternative:

    >>> from mcda.mavt.aggregators import TOPSIS
    >>> criteria_weights = {"cost": 3, "fuel consumption": 4, "comfort": 2,
    ... "color": 5, "range": 1}
    >>> topsis = TOPSIS(criteria_weights)
    >>> result = topsis(numeric_table).sort()
    >>> print(result.data)
    Honda Civic       0.823318
    Fiat 500          0.634897
    Opel Astra        0.413274
    Renault Clio      0.362293
    Peugeot 309       0.357782
    Toyota Corolla    0.249553
    dtype: float64
    """

    def __init__(
        self,
        criteria_weights: Union[Dict[Any, float], Series],
    ):
        super().__init__(
            out_scale=QuantitativeScale.normal(),
            in_stype=QuantitativeScale,
            out_stype=QuantitativeScale,
        )
        self.criteria_weights = criteria_weights

    @property
    def normalized_weights(self) -> Dict[Any, float]:
        """Normalized criteria weights"""
        total = Series(self.criteria_weights).sum()
        normalized_weights = {
            key: value / total for key, value in self.criteria_weights.items()
        }
        return normalized_weights

    @classmethod
    def normalize(
        self, matrix: IValueMatrix[QuantitativeScale]
    ) -> PerformanceTable[QuantitativeScale]:
        """Normalize performance table values.

        Norm used is the euclidean norm applied on each criterion values.

        :param matrix:
        :return: normalized table

        .. note:: input scales preference direction are preserved
        """
        normalization_vector = matrix.data.pow(2).sum(axis=0).pow(0.5)
        normalized_data = matrix.data.div(normalization_vector, axis=1)
        return PerformanceTable(
            normalized_data,
            scales={
                criterion: QuantitativeScale(
                    0, 1, preference_direction=scale.preference_direction
                )
                for criterion, scale in matrix.scales.items()
            },
        )

    def _apply_weights(
        self, matrix: IValueMatrix[QuantitativeScale]
    ) -> PerformanceTable[QuantitativeScale]:
        """Apply normalized criteria weights to performance table.

        :param matrix:
        :return: weighted performance table
        """
        weights_series = Series(self.normalized_weights)
        weighted_df = matrix.data.multiply(weights_series, axis=1)
        return PerformanceTable(weighted_df, scales=matrix.scales)

    @classmethod
    def positive_ideal_solution(
        cls, matrix: IValueMatrix[I_OS]
    ) -> Values[I_OS]:
        """Compute ideal positive solution.

        This fictive alternative corresponds to the best criterion value for
        every criterion.

        :param matrix:
        :return: ideal positive solution as an alternative value
        """
        best_values = []
        for criterion_values in matrix.columns_values.values():
            best = criterion_values.data.iloc[0]
            for val in criterion_values.data.values[1:]:
                best = (
                    val
                    if criterion_values.scale.is_better(val, best)
                    else best
                )
            best_values.append(best)
        return Values(
            Series(best_values, index=matrix.columns),
            scales=matrix.scales,
        )

    @classmethod
    def negative_ideal_solution(
        cls, matrix: IValueMatrix[I_OS]
    ) -> Values[I_OS]:
        """Compute ideal negative solution.

        This fictive alternative corresponds to the worst criterion value for
        every criterion.

        :param matrix:
        :return: ideal negative solution as an alternative value
        """
        worst_values = []
        for criterion_values in matrix.columns_values.values():
            worst = criterion_values.data.iloc[0]
            for val in criterion_values.data.values[1:]:
                worst = (
                    val
                    if criterion_values.scale.is_better(worst, val)
                    else worst
                )
            worst_values.append(worst)
        return Values(
            Series(worst_values, index=matrix.columns),
            scales=matrix.scales,
        )

    def __call__(
        self, data: IValueMatrix[QuantitativeScale], *args, **kwargs
    ) -> CommensurableValues[NormalScale]:
        """Apply TOPSIS aggregation method to input data.

        :param data:
        :return: aggregation result
        """
        _normalized = self.normalize(data)
        weighted = self._apply_weights(_normalized)
        posideal = self.positive_ideal_solution(weighted).data.to_numpy()
        negideal = self.negative_ideal_solution(weighted).data.to_numpy()

        weighted_normalized = weighted.data.to_numpy()

        positive_distance = norm(weighted_normalized - posideal, ord=2, axis=1)
        negative_distance = norm(weighted_normalized - negideal, ord=2, axis=1)

        denominator = positive_distance + negative_distance
        zero_loc = denominator == 0
        denominator[zero_loc] = 1  # Avoid division by zero

        result = negative_distance / denominator
        result[zero_loc] = 0  # Set result of zero for zero-denominator

        return CommensurableValues(
            Series(result, index=data.rows), scale=QuantitativeScale.normal()
        )
