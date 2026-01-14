"""This module contains all functions related to matrices.
"""
from __future__ import annotations

import functools
import sys
from abc import ABC, abstractmethod
from itertools import product
from typing import (
    Any,
    Generic,
    Iterator,
    List,
    Literal,
    Mapping,
    Sequence,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
    overload,
)

from pandas import DataFrame, Series, concat
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components, floyd_warshall

from .compatibility import dataframe_map
from .scales import (
    BinaryScale,
    DiscreteQuantitativeScale,
    OrdinalScale,
    QuantitativeScale,
    Scale,
    common_scale_type,
)
from .utils import set_module
from .values import CommensurableValues, Values

if sys.version_info >= (3, 11):  # pragma: nocover
    from typing import Self
else:
    from typing_extensions import Self


try:
    from graphviz import Digraph

    _has_graphviz = True
except ImportError:  # pragma: nocover
    import warnings

    warnings.warn(
        "Graph plotting features not available. "
        "If you need those, please install 'graphviz' or this package "
        "optional plotting dependencies 'mcda[plot]'."
    )
    _has_graphviz = False


def requires_graphviz(func):
    """Wrap a class or function that requires graphviz to function.

    :param obj: either a class or function
    :raises ImportError: if graphviz is not installed
    :return: wrapped class or function
    """

    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        if not _has_graphviz:  # pragma: nocover
            raise ImportError("This function requires 'graphviz'")
        return func(*args, **kwargs)

    return wrapped


def dataframe_equals(df1: DataFrame, df2: DataFrame) -> bool:
    """Check if two dataframes have the same values.

    It will realign the indexes and columns if they are ordered differently.

    :param df1:
    :param df2:
    :return:

    .. todo:: integrate into :class:`mcda/core.adjacency_matrix.Matrix`
    """
    return df1.to_dict() == df2.to_dict()


class IMatrix(ABC):
    """This class implements a wrapper on :class:`pandas.DataFrame`.

    It adds a method to check if two such objects are equals.
    It is meant to be use for any class that needs a DataFrame as its
    internal data representation in this package.

    :param data: dataframe containing the matrix
    :raise KeyError:
        * if some indexes are duplicated
        * if some columns are duplicated
    """

    def __init__(self, data, **kwargs):
        self.data = DataFrame(data)
        if self.data.index.has_duplicates:
            raise KeyError(
                "some indexes are duplicated: "
                f"{self.data.index[self.data.index.duplicated()].tolist()}"
            )
        if self.data.columns.has_duplicates:
            raise KeyError(
                "some columns are duplicated: "
                f"{self.data.columns[self.data.columns.duplicated()].tolist()}"
            )

    @property
    def rows(self) -> List:
        """Return row labels."""
        return self.data.index.tolist()

    @property
    def columns(self) -> List:
        """Return column labels."""
        return self.data.columns.tolist()

    @property
    def cell(self) -> Mapping[Tuple[Any, Any], Any]:
        """Return matrix cell accessor.

        .. note:: actually returns :meth:`DataFrame.at` from :attr:`data`
        """
        return self.data.at

    def __eq__(self, other) -> bool:
        """Check if both matrices have the same dataframe

        :return:

        .. note:: vertices order does not matter
        """
        if type(other) != type(self):
            return False
        return dataframe_equals(self.data, other.data)


class IAdjacencyMatrix(IMatrix, ABC):
    """This class implements graphs as an adjacency matrix.

    The adjacency matrix is represented internally by a
    :class:`pandas.DataFrame` with vertices as the indexes and columns.

    :param data: adjacency matrix in an array-like or dict-structure
    :param vertices:

    :raise KeyError:
        * if columns and rows have different sets of labels
        * if some vertices are duplicated

    .. note:: the cells of the matrix can be of any type (not just numerics)
    """

    def __init__(self, data, vertices: Union[List, None] = None, **kwargs):
        df = DataFrame(
            data.values if isinstance(data, DataFrame) and vertices else data,
            index=vertices,
            columns=vertices,
        )
        if df.columns.tolist() != df.index.tolist():
            raise KeyError(
                f"{self.__class__} supports only same labelled"
                "index and columns"
            )
        super().__init__(df, **kwargs)

    @property
    def vertices(self) -> List:
        """Return list of vertices"""
        return self.rows


S = TypeVar("S", bound=Scale, covariant=True)


class RowView(Mapping[Any, Values[S]], Generic[S]):
    """This class defines a view of a value matrix per row.

    :param matrix:
    """

    def __init__(self, matrix: IValueMatrix[S]):
        self._matrix = matrix

    @property
    def _data(self) -> DataFrame:
        """Dataframe of the value matrix"""
        return self._matrix.data

    @property
    def _scales(self) -> Mapping[Any, S]:
        """Scales of the value matrix"""
        return self._matrix.scales

    @property
    def _stype(self) -> Type[S]:
        """Scale type of the value matrix"""
        return self._matrix.stype

    def __len__(self) -> int:
        """Number of rows in the value matrix"""
        return len(self._matrix.rows)

    def __getitem__(self, key: Any) -> Values[S]:
        """Return values at row.

        :param key: row index
        :raises KeyError: if `key` row doesn't exist
        :return:
        """
        return Values[S](self._data.loc[key], self._scales, self._stype)

    def __iter__(self) -> Iterator[Any]:
        """Iterate on the rows"""
        return iter(self._matrix.rows)


class ColumnView(Mapping[Any, CommensurableValues[S]], Generic[S]):
    """This class defines a view of a value matrix per column.

    :param matrix:
    """

    def __init__(self, matrix: IValueMatrix[S]):
        self._matrix = matrix

    @property
    def _data(self) -> DataFrame:
        """Dataframe of the value matrix"""
        return self._matrix.data

    @property
    def _scales(self) -> Mapping[Any, S]:
        """Scales of the value matrix"""
        return self._matrix.scales

    @property
    def _stype(self) -> Type[S]:
        """Scale type of the value matrix"""
        return self._matrix.stype

    def __len__(self) -> int:
        """Number of columns in the value matrix"""
        return len(self._matrix.columns)

    def __getitem__(self, key: Any) -> CommensurableValues[S]:
        """Return values at column.

        :param key: column index
        :raises KeyError: if `key` column doesn't exist
        :return:
        """
        return CommensurableValues[S](
            self._data[key], self._scales[key], self._stype
        )

    def __iter__(self) -> Iterator[Any]:
        """Iterate on the columns"""
        return iter(self._matrix.columns)


class IValueMatrix(IMatrix, Generic[S], ABC):
    """This class defines a matrix with associated scales (one per column).

    :param data:
    :param scales:
        data scale(s) (one per column or one shared, will be inferred from data
        if absent using :meth:`Scale.fit`)
    :param stype: scales type used
    :raise KeyError:
        * if some indexes are duplicated
        * if some columns are duplicated
    :raise TypeError: if `stype` and `scales` types mismatch

    .. todo:: remove this class completely, put its code in current subclasses
    """

    def __init__(
        self,
        data,
        scales: Union[S, Mapping[Any, S], None] = None,
        stype: Union[Type[S], None] = None,
        **kwargs,
    ):
        super().__init__(data, **kwargs)
        self.scales: Mapping[Any, S] = {}
        _stype = cast(Type[S], Scale if stype is None else stype)
        for c in self.columns:
            if isinstance(scales, Mapping) and c in scales:
                self.scales[c] = scales[c]
            elif isinstance(scales, Scale):
                self.scales[c] = cast(S, scales)
            else:
                self.scales[c] = _stype.fit(self.data[c])
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

    @property
    def bounds(self) -> Mapping[Any, S]:
        """Return scales inferred from values."""
        return {
            column: value.bounds
            for column, value in self.columns_values.items()
        }

    @property
    def union_bounds(self) -> S:
        """Return one scale for whole matrix inferred from values."""
        return Values[S](
            Series(self.data.values.flatten().tolist()), stype=self.stype
        ).bounds

    @property
    def rows_values(self) -> Mapping[Any, Values[S]]:
        """Iterator on the table alternatives values"""
        return RowView[S](self)

    @property
    def columns_values(self) -> Mapping[Any, CommensurableValues[S]]:
        """Iterator on the table criteria values"""
        return ColumnView[S](self)

    @property
    @abstractmethod
    def to_numeric(self) -> IValueMatrix[QuantitativeScale]:  # pragma: nocover
        """Return numeric conversion of ordinal values.

        :raise TypeError: if :attr:`scales` are not ordinal
        """
        pass

    def __eq__(self, other: Any) -> bool:
        """Check equality of scale matrices.

        Equality is defines as having the same set of scales, and having the
        same data.

        :return: ``True`` if both are equal
        """
        if not super().__eq__(other):
            return False
        _values = cast(IValueMatrix, other)
        return self.scales == _values.scales

    @property
    def within_scales(self) -> DataFrame:
        """Return a dataframe indicating which values are within their
        respective scale.

        :return:
        """
        return DataFrame(
            {c: dict(v.within_scales) for c, v in self.columns_values.items()}
        )

    @property
    def is_within_scales(self) -> bool:
        """Check whether all values are within their respective scales.

        :return:
        """
        return self.within_scales.all(None)

    @property
    def is_numeric(self) -> bool:
        """Check whether table is numeric.

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

    @overload
    def sum(self, axis: None = None) -> float:  # pragma: nocover
        ...

    @overload
    def sum(
        self, axis: Literal[0, 1]
    ) -> CommensurableValues[QuantitativeScale]:  # pragma: nocover
        ...

    def sum(
        self, axis: Literal[0, 1] | None = None
    ) -> Union[CommensurableValues[QuantitativeScale], float]:
        """Return the sum of the data (all table, row or column-wise).

        :param axis:
            * 0: column-wise sum
            * 1: row-wise sum
            * ``None``: complete sum
        :return:

        .. warning::
            it will raise a :class:`TypeError` if data contains numeric
            and non-numeric values
        """
        if axis is None:
            return self.data.sum().sum()
        return CommensurableValues(
            self.data.sum(axis=axis), stype=QuantitativeScale
        )

    def copy(self) -> Self:
        """Return a copy of the object"""
        return self.__class__(
            self.data.copy(), scales=dict(self.scales), stype=self.stype
        )


@set_module("mcda")
class PerformanceTable(IValueMatrix[S], Generic[S]):
    """This class defines a performance table.

    :param data:
    :param scales:
        data scale(s) (one per column or one shared, will be inferred from data
        if absent using :meth:`Scale.fit`)
    :param alternatives: if not set, inferred from `data`
    :param criteria:  if not set, inferred from `data`
    :param stype: scales type used
    :raise KeyError:
        * if some indexes are duplicated
        * if some columns are duplicated
    :raise TypeError: if `stype` and `scales` types mismatch
    """

    def __init__(
        self,
        data,
        scales: Union[S, Mapping[Any, S], None] = None,
        alternatives: Union[List, None] = None,
        criteria: Union[List, None] = None,
        stype: Union[Type[S], None] = None,
        **kwargs,
    ):
        df = DataFrame(data, index=alternatives, columns=criteria)
        super().__init__(df, scales=scales, stype=stype, **kwargs)

    @property
    def criteria(self) -> List:
        """Return performance table criteria"""
        return self.columns

    @property
    def alternatives(self) -> List:
        """Return performance table alternatives"""
        return self.rows

    @property
    def alternatives_values(self) -> Mapping[Any, Values[S]]:
        """Iterator on the table alternatives values"""
        return self.rows_values

    @property
    def criteria_values(self) -> Mapping[Any, CommensurableValues[S]]:
        """Iterator on the table criteria values"""
        return self.columns_values

    @property
    def efficients(self) -> List:
        """Return efficient alternatives.

        This is the list of alternatives that are not strongly dominated by
        another one.

        :return:
        """
        res = set(self.alternatives)
        for avalues in self.alternatives_values.values():
            dominated = set()
            for b in res:
                if avalues.name == b:
                    continue
                if avalues.dominate_strongly(self.alternatives_values[b]):
                    dominated.add(b)
            res -= dominated
        return sorted(res, key=lambda a: self.alternatives.index(a))

    @property
    def to_numeric(self) -> PerformanceTable[QuantitativeScale]:
        """Return numeric conversion of ordinal values.

        :raise TypeError: if :attr:`scales` are not ordinal
        """
        if self.is_numeric:
            return cast(PerformanceTable[QuantitativeScale], self.copy())
        if not self.is_ordinal:
            raise TypeError("cannot convert to numerics nominal values")
        return PerformanceTable(
            DataFrame(
                {
                    c: dict(v.to_numeric.data)
                    for c, v in self.columns_values.items()
                }
            ),
            {c: cast(OrdinalScale, s).numeric for c, s in self.scales.items()},
        )

    def __mul__(self, other: Union[IMatrix, float]) -> PerformanceTable:
        """Return product.

        :param other:
        :return:
        """
        coeff = other.data if isinstance(other, IMatrix) else other
        return PerformanceTable(self.data * coeff)

    def __add__(self, other: Any) -> PerformanceTable:
        """Return addition.

        :param other:
        :return:
        """
        added = other.data if isinstance(other, IMatrix) else other
        return PerformanceTable(self.data + added)

    def __sub__(self, other: Any) -> PerformanceTable:
        """Return subtraction.

        :param other:
        :return:
        """
        subtracted = other.data if isinstance(other, IMatrix) else other
        return PerformanceTable(self.data - subtracted)

    def subtable(
        self, rows: Union[List, None] = None, columns: Union[List, None] = None
    ) -> Self:
        """Return the subtable containing given rows and columns.

        :param rows:
        :param columns:
        :return:
        """
        rows = self.rows if rows is None else rows
        columns = self.columns if columns is None else columns
        return self.__class__(
            self.data.loc[rows, columns],
            {criterion: self.scales[criterion] for criterion in columns},
            stype=self.stype,
        )

    @classmethod
    def concat(
        cls,
        matrices: Sequence[IValueMatrix],
        axis: Literal[0, 1] = 0,
        **kwargs,
    ) -> Self:
        """Concatenate multiple value matrices.

        :param matrices:
        :param axis:
            axis along which to concatenate
            (0: add alternatives, 1: add criteria)
        :return: concatenated value matrix

        .. warning::
            `matrices` objects are concatenated as is, no
            transformation of scales is applied.
        """
        scales: dict[Any, S] = {}
        dataframes = []
        for t in matrices:
            dataframes.append(t.data)
            for c, s in t.scales.items():
                scales.setdefault(c, s)
        df = concat(dataframes, axis=axis)
        return cls(df, scales=scales)


class PartialRowView(Mapping[Any, PerformanceTable[S]], Generic[S]):
    """This class defines a view of a partial value matrix per row.

    :param matrix:
    """

    def __init__(self, matrix: PartialValueMatrix[S]):
        self._matrix = matrix

    @property
    def _data(self) -> DataFrame:
        """Dataframe of the partial value matrix"""
        return self._matrix.data

    @property
    def _scales(self) -> Mapping[Any, S]:
        """Scales of the partial value matrix"""
        return self._matrix.scales

    @property
    def _stype(self) -> Type[S]:
        """Scale type of the partial value matrix"""
        return self._matrix.stype

    def __len__(self) -> int:
        """Number of vertices in the partial value matrix"""
        return len(self._matrix.vertices)

    def __getitem__(self, key: Any) -> PerformanceTable[S]:
        """Return values at row.

        :param key: vertex
        :raises KeyError: if `key` vertex doesn't exist
        :return:
        """
        return PerformanceTable(
            DataFrame(
                [s.tolist() for s in self._data.loc[key].tolist()],
                index=self._matrix.vertices,
                columns=self._matrix.criteria,
            ),
            self._scales,
            stype=self._stype,
        )

    def __iter__(self) -> Iterator[Any]:
        """Iterate on the vertices"""
        return iter(self._matrix.vertices)


class PartialColumnView(Mapping[Any, PerformanceTable[S]], Generic[S]):
    """This class defines a view of a partial value matrix per column.

    :param matrix:
    """

    def __init__(self, matrix: PartialValueMatrix[S]):
        self._matrix = matrix

    @property
    def _data(self) -> DataFrame:
        """Dataframe of the partial value matrix"""
        return self._matrix.data

    @property
    def _scales(self) -> Mapping[Any, S]:
        """Scales of the partial value matrix"""
        return self._matrix.scales

    @property
    def _stype(self) -> Type[S]:
        """Scale type of the partial value matrix"""
        return self._matrix.stype

    def __len__(self) -> int:
        """Number of vertices in the partial value matrix"""
        return len(self._matrix.vertices)

    def __getitem__(self, key: Any) -> PerformanceTable[S]:
        """Return values at column.

        :param key: vertex
        :raises KeyError: if `key` vertex doesn't exist
        :return:
        """
        return PerformanceTable(
            DataFrame(
                [s.tolist() for s in self._data[key].tolist()],
                index=self._matrix.vertices,
                columns=self._matrix.criteria,
            ),
            self._scales,
            stype=self._stype,
        )

    def __iter__(self) -> Iterator[Any]:
        """Iterate on the vertices"""
        return iter(self._matrix.vertices)


class PartialCriterionView(
    Mapping[Any, "AdjacencyValueMatrix[S]"], Generic[S]
):
    """This class defines a view of a partial value matrix per criterion.

    :param matrix:
    """

    def __init__(self, matrix: PartialValueMatrix[S]):
        self._matrix = matrix

    @property
    def _data(self) -> DataFrame:
        """Dataframe of the partial value matrix"""
        return self._matrix.data

    @property
    def _scales(self) -> Mapping[Any, S]:
        """Scales of the partial value matrix"""
        return self._matrix.scales

    @property
    def _stype(self) -> Type[S]:
        """Scale type of the partial value matrix"""
        return self._matrix.stype

    def __len__(self) -> int:
        """Number of criteria in the partial value matrix"""
        return len(self._matrix.criteria)

    def __getitem__(self, key: Any) -> AdjacencyValueMatrix[S]:
        """Return values at criterion.

        :param key: criterion
        :raises KeyError: if `key` criterion doesn't exist
        :return:
        """
        return AdjacencyValueMatrix(
            dataframe_map(self._data, lambda s: s[key]),
            scale=self._scales[key],
            stype=self._stype,
        )

    def __iter__(self) -> Iterator[Any]:
        """Iterate on the criteria"""
        return iter(self._matrix.criteria)


@set_module("mcda.matrices")
class PartialValueMatrix(IAdjacencyMatrix, Generic[S]):
    """This class describes a matrix of partial values.

    :param data:
    :param vertices: labels used to identify both rows and columns
    :param criteria: labels used for the values in each cell
    :param scales:
    :param stype: scales type used
    :raise KeyError:
        * if columns and rows have different sets of labels
        * if some vertices are duplicated
    :raise TypeError: if `stype` and `scale` type mismatch
    """

    def __init__(
        self,
        data,
        vertices: Union[List, None] = None,
        criteria: Union[List, None] = None,
        scales: Union[S, Mapping[Any, S], None] = None,
        stype: Union[Type[S], None] = None,
        **kwargs,
    ):
        super().__init__(data, vertices, **kwargs)
        if criteria is None:
            criteria = (
                cast(Series, self.data.iloc[0, 0]).index.tolist()
                if isinstance(self.data.iloc[0, 0], Series)
                else list(range(len(self.data.iloc[0, 0])))
            )
        if len(set(criteria)) != len(criteria):
            raise KeyError("criteria must be uniques")
        self.data = dataframe_map(
            self.data, lambda s: Series(list(s), index=criteria)
        )
        self.scales: Mapping[Any, S] = {}
        _stype = cast(Type[S], Scale if stype is None else stype)
        for c in criteria:
            if isinstance(scales, Mapping) and c in scales:
                self.scales[c] = scales[c]
            elif isinstance(scales, Scale):
                self.scales[c] = cast(S, scales)
            else:
                self.scales[c] = _stype.fit(
                    Series(
                        dataframe_map(
                            self.data, lambda s: s[c]
                        ).values.flatten()
                    )
                )
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

    @property
    def criteria(self) -> List:
        return list(self.scales.keys())

    @property
    def bounds(self) -> Mapping[Any, S]:
        """Infer common scales for each values cell.

        :return: inferred scales
        """
        return {c: m.union_bounds for c, m in self.criteria_matrices.items()}

    @property
    def row_matrices(self) -> Mapping[Any, PerformanceTable[S]]:
        """Iterator on the table rows."""
        return PartialRowView[S](self)

    @property
    def column_matrices(self) -> Mapping[Any, PerformanceTable[S]]:
        """Iterator on the table columns."""
        return PartialColumnView[S](self)

    @property
    def criteria_matrices(self) -> Mapping[Any, AdjacencyValueMatrix[S]]:
        """Iterator on the table criteria."""
        return PartialCriterionView[S](self)

    @property
    def cell(self) -> Mapping[Tuple[Any, Any], Values[S]]:
        """Return matrix cell accessor"""
        return {
            (r, c): Values(
                self.data.at[r, c], scales=self.scales, stype=self.stype
            )
            for c in self.columns
            for r in self.rows
        }

    def __eq__(self, other: Any) -> bool:
        """Check equality of scale matrices.

        Equality is defines as having the same set of scales, and having the
        same data.

        :return: ``True`` if both are equal
        """
        if not isinstance(other, PartialValueMatrix):
            return False
        _values = cast(PartialValueMatrix, other)
        if self.scales == _values.scales:
            d1 = dataframe_map(self.data, lambda s: s.to_dict())
            d2 = dataframe_map(_values.data, lambda s: s.to_dict())
            return d1.to_dict() == d2.to_dict()
        return False

    @property
    def within_scales(self) -> DataFrame:
        """Return a dataframe indicating which values are within their
        respective scale.

        :return:
        """
        return dataframe_map(
            self.data, lambda s: Values(s, self.scales).within_scales
        )

    @property
    def is_within_scales(self) -> bool:
        """Check whether all values are within their respective scales.

        :return:
        """
        return dataframe_map(self.within_scales, lambda s: s.all()).all(None)

    @property
    def is_numeric(self) -> bool:
        """Check whether table is numeric.

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
    def to_numeric(self) -> PartialValueMatrix[QuantitativeScale]:
        """Return numeric conversion of ordinal values.

        :raise TypeError: if :attr:`scales` are not ordinal
        """
        if self.is_numeric:
            return cast(PartialValueMatrix[QuantitativeScale], self.copy())
        if not self.is_ordinal:
            raise TypeError("cannot convert to numerics nominal values")
        return PartialValueMatrix(
            dataframe_map(
                self.data,
                lambda s: Values(s, scales=self.scales).to_numeric.data,
            ),
            scales={
                c: cast(OrdinalScale, s).numeric
                for c, s in self.scales.items()
            },
        )

    def copy(self) -> Self:
        """Return a copy of the object"""
        return self.__class__(
            self.data.copy(), scales=dict(self.scales), stype=self.stype
        )

    def subtable(
        self,
        vertices: Union[List, None] = None,
        criteria: Union[List, None] = None,
    ) -> Self:
        """Return the subtable containing given rows and columns.

        :param rows:
        :param columns:
        :return:
        """
        vertices = self.vertices if vertices is None else vertices
        criteria = self.criteria if criteria is None else criteria
        return self.__class__(
            dataframe_map(
                self.data.loc[vertices, vertices], lambda s: s[criteria]
            ),
            scales={
                criterion: self.scales[criterion] for criterion in criteria
            },
            stype=self.stype,
        )


@set_module("mcda.matrices")
class AdditivePerformanceTable(PerformanceTable[QuantitativeScale]):
    """This class defines a performance table with additive values.

    :param data:
    :param scales:
        data scale(s) (one per column or one shared, will be inferred from data
        if absent using :meth:`Scale.fit`)
    :param aggregated_scale:
        output scale of row-wise aggregation (inferred if not provided)
    :param alternatives: if not set, inferred from `data`
    :param criteria:  if not set, inferred from `data`
    :param stype: scales type used
    :raise KeyError:
        * if some indexes are duplicated
        * if some columns are duplicated
    :raise TypeError: if `stype` and `scales` types mismatch

    .. note::
        This class is not intended for general use, it can though be the output
        of some algorithms.
    """

    def __init__(
        self,
        data,
        scales: Union[
            QuantitativeScale, Mapping[Any, QuantitativeScale], None
        ] = None,
        aggregated_scale: Union[QuantitativeScale, None] = None,
        alternatives: Union[List, None] = None,
        criteria: Union[List, None] = None,
        stype: Union[Type[QuantitativeScale], None] = None,
        **kwargs,
    ):
        self.aggregated_scale = aggregated_scale
        super().__init__(
            data,
            scales=scales,
            alternatives=alternatives,
            criteria=criteria,
            stype=stype,
            **kwargs,
        )

    @overload
    def sum(self, axis: None = None) -> float:  # pragma: nocover
        ...

    @overload
    def sum(
        self, axis: Literal[0, 1]
    ) -> CommensurableValues[QuantitativeScale]:  # pragma: nocover
        ...

    def sum(
        self, axis: Literal[0, 1] | None = None
    ) -> Union[CommensurableValues[QuantitativeScale], float]:
        """Return the sum of the data (all table, row or column-wise).

        :param axis:
            * 0: column-wise sum
            * 1: row-wise sum
            * ``None``: complete sum
        :return:

        .. warning::
            it will raise a :class:`TypeError` if data contains numeric
            and non-numeric values

        .. note::
            if `axis` is ``1``, :attr:`aggregated_scale` is used as the result
            scale
        """
        if axis == 1:
            return CommensurableValues(
                self.data.sum(axis=axis),
                scale=self.aggregated_scale,
                stype=QuantitativeScale,
            )
        return super().sum(axis=axis)


class VertexRowView(Mapping[Any, CommensurableValues[S]], Generic[S]):
    """This class defines a view of an adjacency value matrix per row.

    :param matrix:
    """

    def __init__(self, matrix: AdjacencyValueMatrix[S]):
        self._matrix: AdjacencyValueMatrix[S] = matrix

    @property
    def _data(self) -> DataFrame:
        """Dataframe of the value matrix"""
        return self._matrix.data

    @property
    def _stype(self) -> Type[S]:
        """Scale type of the value matrix"""
        return self._matrix.stype

    @property
    def _scale(self) -> S:
        """Scales of the adjacency value matrix"""
        return self._matrix.scale

    def __len__(self) -> int:
        """Number of vertices in the adjacency value matrix"""
        return len(self._matrix.vertices)

    def __getitem__(self, key: Any) -> CommensurableValues[S]:
        """Return values at row.

        :param key: vertex
        :raises KeyError: if `key` vertex doesn't exist
        :return:
        """
        return CommensurableValues[S](
            self._data.loc[key], self._scale, self._stype
        )

    def __iter__(self) -> Iterator[Any]:
        """Iterate on the vertices"""
        return iter(self._matrix.vertices)


class VertexColumnView(ColumnView[S], Generic[S]):
    """This class defines a view of an adjacency value matrix per column.

    :param matrix:
    """

    def __init__(self, matrix: AdjacencyValueMatrix[S]):
        self._matrix: AdjacencyValueMatrix[S] = matrix

    @property
    def _scale(self) -> S:
        """Scale of the adjacency value matrix"""
        return self._matrix.scale

    def __len__(self) -> int:
        """Number of vertices in the adjacency value matrix"""
        return len(self._matrix.vertices)

    def __getitem__(self, key: Any) -> CommensurableValues[S]:
        """Return values at column.

        :param key: vertex
        :raises KeyError: if `key` vertex doesn't exist
        :return:
        """
        return CommensurableValues[S](
            self._data[key], self._scale, self._stype
        )

    def __iter__(self) -> Iterator[Any]:
        """Iterate on the vertices"""
        return iter(self._matrix.vertices)


@set_module("mcda.matrices")
class AdjacencyValueMatrix(IAdjacencyMatrix, IValueMatrix[S], Generic[S]):
    """This class implements graphs as an adjacency value matrix.

    The adjacency matrix is represented internally by a
    :class:`pandas.DataFrame` with vertices as the indexes and columns.

    :param data: adjacency matrix in an array-like or dict-structure
    :param vertices:
    :param scale:
    :param stype: scales type used

    :raise KeyError:
        * if columns and rows have different sets of labels
        * if some vertices are duplicated
    :raise TypeError: if `stype` and `scale` type mismatch

    .. note:: the cells of the matrix can be of any type (not just numerics)
    """

    def __init__(
        self,
        data,
        vertices: Union[List, None] = None,
        scale: Union[S, None] = None,
        stype: Union[Type[S], None] = None,
        **kwargs,
    ):
        super().__init__(
            data, vertices=vertices, scales=scale, stype=stype, **kwargs
        )
        self.scale = self.union_bounds if scale is None else scale
        self.scales = {c: self.scale for c in self.vertices}

    @property
    def rows_values(self) -> Mapping[Any, CommensurableValues[S]]:
        """Iterator on the table alternatives values"""
        return VertexRowView[S](self)

    @property
    def columns_values(self) -> Mapping[Any, CommensurableValues[S]]:
        """Iterator on the table alternatives values"""
        return VertexColumnView[S](self)

    @property
    def to_numeric(self) -> AdjacencyValueMatrix[QuantitativeScale]:
        """Return numeric conversion of ordinal values.

        :raise TypeError: if :attr:`scales` are not ordinal
        """
        if self.is_numeric:
            return cast(AdjacencyValueMatrix[QuantitativeScale], self.copy())
        if not self.is_ordinal:
            raise TypeError("cannot convert to numerics nominal values")
        return AdjacencyValueMatrix(
            DataFrame(
                {
                    c: dict(v.to_numeric.data)
                    for c, v in self.columns_values.items()
                }
            ),
            scale=cast(OrdinalScale, self.scale).numeric,
        )

    @property
    def is_binary(self) -> bool:
        """Check whether adjacency value matrix is binary.

        :return:
        """
        return self.scale == DiscreteQuantitativeScale.binary()

    @property
    def transitive_closure(self) -> OutrankingMatrix:
        """Return transitive closure of matrix.

        :return:
        :raise TypeError: if matrix is not binary
        """
        if not self.is_binary:
            raise TypeError(
                "This property is only defined for binary matrices"
            )
        _m = floyd_warshall(csr_matrix(self.data.to_numpy())) < float("inf")
        m = DataFrame(
            _m,
            index=self.vertices,
            columns=self.vertices,
        )
        res = DataFrame(
            0,
            index=self.vertices,
            columns=self.vertices,
        )
        res[m] = 1
        return create_outranking_matrix(res)

    @property
    def transitive_reduction(self) -> OutrankingMatrix:
        """Return transitive reduction of matrix.

        :return:
        :raise TypeError: if matrix is not binary

        .. note:: this function can change the matrix shape
        """
        if not self.is_binary:
            raise TypeError(
                "This property is only defined for binary matrices"
            )
        matrix = self.graph_condensation
        path_matrix = floyd_warshall(csr_matrix(matrix.data.to_numpy())) == 1
        nodes = range(len(matrix.data))
        for u in nodes:
            for v in nodes:
                if path_matrix[u][v]:
                    for w in nodes:
                        if path_matrix[v][w]:
                            matrix.data.iloc[u, w] = 0
        return matrix

    @property
    def graph_condensation(self) -> OutrankingMatrix:
        """Return the condensation graph

        :return:
        :raise TypeError: if matrix is not binary

        .. note:: the matrix output by this function is acyclic

        .. warning:: this function changes the matrix shape
        """
        if not self.is_binary:
            raise TypeError(
                "This property is only defined for binary matrices"
            )

        n_components, labels = connected_components(
            self.data.to_numpy(), connection="strong"
        )
        # Return input matrix if no cycle found
        if n_components == len(self.data):
            return create_outranking_matrix(self.data)
        # Create new matrix with appropriate names for components
        components = []
        for component_index in range(n_components):
            component = tuple(
                self.data.index[labels == component_index].tolist()
            )
            components.append(component)
        new_matrix = DataFrame(False, index=components, columns=components)
        for component_a, component_b in product(
            range(n_components), range(n_components)
        ):
            if component_a != component_b:
                new_matrix.iloc[component_a, component_b] = (
                    self.data.iloc[
                        labels == component_a, labels == component_b
                    ]
                    .to_numpy()
                    .any()
                )

        return create_outranking_matrix(new_matrix.astype(int))

    @property
    def cycle_reduction_matrix(self) -> OutrankingMatrix:
        """Return matrix with cycles removed.

        :return:
        :raise TypeError: if matrix is not binary
        """
        if not self.is_binary:
            raise TypeError(
                "This property is only defined for binary matrices"
            )
        n_components, labels = connected_components(
            self.data.to_numpy(), connection="strong"
        )
        components = range(n_components)
        new_matrix = DataFrame(
            False, index=self.vertices, columns=self.vertices
        )
        for component_a, component_b in product(components, components):
            if component_a != component_b:
                new_matrix.loc[
                    labels == component_a, labels == component_b
                ] = (
                    self.data.loc[labels == component_a, labels == component_b]
                    .to_numpy()
                    .any()
                )
        return create_outranking_matrix(new_matrix.astype(int))

    @property
    def kernel(self) -> List:
        """Return the kernel of the graph if existing.

        The kernel is a *stable* and *dominant* set of nodes.
        Dominant nodes are the origin of edges, dominated ones are the target.

        :return: the kernel (if existing), else an empty list
        :raise TypeError: if matrix is not binary
        """
        if not self.is_binary:
            raise TypeError("can only compute kernel of binary matrix")
        graph = self.data.copy()
        # We remove self loops
        for v in self.vertices:
            graph.at[v, v] = 0
        kernel: Set = set()
        outsiders: Set = set()
        while not graph.empty:
            domination = (graph == 0).all(axis=0)
            dominators = domination[domination].index.tolist()
            if len(dominators) == 0:
                return []

            dominated = (graph == 1).loc[dominators].any(axis=0)
            neighbours = dominated[dominated].index.tolist()

            to_remove = dominators + neighbours
            graph = graph.drop(index=to_remove, columns=to_remove)
            kernel = kernel.union(dominators)
            outsiders = outsiders.union(neighbours)
        return list(kernel)

    def __mul__(self, other: Union[IMatrix, float]) -> AdjacencyValueMatrix:
        """Return product.

        :param other:
        :return:
        """
        coeff = other.data if isinstance(other, IMatrix) else other
        return AdjacencyValueMatrix(self.data * coeff)

    def __add__(self, other: Any) -> AdjacencyValueMatrix:
        """Return addition.

        :param other:
        :return:
        """
        added = other.data if isinstance(other, IMatrix) else other
        return AdjacencyValueMatrix(self.data + added)

    def __sub__(self, other: Any) -> AdjacencyValueMatrix:
        """Return subtraction.

        :param other:
        :return:
        """
        subtracted = other.data if isinstance(other, IMatrix) else other
        return AdjacencyValueMatrix(self.data - subtracted)

    def __or__(self, other: Any) -> AdjacencyValueMatrix[BinaryScale]:
        """Apply elementwise or.

        :param other: other binary adjacency matrix
        :raises TypeError:
            if both matrices are not binary :class:`AdjacencyValueMatrix`
        :return: result
        """
        if isinstance(other, AdjacencyValueMatrix):
            if self.is_binary and other.is_binary:
                res = cast(AdjacencyValueMatrix[BinaryScale], self.copy())
                res.data[other.data == 1] = 1
                return res
        raise TypeError(
            "can only do this operation between binary 'AdjacencyValueMatrix'"
        )

    def __and__(self, other: Any) -> AdjacencyValueMatrix[BinaryScale]:
        """Apply elementwise and.

        :param other: other binary adjacency matrix
        :raises TypeError:
            if both matrices are not binary :class:`AdjacencyValueMatrix`
        :return: result
        """
        if isinstance(other, AdjacencyValueMatrix):
            if self.is_binary and other.is_binary:
                res = cast(AdjacencyValueMatrix[BinaryScale], self.copy())
                res.data[other.data == 0] = 0
                return res
        raise TypeError(
            "can only do this operation between binary 'AdjacencyValueMatrix'"
        )

    def subtable(self, vertices: List) -> Self:
        """Return the subtable containing given vertices.

        :param vertices:
        :return:
        """
        return self.__class__(
            self.data.loc[vertices, vertices],
            scale=self.scale,
            stype=self.stype,
        )

    def copy(self) -> Self:
        """Return a copy of the object"""
        return self.__class__(
            self.data.copy(), scale=self.scale, stype=self.stype
        )

    @requires_graphviz
    def to_graph(
        self,
        edge_label: bool = False,
        self_loop: bool = False,
    ) -> Digraph:
        """Create a graph for adjacency matrix.

        This function creates a Graph using graphviz.

        :param edge_label: (optional) parameter to display the value of edges
        :param self_loop: (optional) parameter to display self looping edges
        :return: graph
        """
        graph = Digraph("graph", strict=True)
        graph.attr("node", shape="box")

        for v in self.vertices:
            graph.node(str(v))
        for a in self.data.index:
            for b in self.data.columns:
                if not self_loop and a == b:
                    continue
                elif self.data.at[a, b] == 0:
                    continue

                graph.edge(
                    str(a),
                    str(b),
                    label=str(self.data.at[a, b]) if edge_label else None,
                )
        return graph

    @requires_graphviz
    def plot(
        self,
        edge_label: bool = False,
        self_loop: bool = False,
    ) -> Digraph:  # pragma: nocover
        """Plot adjacency matrix as a graph.

        :param edge_label: (optional) parameter to display the value of edges
        :param self_loop: (optional) parameter to display self looping edges
        :return: graph

        .. note::
            You need an environment that will actually display the graph (such
            as a jupyter notebook), otherwise the function only returns the
            graph.
        """
        return self.to_graph(edge_label=edge_label, self_loop=self_loop)

    @requires_graphviz
    def save_plot(
        self,
        edge_label: bool = False,
        self_loop: bool = False,
    ) -> str:  # pragma: nocover
        """Plot adjacency matrix as a graph and save it.

        :param edge_label: (optional) parameter to display the value of edges
        :param self_loop: (optional) parameter to display self looping edges
        :return: file name where plot is saved
        """
        return self.plot(edge_label=edge_label, self_loop=self_loop).render()

    @classmethod
    def from_ordered_alternatives_groups(
        cls,
        categories: List[List],
    ) -> OutrankingMatrix:
        """Convert a ranking of categories of alternatives into an outranking
        matrix.

        :param categories:
            the ranked categories (each category is a list of alternatives)
        :return: outranking matrix
        """

        alternatives = [a for ll in categories for a in ll]
        res = create_outranking_matrix(0, vertices=alternatives)
        for category in categories:
            res.data.loc[category, category] = 1
            res.data.loc[
                category, alternatives[alternatives.index(category[-1]) + 1 :]
            ] = 1
        return res


OutrankingMatrix = AdjacencyValueMatrix[BinaryScale]
"""This type alias represents an outranking matrix"""


def create_outranking_matrix(
    data, vertices: Union[List, None] = None, **kwargs
) -> OutrankingMatrix:
    """Create an outranking matrix.

    :param data: adjacency matrix in an array-like or dict-structure
    :param vertices:

    :raise KeyError:
        * if columns and rows have different sets of labels
        * if some vertices are duplicated
    :raise TypeError: if `data` is not binary

    .. note::
        This function is just an easier way to create
        :class:`AdjacencyValueMatrix` with binary scale
    """
    kwargs.pop("stype", None)
    m = AdjacencyValueMatrix(
        data,
        vertices=vertices,
        scale=DiscreteQuantitativeScale.binary(),
        **kwargs,
    )
    if not m.is_within_scales:
        raise TypeError("outranking matrix data must be binary")
    return m
