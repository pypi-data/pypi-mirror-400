import unittest

from graphviz import Digraph
from pandas import DataFrame, Series
from pandas.testing import assert_frame_equal, assert_series_equal

from mcda.matrices import (
    AdditivePerformanceTable,
    AdjacencyValueMatrix,
    PartialValueMatrix,
    PerformanceTable,
    create_outranking_matrix,
    dataframe_equals,
)
from mcda.scales import (
    DiscreteQuantitativeScale,
    NominalScale,
    PreferenceDirection,
    QualitativeScale,
    QuantitativeScale,
)
from mcda.types import Scale
from mcda.values import CommensurableValues, Values


def test_dataframe_equals():
    df1 = DataFrame([[0, 1], [1, 1]], index=["a", "b"], columns=["c", "d"])
    df2 = DataFrame([[0, 1], [1, 1]], index=["a", "b"], columns=["c", "d"])
    df3 = DataFrame([[1, 1], [0, 1]], index=["b", "a"], columns=["c", "d"])
    df4 = DataFrame([[1, 0], [1, 1]], index=["a", "b"], columns=["d", "c"])
    df5 = DataFrame([[1, 1], [1, 0]], index=["b", "a"], columns=["d", "c"])
    df6 = DataFrame([[0, 1], [1, 1]], index=["aa", "b"], columns=["c", "d"])
    df7 = DataFrame([[0, 1], [1, 1]], index=["a", "b"], columns=["cc", "d"])
    assert dataframe_equals(df1, df2)
    assert dataframe_equals(df1, df3)
    assert dataframe_equals(df1, df4)
    assert dataframe_equals(df1, df5)
    assert not dataframe_equals(df1, df6)
    assert not dataframe_equals(df1, df7)


class PerformanceTableTestCase(unittest.TestCase):
    def setUp(self):
        self.alternatives = ["a01", "a02", "a03", "a04"]
        self.criteria = ["c01", "c02", "c03"]
        self.scales = {
            "c01": QualitativeScale(
                Series({"*": 1, "**": 2, "***": 3, "****": 4})
            ),
            "c02": QualitativeScale(
                Series({"Perfect": 1, "Good": 2, "Bad": 3}),
                PreferenceDirection.MIN,
            ),
            "c03": QuantitativeScale(
                0, 25000, preference_direction=PreferenceDirection.MIN
            ),
        }
        self.numeric_scales = {
            "c01": DiscreteQuantitativeScale([1, 2, 3, 4]),
            "c02": DiscreteQuantitativeScale(
                [1, 2, 3], preference_direction=PreferenceDirection.MIN
            ),
            "c03": QuantitativeScale(
                0, 25000, preference_direction=PreferenceDirection.MIN
            ),
        }
        self.df = DataFrame(
            [
                ["*", "Good", 5000],
                ["***", "Bad", 12000],
                ["**", "Perfect", 8500],
                ["****", "Good", 18635.2],
            ],
            index=self.alternatives,
            columns=self.criteria,
        )
        self.performance_table = PerformanceTable(
            [
                ["*", "Good", 5000],
                ["***", "Bad", 12000],
                ["**", "Perfect", 8500],
                ["****", "Good", 18635.2],
            ],
            scales=self.scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.numeric_table = PerformanceTable(
            [
                [1, 2, 5000],
                [3, 3, 12000],
                [2, 1, 8500],
                [4, 2, 18635.2],
            ],
            scales=self.numeric_scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.normal_table = PerformanceTable(
            [
                [0, 0.5, 1 - 5000 / 25000],
                [2 / 3, 0, 1 - 12000 / 25000],
                [1 / 3, 1, 1 - 8500 / 25000],
                [1, 0.5, 1 - 18635.2 / 25000],
            ],
            alternatives=self.alternatives,
            criteria=self.criteria,
            scales={
                criterion: QuantitativeScale.normal()
                for criterion in self.criteria
            },
        )
        self.bounds = {
            "c01": QuantitativeScale(1, 4),
            "c02": QuantitativeScale(1, 3),
            "c03": QuantitativeScale(5000, 18635.2),
        }

    def test_constructor(self):
        assert_frame_equal(self.performance_table.data, self.df)
        self.assertEqual(self.performance_table.scales, self.scales)
        table = PerformanceTable(self.numeric_table.data)
        assert_frame_equal(table.data, self.numeric_table.data)
        self.assertEqual(table.bounds, table.scales)
        self.assertRaises(
            KeyError,
            PerformanceTable,
            self.df,
            alternatives=[0] * len(self.alternatives),
        )
        self.assertRaises(
            KeyError,
            PerformanceTable,
            self.df,
            criteria=[0] * len(self.criteria),
        )
        with self.assertRaises(TypeError):
            PerformanceTable(
                self.performance_table.data,
                scales=self.scales,
                stype=QuantitativeScale,
            )
        with self.assertRaises(TypeError):
            PerformanceTable(
                self.normal_table.data,
                scales=QuantitativeScale.normal(),
                stype=NominalScale,
            )

    def test_equal(self):
        self.assertNotEqual(self.performance_table, self.df)
        self.assertNotEqual(self.performance_table, self.numeric_table)
        self.assertNotEqual(self.performance_table, 12)
        self.assertEqual(
            PerformanceTable(
                self.df, self.scales, self.alternatives, self.criteria
            ),
            self.performance_table,
        )

    def test_multiply(self):
        b = PerformanceTable(
            DataFrame(2, index=self.alternatives, columns=self.criteria)
        )
        assert_frame_equal(
            (self.numeric_table * b).data, 2 * self.numeric_table.data
        )
        assert_frame_equal(
            (self.numeric_table * 2).data, 2 * self.numeric_table.data
        )

    def test_add(self):
        b = PerformanceTable(
            DataFrame(2, index=self.alternatives, columns=self.criteria)
        )
        assert_frame_equal(
            (self.numeric_table + b).data, self.numeric_table.data + 2
        )
        assert_frame_equal(
            (self.numeric_table + 2).data, self.numeric_table.data + 2
        )

    def test_subtract(self):
        b = PerformanceTable(
            DataFrame(2, index=self.alternatives, columns=self.criteria)
        )
        assert_frame_equal(
            (self.numeric_table - b).data, self.numeric_table.data - 2
        )
        assert_frame_equal(
            (self.numeric_table - 2).data, self.numeric_table.data - 2
        )

    def test_columns(self):
        self.assertEqual(self.performance_table.columns, self.criteria)

    def test_rows(self):
        self.assertEqual(self.performance_table.rows, self.alternatives)

    def test_rows_values(self):
        self.assertEqual(
            len(self.performance_table.rows_values), len(self.alternatives)
        )
        self.assertEqual(
            list(self.performance_table.rows_values),
            self.performance_table.rows,
        )
        for (
            alternative,
            alternative_values,
        ) in self.performance_table.rows_values.items():
            self.assertEqual(
                alternative_values,
                Values(
                    self.performance_table.data.loc[alternative],
                    self.scales,
                ),
            )

    def test_columns_values(self):
        self.assertEqual(
            len(self.performance_table.columns_values), len(self.criteria)
        )
        self.assertEqual(
            list(self.performance_table.columns_values),
            self.performance_table.columns,
        )
        for (
            criterion,
            criterion_values,
        ) in self.performance_table.columns_values.items():
            self.assertEqual(
                criterion_values,
                CommensurableValues(
                    self.performance_table.data[criterion],
                    self.scales[criterion],
                ),
            )

    def test_criteria(self):
        self.assertEqual(self.performance_table.criteria, self.criteria)

    def test_alternatives(self):
        self.assertEqual(
            self.performance_table.alternatives, self.alternatives
        )

    def test_alternatives_values(self):
        self.assertEqual(
            len(self.performance_table.alternatives_values),
            len(self.alternatives),
        )
        self.assertEqual(
            list(self.performance_table.alternatives_values),
            self.performance_table.alternatives,
        )
        for (
            alternative,
            alternative_values,
        ) in self.performance_table.alternatives_values.items():
            self.assertEqual(
                alternative_values,
                Values(
                    self.performance_table.data.loc[alternative],
                    self.scales,
                ),
            )

    def test_criteria_values(self):
        self.assertEqual(
            len(self.performance_table.criteria_values), len(self.criteria)
        )
        self.assertEqual(
            list(self.performance_table.criteria_values),
            self.performance_table.criteria,
        )
        for (
            criterion,
            criterion_values,
        ) in self.performance_table.criteria_values.items():
            self.assertEqual(
                criterion_values,
                CommensurableValues(
                    self.performance_table.data[criterion],
                    self.scales[criterion],
                ),
            )

    def test_cell(self):
        self.assertEqual(self.performance_table.cell["a03", "c02"], "Perfect")

    def test_is_numeric(self):
        self.assertTrue(self.numeric_table.is_numeric)
        self.assertFalse(self.performance_table.is_numeric)

    def test_is_ordinal(self):
        self.assertTrue(self.performance_table.is_ordinal)
        self.assertFalse(
            PerformanceTable(self.performance_table.data).is_ordinal
        )

    def test_bounds(self):
        self.assertEqual(self.numeric_table.bounds, self.bounds)

    def test_union_bounds(self):
        expected = QuantitativeScale(1, 18635.2)
        self.assertEqual(self.numeric_table.union_bounds, expected)

    def test_to_numeric(self):
        self.assertEqual(self.performance_table.to_numeric, self.numeric_table)
        self.assertEqual(self.numeric_table.to_numeric, self.numeric_table)
        with self.assertRaises(TypeError):
            PerformanceTable(self.performance_table.data).to_numeric

    def test_efficients(self):
        efficients = self.performance_table.efficients
        self.assertEqual(efficients, self.performance_table.alternatives)
        table = PerformanceTable(
            [
                ["*", "Good", 10000],
                ["**", "Bad", 6500],
                ["***", "Perfect", 8500],
                ["****", "Good", 5000],
            ],
            scales=self.scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.assertEqual(table.efficients, ["a03", "a04"])

    def test_is_within_criteria_scales(self):
        self.assertTrue(self.performance_table.is_within_scales)
        table = PerformanceTable(
            [
                ["*", "Good", 5000],
                ["Stars", "Bad", 12000],
                ["**", "Perfect", 8500],
                ["****", "Good", 18635.2],
            ],
            scales=self.scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.assertFalse(table.is_within_scales)

    def test_within_criteria_scales(self):
        res = self.performance_table.within_scales
        self.assertTrue(res.all(None))
        table = PerformanceTable(
            [
                ["*", "Good", 5000],
                ["Stars", "Bad", 12000],
                ["**", "Perfect", 8500],
                ["****", "Good", 18635.2],
            ],
            scales=self.scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.assertFalse(table.within_scales.loc["a02", "c01"])

    def test_subtable(self):
        expected = PerformanceTable(
            [
                ["*", "Good", 5000],
                ["***", "Bad", 12000],
                ["**", "Perfect", 8500],
                ["****", "Good", 18635.2],
            ],
            scales=self.scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        expected = PerformanceTable(
            [
                ["*", "Good"],
                ["**", "Perfect"],
            ],
            scales={"c01": self.scales["c01"], "c02": self.scales["c02"]},
            alternatives=["a01", "a03"],
            criteria=["c01", "c02"],
        )
        res = self.performance_table.subtable(["a01", "a03"], ["c02", "c01"])
        self.assertEqual(res, expected)

        self.assertEqual(
            self.performance_table.subtable(), self.performance_table
        )

    def test_concat(self):
        result = PerformanceTable(
            [
                ["*", "Good", 5000],
                ["***", "Bad", 12000],
                ["**", "Perfect", 8500],
                ["****", "Good", 18635.2],
            ],
            scales=self.scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        other = PerformanceTable(
            [
                ["**", "Perfect", 7500],
                ["**", "Bad", 4500],
            ],
            scales=self.scales,
            alternatives=["a05", "a06"],
            criteria=self.criteria,
        )
        result = PerformanceTable(
            [
                ["*", "Good", 5000],
                ["***", "Bad", 12000],
                ["**", "Perfect", 8500],
                ["****", "Good", 18635.2],
                ["**", "Perfect", 7500],
                ["**", "Bad", 4500],
            ],
            scales=self.scales,
            alternatives=["a01", "a02", "a03", "a04", "a05", "a06"],
            criteria=self.criteria,
        )
        self.assertEqual(
            PerformanceTable.concat([self.performance_table, other]), result
        )
        new_scales = {
            "c04": QuantitativeScale(0, 100),
            "c05": QuantitativeScale(-100, 100),
        }
        other2 = PerformanceTable(
            [[12.5, -5], [50, -25], [15.5, 95], [0, -85]],
            scales=new_scales,
            alternatives=self.alternatives,
            criteria=new_scales.keys(),
        )
        result2 = PerformanceTable(
            [
                ["*", "Good", 5000, 12.5, -5],
                ["***", "Bad", 12000, 50, -25],
                ["**", "Perfect", 8500, 15.5, 95],
                ["****", "Good", 18635.2, 0, -85],
            ],
            scales=dict(**self.scales, **new_scales),
            alternatives=self.alternatives,
            criteria=self.criteria + list(new_scales.keys()),
        )
        self.assertEqual(
            PerformanceTable.concat([self.performance_table, other2], axis=1),
            result2,
        )
        self.assertRaises(
            ValueError,
            PerformanceTable.concat,
            [self.performance_table, other2],
            axis=2,
        )

    def test_copy(self):
        copy = self.performance_table.copy()
        self.assertEqual(self.performance_table, copy)
        copy.data.iloc[0, 0] = 0
        self.assertNotEqual(
            copy.data.iloc[0, 0], self.performance_table.data.iloc[0, 0]
        )

    def test_sum(self):
        with self.assertRaises(TypeError):
            self.performance_table.sum()
        assert_series_equal(
            self.numeric_table.sum(0).data,
            Series([10, 8, 44135.2], index=self.criteria),
        )
        assert_series_equal(
            self.numeric_table.sum(1).data,
            Series([5003, 12006, 8503, 18641.2], index=self.alternatives),
        )
        self.assertEqual(self.numeric_table.sum(), 44153.2)


class AdjacencyValueMatrixTestCase(unittest.TestCase):
    def setUp(self):
        self.vertices = ["a", "b", "c"]
        self.scale = QualitativeScale(Series({"a": 1, "b": 2, "c": 3}))
        self.quali_data = DataFrame(
            [["a", "b", "c"], ["a", "b", "c"], ["a", "b", "c"]]
        )
        self.matrix = AdjacencyValueMatrix(
            self.quali_data,
            vertices=self.vertices,
            scale=self.scale,
        )
        self.data = DataFrame([[0, 0.5, 1], [-1.2, 2.5, 0], [0.1, 0.2, 0.3]])
        self.numeric_matrix = AdjacencyValueMatrix(
            self.data, self.vertices, stype=DiscreteQuantitativeScale
        )
        self.outranking_matrix = AdjacencyValueMatrix(
            [
                [1, 0, 0, 0, 0],
                [1, 1, 1, 0, 0],
                [0, 1, 1, 1, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1],
            ],
            scale=DiscreteQuantitativeScale.binary(),
        )

    def test_constructor(self):
        assert_frame_equal(
            self.numeric_matrix.data,
            DataFrame(
                self.data.values, index=self.vertices, columns=self.vertices
            ),
        )
        self.assertEqual(self.numeric_matrix.vertices, self.vertices)
        self.assertEqual(
            AdjacencyValueMatrix(self.data).vertices,
            [*range(len(self.data))],
        )
        self.assertRaises(
            KeyError, AdjacencyValueMatrix, DataFrame([[0]], index=["a"])
        )
        self.assertRaises(
            KeyError,
            AdjacencyValueMatrix,
            DataFrame([[0, 1], [0, 1]]),
            vertices=[0, 0],
        )
        with self.assertRaises(TypeError):
            AdjacencyValueMatrix([["A"]], stype=DiscreteQuantitativeScale)

    def test_equal(self):
        self.assertNotEqual(self.numeric_matrix, self.data)
        self.assertNotEqual(self.numeric_matrix, self.matrix)
        self.assertNotEqual(self.numeric_matrix, 12)
        self.assertEqual(
            AdjacencyValueMatrix(
                self.quali_data, vertices=self.vertices, scale=self.scale
            ),
            self.matrix,
        )

    def test_multiply(self):
        b = AdjacencyValueMatrix(2, vertices=self.vertices)
        assert_frame_equal(
            (self.numeric_matrix * b).data, 2 * self.numeric_matrix.data
        )
        assert_frame_equal(
            (self.numeric_matrix * 2).data, 2 * self.numeric_matrix.data
        )

    def test_add(self):
        b = AdjacencyValueMatrix(2, vertices=self.vertices)
        assert_frame_equal(
            (self.numeric_matrix + b).data, self.numeric_matrix.data + 2
        )
        assert_frame_equal(
            (self.numeric_matrix + 2).data, self.numeric_matrix.data + 2
        )

    def test_subtract(self):
        b = AdjacencyValueMatrix(2, vertices=self.vertices)
        assert_frame_equal(
            (self.numeric_matrix - b).data, self.numeric_matrix.data - 2
        )
        assert_frame_equal(
            (self.numeric_matrix - 2).data, self.numeric_matrix.data - 2
        )

    def test_and(self):
        other = AdjacencyValueMatrix(
            [
                [1, 0, 1, 0, 0],
                [1, 1, 0, 0, 0],
                [0, 1, 1, 0, 0],
                [1, 0, 0, 1, 0],
                [0, 0, 1, 0, 1],
            ],
            scale=DiscreteQuantitativeScale.binary(),
        )
        expected = AdjacencyValueMatrix(
            [
                [1, 0, 0, 0, 0],
                [1, 1, 0, 0, 0],
                [0, 1, 1, 0, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1],
            ],
            scale=DiscreteQuantitativeScale.binary(),
        )
        self.assertEqual(self.outranking_matrix & other, expected)
        with self.assertRaises(TypeError):
            self.outranking_matrix & 10
        with self.assertRaises(TypeError):
            self.outranking_matrix & self.matrix
        with self.assertRaises(TypeError):
            self.matrix & other

    def test_or(self):
        other = AdjacencyValueMatrix(
            [
                [1, 0, 1, 0, 0],
                [1, 1, 0, 0, 0],
                [0, 1, 1, 0, 0],
                [1, 0, 0, 1, 0],
                [0, 0, 1, 0, 1],
            ],
            scale=DiscreteQuantitativeScale.binary(),
        )
        expected = AdjacencyValueMatrix(
            [
                [1, 0, 1, 0, 0],
                [1, 1, 1, 0, 0],
                [0, 1, 1, 1, 0],
                [1, 0, 0, 1, 0],
                [0, 0, 1, 0, 1],
            ],
            scale=DiscreteQuantitativeScale.binary(),
        )
        self.assertEqual(self.outranking_matrix | other, expected)
        with self.assertRaises(TypeError):
            self.outranking_matrix | 10
        with self.assertRaises(TypeError):
            self.outranking_matrix | self.matrix
        with self.assertRaises(TypeError):
            self.matrix & other

    def test_columns(self):
        self.assertEqual(self.numeric_matrix.columns, self.vertices)

    def test_rows(self):
        self.assertEqual(self.numeric_matrix.rows, self.vertices)

    def test_vertices(self):
        self.assertEqual(self.numeric_matrix.vertices, self.vertices)

    def test_rows_values(self):
        self.assertEqual(
            len(self.numeric_matrix.rows_values), len(self.vertices)
        )
        self.assertEqual(
            list(self.numeric_matrix.rows_values),
            self.numeric_matrix.vertices,
        )
        for (
            vertex,
            alternative_values,
        ) in self.numeric_matrix.rows_values.items():
            self.assertEqual(
                alternative_values,
                CommensurableValues(
                    self.numeric_matrix.data.loc[vertex],
                    self.numeric_matrix.scale,
                ),
            )

    def test_columns_values(self):
        self.assertEqual(
            len(self.numeric_matrix.columns_values), len(self.vertices)
        )
        self.assertEqual(
            list(self.numeric_matrix.columns_values),
            self.numeric_matrix.vertices,
        )
        for (
            vertex,
            criterion_values,
        ) in self.numeric_matrix.columns_values.items():
            self.assertEqual(
                criterion_values,
                CommensurableValues(
                    self.numeric_matrix.data[vertex],
                    self.numeric_matrix.scale,
                ),
            )

    def test_cell(self):
        self.assertEqual(self.matrix.cell["a", "c"], "c")

    def test_is_numeric(self):
        self.assertTrue(self.numeric_matrix.is_numeric)
        self.assertFalse(self.matrix.is_numeric)

    def test_is_ordinal(self):
        self.assertTrue(self.numeric_matrix.is_ordinal)
        self.assertTrue(self.matrix.is_ordinal)
        self.assertFalse(AdjacencyValueMatrix(self.matrix.data).is_ordinal)

    def test_bounds(self):
        bounds = {
            "a": DiscreteQuantitativeScale([0, -1.2, 0.1]),
            "b": DiscreteQuantitativeScale([0.5, 2.5, 0.2]),
            "c": DiscreteQuantitativeScale([1, 0, 0.3]),
        }
        self.assertEqual(self.numeric_matrix.bounds, bounds)

    def test_union_bounds(self):
        self.assertEqual(
            self.numeric_matrix.union_bounds, self.numeric_matrix.scale
        )

    def test_to_numeric(self):
        self.assertEqual(
            self.matrix.to_numeric,
            AdjacencyValueMatrix(
                [[1, 2, 3], [1, 2, 3], [1, 2, 3]],
                vertices=self.vertices,
                scale=self.matrix.scale.numeric,
            ),
        )
        self.assertEqual(self.numeric_matrix.to_numeric, self.numeric_matrix)
        with self.assertRaises(TypeError):
            AdjacencyValueMatrix(self.matrix.data).to_numeric

    def test_graph_condensation(self):
        with self.assertRaises(TypeError):
            self.matrix.graph_condensation
        expected = create_outranking_matrix(
            [[0, 0, 0, 0], [1, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            [
                (0,),
                (1, 2),
                (3,),
                (4,),
            ],
        )
        self.assertEqual(self.outranking_matrix.graph_condensation, expected)
        matrix = create_outranking_matrix(
            DataFrame([[0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1], [0, 0, 0, 0]])
        )
        self.assertEqual(matrix.graph_condensation, matrix)

    def test_transitive_reduction(self):
        with self.assertRaises(TypeError):
            self.matrix.transitive_reduction
        expected = create_outranking_matrix(
            [[0, 0, 0, 0], [1, 0, 1, 0], [0, 0, 0, 0], [0, 0, 0, 0]],
            [
                (0,),
                (1, 2),
                (3,),
                (4,),
            ],
        )
        self.assertEqual(self.outranking_matrix.transitive_reduction, expected)
        matrix = create_outranking_matrix(
            DataFrame([[0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1], [0, 0, 0, 0]])
        )
        expected_matrix = create_outranking_matrix(
            DataFrame([[0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 0, 0]])
        )
        self.assertEqual(matrix.transitive_reduction, expected_matrix)

    def test_transitive_closure(self):
        with self.assertRaises(TypeError):
            self.matrix.transitive_closure
        expected = create_outranking_matrix(
            [
                [1, 0, 0, 0, 0],
                [1, 1, 1, 1, 0],
                [1, 1, 1, 1, 0],
                [0, 0, 0, 1, 0],
                [0, 0, 0, 0, 1],
            ],
        )
        self.assertEqual(self.outranking_matrix.transitive_closure, expected)

    def test_cycle_reduction(self):
        with self.assertRaises(TypeError):
            self.matrix.cycle_reduction_matrix
        matrix = create_outranking_matrix(
            [
                [1, 1, 0, 1, 1, 0],
                [0, 1, 1, 1, 1, 0],
                [0, 1, 0, 1, 1, 0],
                [0, 0, 0, 1, 1, 0],
                [0, 0, 0, 1, 0, 1],
                [0, 0, 0, 1, 0, 0],
            ]
        )
        expected_matrix = create_outranking_matrix(
            [
                [0, 1, 1, 1, 1, 1],
                [0, 0, 0, 1, 1, 1],
                [0, 0, 0, 1, 1, 1],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
                [0, 0, 0, 0, 0, 0],
            ]
        )
        self.assertEqual(matrix.cycle_reduction_matrix, expected_matrix)

    def test_kernel(self):
        with self.assertRaises(TypeError):
            self.matrix.kernel
        self.assertEqual(self.outranking_matrix.kernel, [])
        self.assertEqual(
            set(self.outranking_matrix.cycle_reduction_matrix.kernel),
            {1, 2, 4},
        )

    def test_within_scales(self):
        assert_frame_equal(
            self.matrix.within_scales,
            DataFrame(True, index=self.vertices, columns=self.vertices),
        )
        matrix = self.matrix.copy()
        matrix.data.iloc[0, 0] = 10
        self.assertFalse(matrix.within_scales.iloc[0, 0])

    def test_is_within_scales(self):
        self.assertTrue(self.matrix.is_within_scales)
        matrix = self.matrix.copy()
        matrix.data.iloc[0, 0] = 10
        self.assertFalse(matrix.is_within_scales)

    def test_subtable(self):
        expected = AdjacencyValueMatrix(
            [["a", "b"], ["a", "b"]],
            vertices=self.vertices[0:2],
            scale=QualitativeScale(Series({"a": 1, "b": 2, "c": 3})),
        )
        self.assertEqual(self.matrix.subtable(self.vertices[0:2]), expected)

    def test_copy(self):
        copy = self.matrix.copy()
        self.assertEqual(self.matrix, copy)
        copy.data.iloc[0, 0] = 0
        self.assertNotEqual(copy.data.iloc[0, 0], self.matrix.data.iloc[0, 0])

    def test_to_graph(self):
        graph = Digraph("graph", strict=True)
        graph.attr("node", shape="box")
        graph.node("a")
        graph.node("b")
        graph.node("c")
        graph.edge("a", "b")
        graph.edge("a", "c")
        graph.edge("b", "a")
        graph.edge("c", "a")
        graph.edge("c", "b")
        self.assertEqual(self.numeric_matrix.to_graph().body, graph.body)
        graph2 = Digraph("graph", strict=True)
        graph2.attr("node", shape="box")
        graph2.node("a")
        graph2.node("b")
        graph2.node("c")
        graph2.edge("a", "b", label="0.5")
        graph2.edge("a", "c", label="1.0")
        graph2.edge("b", "a", label="-1.2")
        graph2.edge("b", "b", label="2.5")
        graph2.edge("c", "a", label="0.1")
        graph2.edge("c", "b", label="0.2")
        graph2.edge("c", "c", label="0.3")
        self.assertEqual(
            self.numeric_matrix.to_graph(edge_label=True, self_loop=True).body,
            graph2.body,
        )

    def test_sum(self):
        assert_series_equal(
            self.numeric_matrix.sum(0).data,
            Series([-1.1, 3.2, 1.3], index=self.vertices),
        )
        assert_series_equal(
            self.numeric_matrix.sum(1).data,
            Series([1.5, 1.3, 0.6], index=self.vertices),
        )
        self.assertEqual(self.numeric_matrix.sum(), 3.4000000000000004)

    def test_from_ranked_categories(self):
        categories = [[0, 1], [2], [3, 4]]
        expected = create_outranking_matrix(
            [
                [1, 1, 1, 1, 1],
                [1, 1, 1, 1, 1],
                [0, 0, 1, 1, 1],
                [0, 0, 0, 1, 1],
                [0, 0, 0, 1, 1],
            ]
        )
        self.assertEqual(
            AdjacencyValueMatrix.from_ordered_alternatives_groups(categories),
            expected,
        )


class PartialValueMatrixTest(unittest.TestCase):
    def setUp(self):
        self.vertices = ["a01", "a02"]
        self.criteria = ["c01", "c02", "c03"]
        self.scales = {
            "c01": QualitativeScale(
                Series({"*": 1, "**": 2, "***": 3, "****": 4})
            ),
            "c02": QualitativeScale(
                Series({"Perfect": 1, "Good": 2, "Bad": 3}),
                PreferenceDirection.MIN,
            ),
            "c03": QuantitativeScale(
                0, 25000, preference_direction=PreferenceDirection.MIN
            ),
        }
        self.numeric_scales = {
            "c01": DiscreteQuantitativeScale([1, 2, 3, 4]),
            "c02": DiscreteQuantitativeScale(
                [1, 2, 3], preference_direction=PreferenceDirection.MIN
            ),
            "c03": QuantitativeScale(
                0, 25000, preference_direction=PreferenceDirection.MIN
            ),
        }
        self.matrix = PartialValueMatrix(
            [
                [["**", "Bad", 10000], ["*", "Good", 5000]],
                [["***", "Perfect", 7500], ["****", "Perfect", 500]],
            ],
            vertices=self.vertices,
            criteria=self.criteria,
            scales=self.scales,
        )
        self.numeric_matrix = PartialValueMatrix(
            [
                [[2, 3, 10000], [1, 2, 5000]],
                [[3, 1, 7500], [4, 1, 500]],
            ],
            vertices=self.vertices,
            criteria=self.criteria,
            scales=self.numeric_scales,
        )

    def test_constructor(self):
        self.assertEqual(
            PartialValueMatrix(self.matrix.data, scales=self.scales),
            self.matrix,
        )
        matrix = PartialValueMatrix(
            [[[0, 1], [1, 0]], [[0, 1], [1, 0]]],
            stype=DiscreteQuantitativeScale,
        )
        matrix2 = PartialValueMatrix(
            DataFrame(
                [
                    [Series([0, 1]), Series([1, 0])],
                    [Series([0, 1]), Series([1, 0])],
                ]
            ),
            scales=DiscreteQuantitativeScale.binary(),
        )
        self.assertEqual(matrix, matrix2)
        with self.assertRaises(TypeError):
            PartialValueMatrix(
                self.matrix.data, scales=self.scales, stype=QuantitativeScale
            )
        with self.assertRaises(TypeError):
            PartialValueMatrix(
                self.matrix.data,
                scales=QuantitativeScale(),
                stype=QualitativeScale,
            )
        with self.assertRaises(KeyError):
            PartialValueMatrix(
                DataFrame([[Series([0])]], index=[0], columns=[1])
            )
        with self.assertRaises(KeyError):
            PartialValueMatrix(
                DataFrame(
                    [[Series([0]), Series([0])], [Series([0]), Series([0])]]
                ),
                vertices=[0, 0],
            )
        with self.assertRaises(KeyError):
            PartialValueMatrix(
                DataFrame([[Series([0, 0], index=[0, 0])]]),
            )

    def test_columns(self):
        self.assertEqual(self.matrix.columns, self.vertices)

    def test_rows(self):
        self.assertEqual(self.matrix.rows, self.vertices)

    def test_vertices(self):
        self.assertEqual(self.matrix.vertices, self.vertices)

    def test_criteria(self):
        self.assertEqual(self.matrix.criteria, self.criteria)

    def test_equal(self):
        self.assertNotEqual(self.matrix, 10)
        self.assertNotEqual(
            PartialValueMatrix([[[0, 1], [1, 0]], [[0, 1], [1, 0]]]),
            self.matrix,
        )
        self.assertNotEqual(
            PartialValueMatrix(
                [
                    [["**", "Bad", 10000], ["*", "Good", 5000]],
                    [["***", "Perfect", 750], ["****", "Perfect", 500]],
                ],
                vertices=self.vertices,
                criteria=self.criteria,
                scales=self.scales,
            ),
            self.matrix,
        )
        self.assertEqual(
            PartialValueMatrix(
                self.matrix.data,
                scales=self.scales,
            ),
            self.matrix,
        )

    def test_bounds(self):
        matrix = PartialValueMatrix(self.matrix.data, stype=Scale)
        expected = {
            "c01": NominalScale(["*", "**", "***", "****"]),
            "c02": NominalScale(["Perfect", "Good", "Bad"]),
            "c03": QuantitativeScale(500, 10000),
        }
        self.assertEqual(matrix.bounds, expected)

    def test_row_matrices(self):
        expected = {
            "a01": PerformanceTable(
                [["**", "Bad", 10000], ["*", "Good", 5000]],
                alternatives=self.vertices,
                criteria=self.criteria,
                scales=self.scales,
            ),
            "a02": PerformanceTable(
                [["***", "Perfect", 7500], ["****", "Perfect", 500]],
                alternatives=self.vertices,
                criteria=self.criteria,
                scales=self.scales,
            ),
        }
        self.assertEqual(
            len(self.numeric_matrix.row_matrices), len(self.vertices)
        )
        self.assertEqual(
            list(self.numeric_matrix.row_matrices),
            self.numeric_matrix.vertices,
        )
        self.assertEqual(self.matrix.row_matrices, expected)

    def test_column_matrices(self):
        expected = {
            "a01": PerformanceTable(
                [["**", "Bad", 10000], ["***", "Perfect", 7500]],
                alternatives=self.vertices,
                criteria=self.criteria,
                scales=self.scales,
            ),
            "a02": PerformanceTable(
                [["*", "Good", 5000], ["****", "Perfect", 500]],
                alternatives=self.vertices,
                criteria=self.criteria,
                scales=self.scales,
            ),
        }
        self.assertEqual(
            len(self.numeric_matrix.column_matrices), len(self.vertices)
        )
        self.assertEqual(
            list(self.numeric_matrix.column_matrices),
            self.numeric_matrix.vertices,
        )
        self.assertEqual(self.matrix.column_matrices, expected)

    def test_criteria_matrices(self):
        expected = {
            "c01": AdjacencyValueMatrix(
                [
                    ["**", "*"],
                    ["***", "****"],
                ],
                vertices=self.vertices,
                scale=self.scales["c01"],
            ),
            "c02": AdjacencyValueMatrix(
                [
                    ["Bad", "Good"],
                    ["Perfect", "Perfect"],
                ],
                vertices=self.vertices,
                scale=self.scales["c02"],
            ),
            "c03": AdjacencyValueMatrix(
                [
                    [10000, 5000],
                    [7500, 500],
                ],
                vertices=self.vertices,
                scale=self.scales["c03"],
            ),
        }
        self.assertEqual(
            len(self.numeric_matrix.criteria_matrices), len(self.criteria)
        )
        self.assertEqual(
            list(self.numeric_matrix.criteria_matrices),
            self.numeric_matrix.criteria,
        )
        self.assertEqual(self.matrix.criteria_matrices, expected)

    def test_cell(self):
        self.assertEqual(
            self.matrix.cell["a01", "a02"],
            Values(
                {"c01": "*", "c02": "Good", "c03": 5000}, scales=self.scales
            ),
        )

    def test_within_scales(self):
        expected = DataFrame(
            [
                [
                    Series([True, True, True], index=self.criteria),
                    Series([True, True, True], index=self.criteria),
                ],
                [
                    Series([True, True, True], index=self.criteria),
                    Series([True, True, True], index=self.criteria),
                ],
            ],
            index=self.vertices,
            columns=self.vertices,
        )
        assert_frame_equal(self.matrix.within_scales, expected)

    def test_is_within_scales(self):
        self.assertTrue(self.matrix.is_within_scales)

    def test_is_numeric(self):
        self.assertFalse(self.matrix.is_numeric)
        self.assertTrue(self.numeric_matrix.is_numeric)

    def test_is_ordinal(self):
        self.assertTrue(self.matrix.is_ordinal)
        self.assertFalse(PartialValueMatrix(self.matrix.data).is_ordinal)

    def test_to_numeric(self):
        self.assertEqual(self.matrix.to_numeric, self.numeric_matrix)
        self.assertEqual(self.numeric_matrix.to_numeric, self.numeric_matrix)
        with self.assertRaises(TypeError):
            PartialValueMatrix(self.matrix.data).to_numeric

    def test_copy(self):
        copy = self.matrix.copy()
        self.assertEqual(self.matrix, copy)
        copy.scales = copy.bounds
        self.assertNotEqual(self.matrix, copy)

    def test_subtable(self):
        expected1 = PartialValueMatrix(
            [
                [["**", 10000], ["*", 5000]],
                [["***", 7500], ["****", 500]],
            ],
            vertices=self.vertices,
            criteria=["c01", "c03"],
            scales={c: self.scales[c] for c in ["c01", "c03"]},
        )
        self.assertEqual(
            self.matrix.subtable(criteria=["c01", "c03"]), expected1
        )
        expected2 = PartialValueMatrix(
            [
                [["****", "Perfect", 500]],
            ],
            vertices=["a02"],
            criteria=self.criteria,
            scales=self.scales,
        )
        self.assertEqual(self.matrix.subtable(vertices=["a02"]), expected2)


class AdditivePerformanceTableTestCase(unittest.TestCase):
    def setUp(self):
        self.alternatives = ["a01", "a02", "a03", "a04"]
        self.criteria = ["c01", "c02", "c03"]
        self.numeric_scales = {
            "c01": DiscreteQuantitativeScale([1, 2, 3, 4]),
            "c02": DiscreteQuantitativeScale(
                [1, 2, 3], preference_direction=PreferenceDirection.MIN
            ),
            "c03": QuantitativeScale(
                0, 25000, preference_direction=PreferenceDirection.MIN
            ),
        }
        self.numeric_table = AdditivePerformanceTable(
            [
                [1, 2, 5000],
                [3, 3, 12000],
                [2, 1, 8500],
                [4, 2, 18635.2],
            ],
            scales=self.numeric_scales,
            aggregated_scale=QuantitativeScale(0, 50000),
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.normal_table = AdditivePerformanceTable(
            [
                [0, 0.5, 1 - 5000 / 25000],
                [2 / 3, 0, 1 - 12000 / 25000],
                [1 / 3, 1, 1 - 8500 / 25000],
                [1, 0.5, 1 - 18635.2 / 25000],
            ],
            alternatives=self.alternatives,
            criteria=self.criteria,
            scales={
                criterion: QuantitativeScale.normal()
                for criterion in self.criteria
            },
        )
        self.bounds = {
            "c01": QuantitativeScale(1, 4),
            "c02": QuantitativeScale(1, 3),
            "c03": QuantitativeScale(5000, 18635.2),
        }

    def test_constructor(self):
        table = AdditivePerformanceTable(self.numeric_table.data)
        assert_frame_equal(table.data, self.numeric_table.data)
        self.assertEqual(table.bounds, table.scales)
        self.assertRaises(
            KeyError,
            AdditivePerformanceTable,
            self.numeric_table.data,
            alternatives=[0] * len(self.alternatives),
        )
        self.assertRaises(
            KeyError,
            AdditivePerformanceTable,
            self.numeric_table.data,
            criteria=[0] * len(self.criteria),
        )
        with self.assertRaises(TypeError):
            AdditivePerformanceTable(
                self.normal_table.data,
                scales=QuantitativeScale.normal(),
                stype=NominalScale,
            )

    def test_equal(self):
        self.assertNotEqual(self.numeric_table, self.numeric_table.data)
        self.assertNotEqual(self.numeric_table, self.normal_table)
        self.assertNotEqual(self.numeric_table, 12)
        self.assertEqual(
            AdditivePerformanceTable(
                self.numeric_table.data,
                self.numeric_scales,
            ),
            self.numeric_table,
        )

    def test_multiply(self):
        b = PerformanceTable(
            DataFrame(2, index=self.alternatives, columns=self.criteria)
        )
        assert_frame_equal(
            (self.numeric_table * b).data, 2 * self.numeric_table.data
        )
        assert_frame_equal(
            (self.numeric_table * 2).data, 2 * self.numeric_table.data
        )

    def test_add(self):
        b = PerformanceTable(
            DataFrame(2, index=self.alternatives, columns=self.criteria)
        )
        assert_frame_equal(
            (self.numeric_table + b).data, self.numeric_table.data + 2
        )
        assert_frame_equal(
            (self.numeric_table + 2).data, self.numeric_table.data + 2
        )

    def test_subtract(self):
        b = PerformanceTable(
            DataFrame(2, index=self.alternatives, columns=self.criteria)
        )
        assert_frame_equal(
            (self.numeric_table - b).data, self.numeric_table.data - 2
        )
        assert_frame_equal(
            (self.numeric_table - 2).data, self.numeric_table.data - 2
        )

    def test_columns(self):
        self.assertEqual(self.numeric_table.columns, self.criteria)

    def test_rows(self):
        self.assertEqual(self.numeric_table.rows, self.alternatives)

    def test_rows_values(self):
        self.assertEqual(
            len(self.numeric_table.rows_values), len(self.alternatives)
        )
        self.assertEqual(
            list(self.numeric_table.rows_values),
            self.numeric_table.rows,
        )
        for (
            alternative,
            alternative_values,
        ) in self.numeric_table.rows_values.items():
            self.assertEqual(
                alternative_values,
                Values(
                    self.numeric_table.data.loc[alternative],
                    self.numeric_scales,
                ),
            )

    def test_columns_values(self):
        self.assertEqual(
            len(self.numeric_table.columns_values), len(self.criteria)
        )
        self.assertEqual(
            list(self.numeric_table.columns_values),
            self.numeric_table.columns,
        )
        for (
            criterion,
            criterion_values,
        ) in self.numeric_table.columns_values.items():
            self.assertEqual(
                criterion_values,
                CommensurableValues(
                    self.numeric_table.data[criterion],
                    self.numeric_scales[criterion],
                ),
            )

    def test_criteria(self):
        self.assertEqual(self.numeric_table.criteria, self.criteria)

    def test_alternatives(self):
        self.assertEqual(self.numeric_table.alternatives, self.alternatives)

    def test_alternatives_values(self):
        self.assertEqual(
            len(self.numeric_table.alternatives_values), len(self.alternatives)
        )
        self.assertEqual(
            list(self.numeric_table.alternatives_values),
            self.numeric_table.alternatives,
        )
        for (
            alternative,
            alternative_values,
        ) in self.numeric_table.alternatives_values.items():
            self.assertEqual(
                alternative_values,
                Values(
                    self.numeric_table.data.loc[alternative],
                    self.numeric_scales,
                ),
            )

    def test_criteria_values(self):
        self.assertEqual(
            len(self.numeric_table.criteria_values), len(self.criteria)
        )
        self.assertEqual(
            list(self.numeric_table.criteria_values),
            self.numeric_table.criteria,
        )
        for (
            criterion,
            criterion_values,
        ) in self.numeric_table.criteria_values.items():
            self.assertEqual(
                criterion_values,
                CommensurableValues(
                    self.numeric_table.data[criterion],
                    self.numeric_scales[criterion],
                ),
            )

    def test_at(self):
        self.assertEqual(self.numeric_table.cell["a03", "c02"], 1)

    def test_is_numeric(self):
        self.assertTrue(self.numeric_table.is_numeric)

    def test_is_ordinal(self):
        self.assertTrue(self.numeric_table.is_ordinal)

    def test_bounds(self):
        self.assertEqual(self.numeric_table.bounds, self.bounds)

    def test_union_bounds(self):
        expected = QuantitativeScale(1, 18635.2)
        self.assertEqual(self.numeric_table.union_bounds, expected)

    def test_to_numeric(self):
        self.assertEqual(self.numeric_table.to_numeric, self.numeric_table)

    def test_efficients(self):
        efficients = self.numeric_table.efficients
        self.assertEqual(efficients, self.numeric_table.alternatives)
        table = AdditivePerformanceTable(
            [
                [1, 2, 10000],
                [2, 3, 6500],
                [3, 1, 8500],
                [4, 2, 5000],
            ],
            scales=self.numeric_scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.assertEqual(table.efficients, ["a03", "a04"])

    def test_is_within_criteria_scales(self):
        self.assertTrue(self.numeric_table.is_within_scales)
        table = AdditivePerformanceTable(
            [
                [1, 2, 5000],
                [5, 3, 12000],
                [2, 1, 8500],
                [4, 2, 18635.2],
            ],
            scales=self.numeric_scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.assertFalse(table.is_within_scales)

    def test_within_criteria_scales(self):
        res = self.numeric_table.within_scales
        self.assertTrue(res.all(None))
        table = AdditivePerformanceTable(
            [
                [1, 2, 5000],
                [5, 3, 12000],
                [2, 1, 8500],
                [4, 2, 18635.2],
            ],
            scales=self.numeric_scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.assertFalse(table.within_scales.loc["a02", "c01"])

    def test_subtable(self):
        expected = AdditivePerformanceTable(
            [
                [2, 1],
                [1, 2],
            ],
            scales={
                "c01": self.numeric_scales["c01"],
                "c02": self.numeric_scales["c02"],
            },
            alternatives=["a01", "a03"],
            criteria=["c02", "c01"],
        )
        res = self.numeric_table.subtable(["a01", "a03"], ["c02", "c01"])
        self.assertEqual(res, expected)

        self.assertEqual(self.numeric_table.subtable(), self.numeric_table)

    def test_concat(self):
        other = AdditivePerformanceTable(
            [
                [2, 1, 7500],
                [2, 3, 4500],
            ],
            scales=self.numeric_scales,
            alternatives=["a05", "a06"],
            criteria=self.criteria,
        )
        result = AdditivePerformanceTable(
            [
                [1, 2, 5000],
                [3, 3, 12000],
                [2, 1, 8500],
                [4, 2, 18635.2],
                [2, 1, 7500],
                [2, 3, 4500],
            ],
            scales=self.numeric_scales,
            alternatives=["a01", "a02", "a03", "a04", "a05", "a06"],
            criteria=self.criteria,
        )
        self.assertEqual(
            AdditivePerformanceTable.concat([self.numeric_table, other]),
            result,
        )
        new_scales = {
            "c04": QuantitativeScale(0, 100),
            "c05": QuantitativeScale(-100, 100),
        }
        other2 = AdditivePerformanceTable(
            [[12.5, -5], [50, -25], [15.5, 95], [0, -85]],
            scales=new_scales,
            alternatives=self.alternatives,
            criteria=new_scales.keys(),
        )
        result2 = AdditivePerformanceTable(
            [
                [1, 2, 5000, 12.5, -5],
                [3, 3, 12000, 50, -25],
                [2, 1, 8500, 15.5, 95],
                [4, 2, 18635.2, 0, -85],
            ],
            scales=dict(**self.numeric_scales, **new_scales),
            alternatives=self.alternatives,
            criteria=self.criteria + list(new_scales.keys()),
        )
        self.assertEqual(
            AdditivePerformanceTable.concat(
                [self.numeric_table, other2], axis=1
            ),
            result2,
        )
        self.assertRaises(
            ValueError,
            AdditivePerformanceTable.concat,
            [self.numeric_table, other2],
            axis=2,
        )

    def test_copy(self):
        copy = self.numeric_table.copy()
        self.assertEqual(self.numeric_table, copy)
        copy.data.iloc[0, 0] = 0
        self.assertNotEqual(
            copy.data.iloc[0, 0], self.numeric_table.data.iloc[0, 0]
        )

    def test_sum(self):
        assert_series_equal(
            self.numeric_table.sum(0).data,
            Series([10, 8, 44135.2], index=self.criteria),
        )
        self.assertEqual(
            self.numeric_table.sum(1),
            CommensurableValues(
                Series([5003, 12006, 8503, 18641.2], index=self.alternatives),
                scale=self.numeric_table.aggregated_scale,
            ),
        )
        self.assertEqual(self.numeric_table.sum(), 44153.2)


class CreateOutrankingMatrixTestCase(unittest.TestCase):
    def test_create_outranking_matrix(self):
        vertices = ["a01", "a02", "a03", "a04"]
        self.assertEqual(
            create_outranking_matrix(
                DataFrame(
                    [[0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1], [0, 0, 0, 0]],
                    index=vertices,
                    columns=vertices,
                )
            ),
            create_outranking_matrix(
                DataFrame(
                    [[0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1], [0, 0, 0, 0]],
                ),
                vertices=vertices,
            ),
        )
        self.assertRaises(
            TypeError, create_outranking_matrix, DataFrame([0.2])
        )
        with self.assertRaises(KeyError):
            create_outranking_matrix(DataFrame([[2]], index=[0], columns=[1]))
        with self.assertRaises(KeyError):
            create_outranking_matrix(
                DataFrame(
                    [[0, 1, 1, 1], [0, 0, 1, 1], [0, 0, 0, 1], [0, 0, 0, 0]],
                ),
                vertices=[0, 1, 0, 2],
            )
