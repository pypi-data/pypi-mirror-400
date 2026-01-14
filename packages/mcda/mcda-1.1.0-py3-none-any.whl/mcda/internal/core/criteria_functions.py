from __future__ import annotations

from typing import Any, Generic, Mapping, Type, TypeVar, Union, cast, overload

from pandas import DataFrame, Series

from .aliases import Function
from .compatibility import dataframe_map
from .matrices import PartialValueMatrix, PerformanceTable
from .scales import Scale
from .utils import set_module
from .values import CommensurableValues, Values

I_S = TypeVar("I_S", bound=Scale, covariant=True)
O_S = TypeVar("O_S", bound=Scale, covariant=True)


@set_module("mcda.functions")
class CriterionFunction(Generic[I_S, O_S]):
    """This class defines a function and its input/output scale.

    :param function:
    :param in_scale: input scale (if not provided, inferred from input)
    :param out_scale: output scale (if not provided, inferred from output)
    :param in_stype: input scale type (if not provided, inferred from input)
    :param out_stype: output scale type (if not provided, inferred from output)
    :raise TypeError:
        * if `in_scale` is not an instance of `in_stype` (and both are set)
        * if `out_scale` is not an instance of `out_stype` (and both are set)
    """

    def __init__(
        self,
        function: Function,
        in_scale: Union[I_S, None] = None,
        out_scale: Union[O_S, None] = None,
        in_stype: Union[Type[I_S], None] = None,
        out_stype: Union[Type[O_S], None] = None,
    ):
        if in_stype and in_scale and not isinstance(in_scale, in_stype):
            raise TypeError("input stype and scale are not compatible")
        if out_stype and out_scale and not isinstance(out_scale, out_stype):
            raise TypeError("output stype and scale are not compatible")
        self.function = function
        self.in_scale = in_scale
        self.out_scale = out_scale
        self.in_stype = in_stype
        self.out_stype = out_stype

    def within_in_scale(
        self, data: Union[Any, Series, CommensurableValues[I_S]]
    ) -> bool:
        """Check potential input is inside input scale.

        :param data:
        :return: ``True`` if `data` is within :attr:`in_scale`
        """
        if isinstance(data, Series):
            v = CommensurableValues(
                data, scale=self.in_scale, stype=self.in_stype
            )
            return v.is_within_scales
        if isinstance(data, CommensurableValues):
            v = CommensurableValues(
                data.data, scale=self.in_scale, stype=self.in_stype
            )
            return v.is_within_scales
        return data in self.in_scale if self.in_scale else True

    def _apply_series(self, series: Series) -> Series:
        """Apply scale function to all cells of a series.

        :param series:
        :return: resulting series

        .. note::
            This method is called when calling object as a function with a
            :class:`pandas.Series` input.
        """
        return series.apply(self.function)

    def _apply_criterion_values(
        self, criterion_values: CommensurableValues[I_S]
    ) -> CommensurableValues[O_S]:
        """Apply scale function to all cells of a criterion values.

        :param criterion_values:
        :return: resulting values

        .. note::
            This method is called when calling object as a function with a
            :class:`CriterionValues` input.
        """
        return CommensurableValues(
            self._apply_series(criterion_values.data),
            scale=self.out_scale,
            stype=self.out_stype,
        )

    @overload
    def __call__(self, x: Series) -> Series:  # pragma: nocover
        ...

    @overload
    def __call__(
        self, x: CommensurableValues[I_S]
    ) -> CommensurableValues[O_S]:  # pragma: nocover
        ...

    @overload
    def __call__(self, x: Any) -> Any:  # pragma: nocover
        ...

    def __call__(
        self, x: Union[Any, Series, CommensurableValues[I_S]]
    ) -> Union[Any, Series, CommensurableValues[O_S]]:
        """Apply scale function to input.

        :param x: either a single value or a series/criterion values
        :return: result
        """
        if isinstance(x, CommensurableValues):
            return self._apply_criterion_values(x)
        if isinstance(x, Series):
            return self._apply_series(x)
        return self.function(x)


@set_module("mcda.functions")
class CriteriaFunctions(Generic[I_S, O_S]):
    """This class represents a multi-attribute scale functions.

    :param functions: either :class:`CriterionFunction` or functions
    :param in_scales:
        input scales (ignored if :class:`CriterionFunction` supplied)
    :param out_scales:
        output scales (ignored if :class:`CriterionFunction` supplied)
    :param in_stype:
    :param out_stype:
    :raise TypeError:
        * if `in_stype` is not consistent with at least one criterion function
        * if `out_stype` is not consistent with at least one criterion function

    :attr functions: criterion functions

    .. note::
        `functions` are defined for the provided scales, so when
        applying functions you must provide correctly scaled values
    """

    def __init__(
        self,
        functions: Mapping[Any, CriterionFunction[I_S, O_S] | Function],
        in_scales: Mapping[Any, I_S] | I_S | None = None,
        out_scales: Mapping[Any, O_S] | O_S | None = None,
        in_stype: Type[I_S] | None = None,
        out_stype: Type[O_S] | None = None,
        **kwargs,
    ):
        self.in_stype = in_stype
        self.out_stype = out_stype
        self.in_scales: Mapping[Any, I_S] = {}
        self.out_scales: Mapping[Any, O_S] = {}
        self.functions: Mapping[Any, CriterionFunction[I_S, O_S]] = {}
        for c, f in functions.items():
            if isinstance(f, CriterionFunction):
                _f = cast(CriterionFunction[I_S, O_S], f)
                if _f.in_scale:
                    self.in_scales[c] = _f.in_scale
                if _f.out_scale:
                    self.out_scales[c] = _f.out_scale
                if (
                    _f.in_stype
                    and self.in_stype
                    and not issubclass(_f.in_stype, self.in_stype)
                ):
                    raise TypeError(
                        "'in_stype' is not compatible with criterion function "
                        f"{c}"
                    )
                if (
                    _f.in_scale
                    and self.in_stype
                    and not isinstance(_f.in_scale, self.in_stype)
                ):
                    raise TypeError(
                        "'in_stype' is not compatible with criterion function "
                        f"{c}"
                    )
                if (
                    _f.out_stype
                    and self.out_stype
                    and not issubclass(_f.out_stype, self.out_stype)
                ):
                    raise TypeError(
                        "'out_stype' is not compatible with criterion function"
                        f" {c}"
                    )
                if (
                    _f.out_scale
                    and self.out_stype
                    and not isinstance(_f.out_scale, self.out_stype)
                ):
                    raise TypeError(
                        "'out_stype' is not compatible with criterion function"
                        f" {c}"
                    )
                self.functions[c] = _f
            else:
                if isinstance(in_scales, Mapping) and c in in_scales:
                    self.in_scales[c] = cast(I_S, in_scales[c])
                elif isinstance(in_scales, Scale):
                    self.in_scales[c] = cast(I_S, in_scales)
                if isinstance(out_scales, Mapping) and c in out_scales:
                    self.out_scales[c] = cast(O_S, out_scales[c])
                elif isinstance(out_scales, Scale):
                    self.out_scales[c] = cast(O_S, out_scales)
                self.functions[c] = CriterionFunction(
                    cast(Function, f),
                    self.in_scales.get(c),
                    self.out_scales.get(c),
                    self.in_stype,
                    self.out_stype,
                )

    def within_in_scales(
        self,
        data: Union[
            Series,
            Values[I_S],
            DataFrame,
            PerformanceTable[I_S],
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
        m = PerformanceTable(
            data.data, scales=self.in_scales, stype=self.in_stype
        )
        return m.is_within_scales

    def _apply_series(self, series: Series) -> Series:
        """Apply each scale function to its corresponding cell.

        :param series:
        :return: resulting series

        .. note::
            This method is called when calling object as a function with a
            :class:`pandas.Series` input.
        """
        return Series(
            {
                criterion: self.functions[criterion](value)
                for criterion, value in dict(series).items()
            }
        )

    def _apply_values(self, values: Values[I_S]) -> Values[O_S]:
        """Apply each scale function to its corresponding cell.

        :param values:
        :return: resulting values

        .. note::
            This method is called when calling object as a function with a
            :class:`Values` input.
        """
        return Values(
            self._apply_series(values.data), self.out_scales, self.out_stype
        )

    def _apply_dataframe(self, df: DataFrame) -> DataFrame:
        """Apply each scale function to its corresponding column.

        :param df:
        :return: resulting dataframe

        .. note::
            This method is called when calling object as a function with a
            :class:`pandas.DataFrame` input.
        """
        return cast(
            DataFrame,
            df.apply(lambda col: col.apply(self.functions.get(col.name))),
        )

    def _apply_performance_table(
        self, performance_table: PerformanceTable[I_S]
    ) -> PerformanceTable[O_S]:
        """Apply each scale function to its corresponding column.

        :param performance_table:
        :return: resulting performance table

        .. note::
            This method is called when calling object as a function with a
            :class:`PerformanceTable` input.
        """
        return PerformanceTable(
            self._apply_dataframe(performance_table.data),
            scales=self.out_scales,
            stype=self.out_stype,
        )

    def _apply_partial_values(
        self, partial_values: PartialValueMatrix[I_S]
    ) -> PartialValueMatrix[O_S]:
        """Apply each scale function to its corresponding criterion.

        :param partial_values:
        :return: resulting partial values matrix

        .. note::
            This method is called when calling object as a function with a
            :class:`PartialValueMatrix` input.
        """
        return PartialValueMatrix(
            dataframe_map(partial_values.data, self._apply_series),
            scales=self.out_scales,
            stype=self.out_stype,
        )

    @overload
    def __call__(self, x: Series) -> Series:  # pragma: nocover
        ...

    @overload
    def __call__(self, x: DataFrame) -> DataFrame:  # pragma: nocover
        ...

    @overload
    def __call__(self, x: Values[I_S]) -> Values[O_S]:  # pragma: nocover
        ...

    @overload
    def __call__(
        self, x: PerformanceTable[I_S]
    ) -> PerformanceTable[O_S]:  # pragma: nocover
        ...

    @overload
    def __call__(
        self, x: PartialValueMatrix[I_S]
    ) -> PartialValueMatrix[O_S]:  # pragma: nocover
        ...

    def __call__(
        self,
        x: Union[
            Series,
            Values[I_S],
            DataFrame,
            PerformanceTable[I_S],
            PartialValueMatrix[I_S],
        ],
    ) -> Union[
        Series,
        Values[O_S],
        DataFrame,
        PerformanceTable[O_S],
        PartialValueMatrix[O_S],
    ]:
        """Apply scale functions to input.

        :param x: input
        :return: result
        """
        if isinstance(x, Series):
            return self._apply_series(x)
        elif isinstance(x, Values):
            return self._apply_values(x)
        elif isinstance(x, DataFrame):
            return self._apply_dataframe(x)
        elif isinstance(x, PartialValueMatrix):
            return self._apply_partial_values(x)
        else:
            return self._apply_performance_table(
                cast(PerformanceTable[I_S], x)
            )
