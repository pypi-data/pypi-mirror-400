import unittest

from pandas import Series
from pandas.testing import assert_frame_equal, assert_series_equal

from mcda.matrices import PartialValueMatrix, PerformanceTable
from mcda.scales import (
    NominalScale,
    PreferenceDirection,
    QualitativeScale,
    QuantitativeScale,
)
from mcda.transformers import (
    ClosestTransformer,
    Transformer,
    normalize,
    transform,
)


class TestTransformer(unittest.TestCase):
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
        self.out_scale = QuantitativeScale(0, 10)
        self.out_scales = {c: self.out_scale for c in self.criteria}
        self.partial_values = PartialValueMatrix(
            [[["*", "Good", 5000]]], criteria=self.criteria, scales=self.scales
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
        self.out_table = PerformanceTable(
            [
                [0, 5, 8],
                [(2 / 3) * 10, 0, 5.2],
                [(1 / 3) * 10, 10, 6.6],
                [10, 5, (1 - (18635.2 / 25000)) * 10],
            ],
            scales=self.out_scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.out_partial_values = PartialValueMatrix(
            [[[0, 5, 8]]], criteria=self.criteria, scales=self.out_scales
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
        self.normal_partial_values = PartialValueMatrix(
            [[[0, 0.5, 1 - 5000 / 25000]]],
            criteria=self.criteria,
            scales=QuantitativeScale.normal(),
        )
        self.klass = Transformer

    def test_transform_one(self):
        self.assertEqual(
            self.klass.transform(
                self.performance_table.data.at["a01", "c01"],
                self.out_scales["c01"],
                self.scales["c01"],
            ),
            self.out_table.data.at["a01", "c01"],
        )

    def test_normalize_one(self):
        self.assertEqual(
            self.klass.normalize(
                self.performance_table.data.at["a01", "c01"],
                self.scales["c01"],
            ),
            self.normal_table.data.at["a01", "c01"],
        )

    def test_transform_values(self):
        res = self.klass.transform(
            self.performance_table.alternatives_values["a01"],
            self.out_scales,
        )
        self.assertEqual(
            self.klass.transform(
                self.performance_table.alternatives_values["a01"],
                self.out_scales,
            ),
            res,
        )
        self.assertEqual(
            res,
            self.out_table.alternatives_values["a01"],
        )

    def test_normalize_values(self):
        self.assertEqual(
            self.klass.normalize(
                self.performance_table.alternatives_values["a01"],
            ),
            self.normal_table.alternatives_values["a01"],
        )

    def test_transform_series(self):
        res = self.klass.transform(
            self.performance_table.alternatives_values["a01"].data,
            self.out_scales,
            self.scales,
        )
        assert_series_equal(
            self.klass.transform(
                self.performance_table.alternatives_values["a01"].data,
                self.out_scale,
                self.scales,
            ),
            res,
        )
        assert_series_equal(
            res,
            self.out_table.alternatives_values["a01"].data,
        )

    def test_normalize_series(self):
        assert_series_equal(
            self.klass.normalize(
                self.performance_table.alternatives_values["a01"].data,
                self.scales,
            ),
            self.normal_table.alternatives_values["a01"].data,
        )

    def test_transform_criteria_values(self):
        self.assertEqual(
            self.klass.transform(
                self.performance_table.criteria_values["c01"],
                self.out_scale,
            ),
            self.out_table.criteria_values["c01"],
        )

    def test_normalize_criteria_values(self):
        self.assertEqual(
            self.klass.normalize(
                self.performance_table.criteria_values["c01"],
            ),
            self.normal_table.criteria_values["c01"],
        )

    def test_transform_performance_table(self):
        res = self.klass.transform(self.performance_table, self.out_scales)
        self.assertEqual(
            self.klass.transform(self.performance_table, self.out_scale),
            res,
        )
        self.assertEqual(res, self.out_table)

    def test_normalize_performance_table(self):
        self.assertEqual(
            self.klass.normalize(self.performance_table), self.normal_table
        )

    def test_transform_dataframe(self):
        res = self.klass.transform(
            self.performance_table.data, self.out_scales, self.scales
        )
        assert_frame_equal(
            self.klass.transform(
                self.performance_table.data, self.out_scale, self.scales
            ),
            res,
        )
        assert_frame_equal(res, self.out_table.data, check_dtype=False)

    def test_normalize_dataframe(self):
        assert_frame_equal(
            self.klass.normalize(self.performance_table.data, self.scales),
            self.normal_table.data,
        )

    def test_transform_partial_values(self):
        res = self.klass.transform(self.partial_values, self.out_scales)
        self.assertEqual(
            self.klass.transform(self.partial_values, self.out_scale), res
        )
        self.assertEqual(res, self.out_partial_values)

    def test_normalize_partial_values(self):
        self.assertEqual(
            self.klass.normalize(
                self.partial_values,
            ),
            self.normal_partial_values,
        )

    def test_transform_adjacency_values(self):
        self.assertEqual(
            self.klass.transform(
                self.partial_values.criteria_matrices["c01"], self.out_scale
            ),
            self.out_partial_values.criteria_matrices["c01"],
        )

    def test_normalize_adjacency_values(self):
        self.assertEqual(
            self.klass.normalize(self.partial_values.criteria_matrices["c01"]),
            self.normal_partial_values.criteria_matrices["c01"],
        )

    def test_transform_error(self):
        with self.assertRaises(TypeError):
            self.klass.transform(150)
        with self.assertRaises(TypeError):
            self.klass.transform("a", QuantitativeScale(), NominalScale(["a"]))
        with self.assertRaises(TypeError):
            self.klass.transform(150, NominalScale(["a"]), QuantitativeScale())

    def test_normalize_error(self):
        with self.assertRaises(TypeError):
            self.klass.normalize(150)
        with self.assertRaises(TypeError):
            self.klass.normalize("a", NominalScale(["a"]))


class TestTransformNormalize(unittest.TestCase):
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
        self.out_scale = QuantitativeScale(0, 10)
        self.out_scales = {c: self.out_scale for c in self.criteria}
        self.partial_values = PartialValueMatrix(
            [[["*", "Good", 5000]]], criteria=self.criteria, scales=self.scales
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
        self.out_table = PerformanceTable(
            [
                [0, 5, 8],
                [(2 / 3) * 10, 0, 5.2],
                [(1 / 3) * 10, 10, 6.6],
                [10, 5, (1 - (18635.2 / 25000)) * 10],
            ],
            scales=self.out_scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.out_partial_values = PartialValueMatrix(
            [[[0, 5, 8]]], criteria=self.criteria, scales=self.out_scales
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
        self.normal_partial_values = PartialValueMatrix(
            [[[0, 0.5, 1 - 5000 / 25000]]],
            criteria=self.criteria,
            scales=QuantitativeScale.normal(),
        )

    def test_transform_one(self):
        self.assertEqual(
            transform(
                self.performance_table.data.at["a01", "c01"],
                self.out_scales["c01"],
                self.scales["c01"],
            ),
            self.out_table.data.at["a01", "c01"],
        )

    def test_normalize_one(self):
        self.assertEqual(
            normalize(
                self.performance_table.data.at["a01", "c01"],
                self.scales["c01"],
            ),
            self.normal_table.data.at["a01", "c01"],
        )

    def test_transform_values(self):
        res = transform(
            self.performance_table.alternatives_values["a01"],
            self.out_scales,
        )
        self.assertEqual(
            transform(
                self.performance_table.alternatives_values["a01"],
                self.out_scale,
            ),
            res,
        )
        self.assertEqual(
            res,
            self.out_table.alternatives_values["a01"],
        )

    def test_normalize_values(self):
        self.assertEqual(
            normalize(
                self.performance_table.alternatives_values["a01"],
            ),
            self.normal_table.alternatives_values["a01"],
        )

    def test_transform_series(self):
        res = transform(
            self.performance_table.alternatives_values["a01"].data,
            self.out_scales,
            self.scales,
        )
        assert_series_equal(
            transform(
                self.performance_table.alternatives_values["a01"].data,
                self.out_scale,
                self.scales,
            ),
            res,
        )
        assert_series_equal(
            res,
            self.out_table.alternatives_values["a01"].data,
        )

    def test_normalize_series(self):
        assert_series_equal(
            normalize(
                self.performance_table.alternatives_values["a01"].data,
                self.scales,
            ),
            self.normal_table.alternatives_values["a01"].data,
        )

    def test_transform_criteria_values(self):
        self.assertEqual(
            transform(
                self.performance_table.criteria_values["c01"],
                self.out_scale,
            ),
            self.out_table.criteria_values["c01"],
        )

    def test_normalize_criteria_values(self):
        self.assertEqual(
            normalize(
                self.performance_table.criteria_values["c01"],
            ),
            self.normal_table.criteria_values["c01"],
        )

    def test_transform_performance_table(self):
        res = transform(self.performance_table, self.out_scales)
        self.assertEqual(
            transform(self.performance_table, self.out_scale),
            res,
        )
        self.assertEqual(res, self.out_table)

    def test_normalize_performance_table(self):
        self.assertEqual(normalize(self.performance_table), self.normal_table)

    def test_transform_dataframe(self):
        res = transform(
            self.performance_table.data, self.out_scales, self.scales
        )
        assert_frame_equal(
            transform(
                self.performance_table.data, self.out_scale, self.scales
            ),
            res,
        )
        assert_frame_equal(res, self.out_table.data, check_dtype=False)

    def test_normalize_dataframe(self):
        assert_frame_equal(
            normalize(self.performance_table.data, self.scales),
            self.normal_table.data,
        )

    def test_transform_partial_values(self):
        res = transform(self.partial_values, self.out_scales)
        self.assertEqual(transform(self.partial_values, self.out_scale), res)
        self.assertEqual(res, self.out_partial_values)

    def test_normalize_partial_values(self):
        self.assertEqual(
            normalize(
                self.partial_values,
            ),
            self.normal_partial_values,
        )

    def test_transform_adjacency_values(self):
        self.assertEqual(
            transform(
                self.partial_values.criteria_matrices["c01"], self.out_scale
            ),
            self.out_partial_values.criteria_matrices["c01"],
        )

    def test_normalize_adjacency_values(self):
        self.assertEqual(
            normalize(self.partial_values.criteria_matrices["c01"]),
            self.normal_partial_values.criteria_matrices["c01"],
        )

    def test_transform_error(self):
        with self.assertRaises(TypeError):
            transform(150, QuantitativeScale())
        with self.assertRaises(TypeError):
            transform("a", QuantitativeScale(), NominalScale(["a"]))
        with self.assertRaises(TypeError):
            transform(150, NominalScale(["a"]), QuantitativeScale())

    def test_normalize_error(self):
        with self.assertRaises(TypeError):
            normalize(150)
        with self.assertRaises(TypeError):
            normalize("a", NominalScale(["a"]))


class TestClosestTransformer(TestTransformer):
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
        self.out_scale = QualitativeScale(
            Series({"Perfect": 1, "Good": 2, "Bad": 3}),
            PreferenceDirection.MIN,
        )
        self.out_scales = {c: self.out_scale for c in self.criteria}
        self.partial_values = PartialValueMatrix(
            [[["*", "Good", 5000]]], criteria=self.criteria, scales=self.scales
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
        self.out_table = PerformanceTable(
            [
                ["Bad", "Good", "Perfect"],
                ["Perfect", "Bad", "Perfect"],
                ["Good", "Perfect", "Perfect"],
                ["Perfect", "Good", "Good"],
            ],
            scales=self.out_scales,
            alternatives=self.alternatives,
            criteria=self.criteria,
        )
        self.out_partial_values = PartialValueMatrix(
            [[["Bad", "Good", "Perfect"]]],
            criteria=self.criteria,
            scales=self.out_scales,
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
        self.normal_partial_values = PartialValueMatrix(
            [[[0, 0.5, 1 - 5000 / 25000]]],
            criteria=self.criteria,
            scales=QuantitativeScale.normal(),
        )
        self.klass = ClosestTransformer
