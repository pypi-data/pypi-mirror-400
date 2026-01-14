"""This module gathers all classes and methods used to transform data to new
scales.
"""
from abc import ABC, abstractmethod
from typing import Any, Mapping, TypeVar, Union, cast, overload

from pandas import DataFrame, Series

from .compatibility import dataframe_map
from .matrices import (
    AdjacencyValueMatrix,
    PartialValueMatrix,
    PerformanceTable,
)
from .scales import (
    DiscreteQuantitativeScale,
    NormalScale,
    OrdinalScale,
    PreferenceDirection,
    QualitativeScale,
    QuantitativeScale,
    Scale,
)
from .utils import set_module
from .values import CommensurableValues, Values

S = TypeVar("S", bound=Scale)


class ITransformer(ABC):
    """This abstract class describes a generic transformer class."""

    @classmethod
    @abstractmethod
    def _transform_one(
        cls, x: Any, in_scale: Scale, out_scale: S
    ) -> Any:  # pragma: nocover
        """Transform a single value to a new scale.

        :param x: value to transform
        :param in_scale: value scale
        :param out_scale: output scale
        :return: transformed value

        .. note:: not intended for general usage
        """
        pass

    @classmethod
    @abstractmethod
    def _normalize_one(
        cls, x: Any, in_scale: Scale
    ) -> float:  # pragma: nocover
        """Normalize a single value given its scale.

        :param x: value to normalize
        :param in_scale: value scale
        :return: normalized value

        .. note:: not intended for general usage
        """
        pass

    @classmethod
    def _normalize_series(
        cls,
        series: Series,
        in_scales: Union[Scale, Mapping[Any, Scale]],
    ) -> Series:
        """Normalize each value of a series.

        :param series:
        :param in_scales: input scales
        :return: normalized series (new object)

        .. note:: not intended for general usage
        """
        in_scales = (
            {criterion: in_scales for criterion in series.index.tolist()}
            if isinstance(in_scales, Scale)
            else in_scales
        )
        return Series(
            {
                criterion: cls._normalize_one(value, in_scales[criterion])
                for criterion, value in series.items()
            },
            name=series.name,
        )

    @classmethod
    def _transform_series(
        cls,
        series: Series,
        in_scales: Union[Scale, Mapping[Any, Scale]],
        out_scales: Union[S, Mapping[Any, S]],
    ) -> Series:
        """Transform each value of a series to new scale.

        :param series:
        :param in_scales: input scales
        :param out_scales: output scales
        :return: transformed series (new object)

        .. note:: not intended for general usage
        """
        in_scales = (
            {criterion: in_scales for criterion in series.index.tolist()}
            if isinstance(in_scales, Scale)
            else in_scales
        )
        out_scales = (
            {
                criterion: cast(S, out_scales)
                for criterion in series.index.tolist()
            }
            if isinstance(out_scales, Scale)
            else out_scales
        )
        return Series(
            {
                criterion: cls._transform_one(
                    value, in_scales[criterion], out_scales[criterion]
                )
                for criterion, value in series.items()
            },
            name=series.name,
        )

    @classmethod
    def _normalize_values(cls, values: Values) -> Values[NormalScale]:
        """Normalize values.

        :param values:
        :return: normalized values (new object)

        .. note:: not intended for general usage
        """
        return values.__class__(
            cls._normalize_series(values.data, in_scales=values.scales),
            scales=QuantitativeScale.normal(),
        )

    @classmethod
    def _transform_values(
        cls,
        values: Values,
        out_scales: Union[S, Mapping[Any, S]],
    ) -> Values[S]:
        """Transform values to desired scales.

        :param values:
        :param out_scales: output scales
        :return: transformed values (new object)

        .. note:: not intended for general usage
        """
        return Values(
            cls._transform_series(
                values.data, in_scales=values.scales, out_scales=out_scales
            ),
            scales=out_scales,
        )

    @classmethod
    def _transform_criterion_values(
        cls, criterion_values: CommensurableValues, out_scale: S
    ) -> CommensurableValues[S]:
        """Transform criterion values to desired scale.

        :param criterion_values:
        :param out_scale: output scale
        :return: transformed criterion values

        .. note:: not intended for general usage
        """
        return CommensurableValues(
            cls._transform_series(
                criterion_values.data, criterion_values.scale, out_scale
            ),
            scale=out_scale,
        )

    @classmethod
    def _normalize_criterion_values(
        cls, criterion_values: CommensurableValues
    ) -> CommensurableValues[NormalScale]:
        """Normalize criterion values.

        :param criterion_values:
        :return: normalized criterion values

        .. note:: not intended for general usage
        """
        return CommensurableValues(
            cls._normalize_series(
                criterion_values.data, criterion_values.scale
            ),
            scale=QuantitativeScale.normal(),
        )

    @classmethod
    def _normalize_dataframe(
        cls,
        df: DataFrame,
        in_scales: Union[Scale, Mapping[Any, Scale]],
    ) -> DataFrame:
        """Normalize dataframe.

        :param df:
        :param in_scales: input scales
        :return: normalized dataframe (new object)

        .. note:: not intended for general usage
        """
        _in_scales = (
            {criterion: in_scales for criterion in df.columns.tolist()}
            if isinstance(in_scales, Scale)
            else in_scales
        )

        def normalize_s(s: Series) -> Series:
            return cls._normalize_series(s, _in_scales[s.name])

        return df.apply(normalize_s, axis=0)

    @classmethod
    def _transform_dataframe(
        cls,
        df: DataFrame,
        in_scales: Union[Scale, Mapping[Any, Scale]],
        out_scales: Union[S, Mapping[Any, S]],
    ) -> DataFrame:
        """Transform dataframe to desired scales.

        :param df:
        :param in_scales: input scales
        :param out_scales: output scales
        :return: transformed dataframe (new object)

        .. note:: not intended for general usage
        """
        _in_scales = (
            {criterion: in_scales for criterion in df.columns.tolist()}
            if isinstance(in_scales, Scale)
            else in_scales
        )
        _out_scales = (
            {
                criterion: cast(S, out_scales)
                for criterion in df.columns.tolist()
            }
            if isinstance(out_scales, Scale)
            else out_scales
        )

        def transform_s(s: Series) -> Series:
            return cls._transform_series(
                s, _in_scales[s.name], _out_scales[s.name]
            )

        return df.apply(
            transform_s,
            axis=0,
        )

    @classmethod
    def _normalize_performance_table(
        cls,
        performance_table: PerformanceTable,
    ) -> PerformanceTable[NormalScale]:
        """Normalize performance table.

        :param performance_table:
        :return: normalized performance table (new object)

        .. note:: not intended for general usage
        """
        return PerformanceTable(
            cls._normalize_dataframe(
                performance_table.data, performance_table.scales
            ),
            scales=QuantitativeScale.normal(),
        )

    @classmethod
    def _transform_performance_table(
        cls,
        performance_table: PerformanceTable,
        out_scales: Union[S, Mapping[Any, S]],
    ) -> PerformanceTable[S]:
        """Transform performance table to new scales.

        :param performance_table:
        :param out_scales: output scales
        :return: transformed performance table (new object)

        .. note:: not intended for general usage
        """
        return PerformanceTable(
            cls._transform_dataframe(
                performance_table.data, performance_table.scales, out_scales
            ),
            scales=out_scales,
        )

    @classmethod
    def _normalize_adjacency_matrix(
        cls, matrix: AdjacencyValueMatrix
    ) -> AdjacencyValueMatrix[NormalScale]:
        """Normalize adjacency value matrix.

        :param matrix:
        :return: normalized adjacency value matrix (new object)

        .. note:: not intended for general usage
        """
        return AdjacencyValueMatrix(
            cls._normalize_dataframe(matrix.data, matrix.scale),
            scale=QuantitativeScale.normal(),
        )

    @classmethod
    def _transform_adjacency_matrix(
        cls, matrix: AdjacencyValueMatrix, out_scale: S
    ) -> AdjacencyValueMatrix[S]:
        """Transform adjacency value matrix to new scale.

        :param matrix:
        :param out_scales: output scales
        :return: transformed adjacency value matrix (new object)

        .. note:: not intended for general usage
        """
        return AdjacencyValueMatrix(
            cls._transform_dataframe(matrix.data, matrix.scale, out_scale),
            scale=out_scale,
        )

    @classmethod
    def _normalize_partial_values(
        cls,
        partial_values: PartialValueMatrix,
    ) -> PartialValueMatrix[NormalScale]:
        """Normalize partial value matrix.

        :param partial_values:
        :return: normalized partial value matrix (new object)

        .. note:: not intended for general usage
        """
        return PartialValueMatrix(
            dataframe_map(
                partial_values.data,
                lambda s: cls._normalize_series(s, partial_values.scales),
            ),
            scales=QuantitativeScale.normal(),
        )

    @classmethod
    def _transform_partial_values(
        cls,
        partial_values: PartialValueMatrix,
        out_scales: Union[S, Mapping[Any, S]],
    ) -> PartialValueMatrix[S]:
        """Transform partial value matrix to new scale.

        :param partial_values:
        :param out_scales: output scales
        :return: transformed partial value matrix (new object)

        .. note:: not intended for general usage
        """
        return PartialValueMatrix(
            dataframe_map(
                partial_values.data,
                lambda s: cls._transform_series(
                    s, partial_values.scales, out_scales
                ),
            ),
            scales=out_scales,
        )

    @overload
    @classmethod
    def normalize(cls, data: Any, in_scales: Scale) -> Any:  # pragma: nocover
        ...

    @overload
    @classmethod
    def normalize(
        cls, data: Series, in_scales: Union[Mapping[Any, Scale], Scale]
    ) -> Series:  # pragma: nocover
        ...

    @overload
    @classmethod
    def normalize(
        cls, data: CommensurableValues
    ) -> CommensurableValues[NormalScale]:  # pragma: nocover
        ...

    @overload
    @classmethod
    def normalize(cls, data: Values) -> Values[NormalScale]:  # pragma: nocover
        ...

    @overload
    @classmethod
    def normalize(
        cls, data: DataFrame, in_scales: Union[Mapping[Any, Scale], Scale]
    ) -> DataFrame:  # pragma: nocover
        ...

    @overload
    @classmethod
    def normalize(
        cls, data: AdjacencyValueMatrix
    ) -> AdjacencyValueMatrix[NormalScale]:  # pragma: nocover
        ...

    @overload
    @classmethod
    def normalize(
        cls, data: PerformanceTable
    ) -> PerformanceTable[NormalScale]:  # pragma: nocover
        ...

    @overload
    @classmethod
    def normalize(
        cls, data: PartialValueMatrix
    ) -> PartialValueMatrix[NormalScale]:  # pragma: nocover
        ...

    @classmethod
    def normalize(
        cls,
        data: Union[
            Any,
            Series,
            Values,
            CommensurableValues,
            DataFrame,
            AdjacencyValueMatrix,
            PerformanceTable,
            PartialValueMatrix,
        ],
        in_scales: Union[Mapping[Any, Scale], Scale, None] = None,
    ) -> Union[
        Any,
        Series,
        Values[NormalScale],
        CommensurableValues[NormalScale],
        DataFrame,
        AdjacencyValueMatrix[NormalScale],
        PerformanceTable[NormalScale],
        PartialValueMatrix[NormalScale],
    ]:
        """Normalize input data.

        Output type is the same as input `data` type.

        :param data:
        :param in_scales:
            input scales (must be used when `data` doesn't have `scales`
            attribute)
        :return: normalized data (new object)
        :raise TypeError: if type of arguments are not supported
        """
        if isinstance(data, Series) and in_scales:
            return cls._normalize_series(data, in_scales)
        elif isinstance(data, CommensurableValues):
            return cls._normalize_criterion_values(data)
        elif isinstance(data, Values):
            return cls._normalize_values(data)
        elif isinstance(data, DataFrame) and in_scales:
            return cls._normalize_dataframe(data, in_scales)
        elif isinstance(data, AdjacencyValueMatrix):
            return cls._normalize_adjacency_matrix(data)
        elif isinstance(data, PerformanceTable):
            return cls._normalize_performance_table(data)
        elif isinstance(data, PartialValueMatrix):
            return cls._normalize_partial_values(data)
        elif isinstance(in_scales, Scale):
            return cls._normalize_one(data, in_scales)
        raise TypeError("type of arguments not supported")

    @overload
    @classmethod
    def transform(
        cls, data: Any, out_scales: S, in_scales: Scale
    ) -> Any:  # pragma: nocover
        ...

    @overload
    @classmethod
    def transform(
        cls,
        data: Series,
        out_scales: Union[S, Mapping[Any, S]],
        in_scales: Union[Scale, Mapping[Any, Scale]],
    ) -> Series:  # pragma: nocover
        ...

    @overload
    @classmethod
    def transform(
        cls, data: CommensurableValues, out_scales: S
    ) -> CommensurableValues[S]:  # pragma: nocover
        ...

    @overload
    @classmethod
    def transform(
        cls, data: Values, out_scales: Union[S, Mapping[Any, S]]
    ) -> Values[S]:  # pragma: nocover
        ...

    @overload
    @classmethod
    def transform(
        cls,
        data: DataFrame,
        out_scales: Union[S, Mapping[Any, S]],
        in_scales: Union[Scale, Mapping[Any, Scale]],
    ) -> DataFrame:  # pragma: nocover
        ...

    @overload
    @classmethod
    def transform(
        cls, data: AdjacencyValueMatrix, out_scales: S
    ) -> AdjacencyValueMatrix[S]:  # pragma: nocover
        ...

    @overload
    @classmethod
    def transform(
        cls, data: PerformanceTable, out_scales: Union[S, Mapping[Any, S]]
    ) -> PerformanceTable[S]:  # pragma: nocover
        ...

    @overload
    @classmethod
    def transform(
        cls, data: PartialValueMatrix, out_scales: Union[S, Mapping[Any, S]]
    ) -> PartialValueMatrix[S]:  # pragma: nocover
        ...

    @classmethod
    def transform(
        cls,
        data: Union[
            Any,
            Series,
            Values,
            CommensurableValues,
            DataFrame,
            AdjacencyValueMatrix,
            PerformanceTable,
            PartialValueMatrix,
        ],
        out_scales: Union[S, Mapping[Any, S]],
        in_scales: Union[Scale, Mapping[Any, Scale], None] = None,
    ) -> Union[
        Any,
        Series,
        Values[S],
        CommensurableValues[S],
        DataFrame,
        AdjacencyValueMatrix[S],
        PerformanceTable[S],
        PartialValueMatrix[S],
    ]:
        """Transform input data to new scales.

        Output type is the same as input `data` type.

        :param data:
        :param out_scales: output scales
        :param in_scales:
            input scales (must be used when `data` doesn't have `scales`
            attribute)
        :return: transformed data (new object)
        :raise TypeError: if type of arguments are not supported
        """
        if isinstance(data, Series) and in_scales:
            return cls._transform_series(data, in_scales, out_scales)
        elif isinstance(data, CommensurableValues) and isinstance(
            out_scales, Scale
        ):
            return cls._transform_criterion_values(data, cast(S, out_scales))
        elif isinstance(data, Values):
            return cls._transform_values(data, out_scales)
        elif isinstance(data, DataFrame) and in_scales:
            return cls._transform_dataframe(data, in_scales, out_scales)
        elif isinstance(data, AdjacencyValueMatrix) and isinstance(
            out_scales, Scale
        ):
            return cls._transform_adjacency_matrix(data, cast(S, out_scales))
        elif isinstance(data, PerformanceTable):
            return cls._transform_performance_table(
                data,
                out_scales,
            )
        elif isinstance(data, PartialValueMatrix):
            return cls._transform_partial_values(data, out_scales)
        elif isinstance(in_scales, Scale) and isinstance(out_scales, Scale):
            return cls._transform_one(data, in_scales, out_scales)
        raise TypeError("type of arguments not supported")


@set_module("mcda.transformers")
class Transformer(ITransformer):
    """This class defines the basic transformer methods.

    It uses normalization and denormalization methods to transform values
    between scales, based on quantitative interval boundaries mapping.
    """

    @classmethod
    def _denormalize_one(cls, x: float, out_scale: S) -> Any:
        """Denormalize a single value given its output scale.

        Quantitative interval boundaries are used to map normalized values to
        the `out_scale` ones.

        :param x: value to normalize
        :param in_scale: value scale
        :return: normalized value

        .. note:: not intended for general usage
        """
        if not isinstance(out_scale, OrdinalScale):
            raise TypeError("cannot denormalize value to non-ordinal scale")
        if out_scale.preference_direction == PreferenceDirection.MIN:
            return out_scale.label(out_scale.interval.denormalize(1 - x))
        return out_scale.label(out_scale.interval.denormalize(x))

    @classmethod
    def _normalize_one(cls, x: Any, in_scale: Scale) -> float:
        """Normalize a single value given its scale.

        Quantitative interval boundaries are used to map `in_scale` values to
        normalized ones.

        :param x: value to normalize
        :param in_scale: value scale
        :return: normalized value

        .. note:: not intended for general usage
        """
        if not isinstance(in_scale, OrdinalScale):
            raise TypeError("cannot transform value from non-ordinal scale")
        normalized_x = in_scale.interval.normalize(in_scale.value(x))
        if in_scale.preference_direction == PreferenceDirection.MIN:
            return 1 - normalized_x
        return normalized_x

    @classmethod
    def _transform_one(cls, x: Any, in_scale: Scale, out_scale: S) -> Any:
        """Transform a single value to a new scale.

        It calls first :meth:`normalize_one` then :meth:`denormalize_one`.

        :param x: value to transform
        :param in_scale: value scale
        :param out_scale: output scale
        :return: transformed value

        .. note:: not intended for general usage
        """
        return cls._denormalize_one(cls._normalize_one(x, in_scale), out_scale)


@set_module("mcda.transformers")
class ClosestTransformer(Transformer):
    """This transformer associates out-of-scale values with closest preferred
    ones in discrete ordinal scales.
    """

    @classmethod
    def _denormalize_one(cls, x: float, out_scale: S) -> Any:
        """Denormalize one value.

        When `out_scale` is qualitative, closest preferred value is returned.

        :param x:
        :param out_scale:
        :return: denormalized value
        """
        if isinstance(out_scale, QualitativeScale) or isinstance(
            out_scale, DiscreteQuantitativeScale
        ):
            continuous_scale = QuantitativeScale(
                out_scale.interval,
                preference_direction=out_scale.preference_direction,
            )
            denormalized_x = super()._denormalize_one(
                x,
                continuous_scale,
            )
            preferred_values = [
                value
                for value in out_scale.values
                if continuous_scale.is_better_or_equal(value, denormalized_x)
            ]
            closest_prefered_value = (
                max(preferred_values)
                if out_scale.preference_direction == PreferenceDirection.MIN
                else min(preferred_values)
            )
            return out_scale.label(closest_prefered_value)
        return super()._denormalize_one(x, out_scale)


transform = Transformer.transform

normalize = Transformer.normalize
