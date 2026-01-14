import unittest
from math import exp

import pytest
from pandas import Series
from pandas.testing import assert_frame_equal, assert_series_equal

from mcda.functions import (
    AdditiveValueFunctions,
    AffineFunction,
    CriteriaFunctions,
    CriterionFunction,
    DiscreteFunction,
    FuzzyNumber,
    GaussianFunction,
    Interval,
    LevelFunction,
    PieceWiseFunction,
    UShapeFunction,
    VShapeFunction,
)
from mcda.matrices import (
    AdditivePerformanceTable,
    AdjacencyValueMatrix,
    PartialValueMatrix,
    PerformanceTable,
)
from mcda.scales import QualitativeScale, QuantitativeScale
from mcda.types import Scale
from mcda.values import CommensurableValues, Values


def test_intervals():
    # Test constructor
    i = Interval(0, 1)
    assert i.dmin == 0 and i.dmax == 1
    assert i.min_in and i.max_in
    with pytest.raises(Exception) as e:
        Interval(2, 1)
    assert e.type == ValueError

    # Check is empty
    assert Interval(0, 0, False).is_empty
    assert not Interval(0, 0).is_empty

    # Check inside
    assert 0 in i and 1 in i and 1.1 not in i
    i = Interval(0, 1, False, False)
    assert 0 not in i and 1 not in i
    assert 0 not in Interval(0, 0, False)

    # Check normalize
    i = Interval(1, 2)
    assert i.normalize(1) == 0 and i.normalize(2) == 1

    # Check denormalize
    assert i.denormalize(0) == 1 and i.denormalize(1) == 2

    # Check intersection
    i = Interval(-10, 10)
    res = i.intersect(Interval(-5, 15))
    assert res.dmin == -5 and res.dmax == 10 and res.min_in and res.max_in
    res = i.intersect(Interval(-20, 20))
    assert res.dmin == -10 and res.dmax == 10 and res.min_in and res.max_in
    res = i.intersect(Interval(-5, 5, False))
    assert res.dmin == -5 and res.dmax == 5 and not res.min_in and res.max_in
    assert i.intersect(Interval(-50, -20, False, False)).is_empty
    assert i.intersect(Interval(-50, -10, False, False)).is_empty

    # Check join
    i = Interval(-10, 10, False)
    res = i.join(Interval(-5, 15))
    assert res.dmin == -10 and res.dmax == 15 and not res.min_in and res.max_in
    res = i.join(Interval(-20, 20))
    assert res.dmin == -20 and res.dmax == 20 and res.min_in and res.max_in
    res = i.join(Interval(-5, 5, False))
    assert res.dmin == -10 and res.dmax == 10 and not res.min_in and res.max_in

    # Check union
    i = Interval(-10, 10, True, False)
    res = i.union(Interval(-20, -10))
    assert res.dmin == -20 and res.dmax == 10 and res.min_in and not res.max_in
    res = i.union(Interval(-5, 15))
    assert res.dmin == -10 and res.dmax == 15 and res.min_in and res.max_in
    res = i.union(Interval(-20, 20))
    assert res.dmin == -20 and res.dmax == 20 and res.min_in and res.max_in
    res = i.union(Interval(-5, 5, False))
    assert res.dmin == -10 and res.dmax == 10 and res.min_in and not res.max_in
    assert i.union(Interval(20, 30)).is_empty
    assert i.union(Interval(10, 30)).is_empty
    i = Interval(-10, 10)
    res = i.join(Interval(10, 20))
    assert res.dmin == -10 and res.dmax == 20

    # Check continuous
    i = Interval(-10, 10, True, False)
    assert i.continuous(Interval(10, 20, True))
    assert not i.continuous(Interval(10, 20, False))
    assert not i.continuous(Interval(15, 20, True))
    assert not i.continuous(Interval(-20, -10, False))

    # Check relation operators
    i = Interval(-10, 10, False, False)
    assert i == Interval(-10, 10, False, False)
    assert i != Interval(-10, 10, True)

    # Test str conversion
    assert str(Interval(0, 1)) == "[0, 1]"
    assert str(Interval(0, 1, False, False)) == "]0, 1["


def test_affine_function_from_segments():
    # Test valid affine function creation
    f = AffineFunction(1, 0.5)
    assert f(0) == 0.5 and f(1) == 1.5

    segment = [[0, 0], [1, 2]]
    f = AffineFunction(segment=segment)
    assert f(0) == 0 and f(1) == 2

    # Test error cases
    with pytest.raises(Exception) as ex:
        AffineFunction(segment=[[0, 0]])
    assert ex.type == ValueError
    with pytest.raises(Exception) as ex:
        AffineFunction(segment=[[0, 0], []])
    assert ex.type == ValueError
    with pytest.raises(Exception) as ex:
        AffineFunction(segment=[[], [0, 0]])
    assert ex.type == ValueError
    with pytest.raises(Exception) as ex:
        AffineFunction(segment=[[0, 1], [0, 0]])
    assert ex.type == ValueError


def test_discrete_functions():
    # Test constructor
    values = {"a": 1, "b": 2, "c": 3}
    f = DiscreteFunction(values)
    assert len(f.values) == 3
    assert f("a") == 1 and f("b") == 2 and f("c") == 3

    with pytest.raises(Exception) as ex:
        f("d")
    assert ex.type == IndexError


def test_piecewise_functions():
    # Test constructor
    intervals = [Interval(0, 2.5, max_in=False), Interval(2.5, 5)]
    functions = {
        intervals[0]: lambda x: x,
        intervals[1]: lambda x: -0.5 * x + 2.0,
    }
    f = PieceWiseFunction(functions)
    assert f(0) == 0 and f(2.5) == 0.75
    f = PieceWiseFunction(
        segments=[[[0, 0], [2.5, 1, False]], [[2.5, 2], [5, 1.5]]]
    )
    assert len(f.functions) == 2
    assert f.intervals == intervals

    # Test apply
    assert f(2.5) == 2 and f(5) == 1.5 and f(0) == 0 and f(1.25) == 0.5
    with pytest.raises(Exception) as ex:
        f(-500)
    assert ex.type == ValueError

    # Test continuity
    assert not f.continuous
    f = PieceWiseFunction(
        {
            Interval(0, 2.5, max_in=False): lambda x: 5,
            Interval(2.5, 5): lambda x: 2 * x,
        }
    )
    assert f.continuous
    f.intervals[1].min_in = False
    assert not f.continuous
    f = PieceWiseFunction({Interval(0, 1): lambda x: 2 * x + 3.5})
    f(0.5)
    assert f.continuous

    # Test string conversion
    assert str(f) == str({"[0, 1]": str(list(f.functions.values())[0])})


def test_fuzzy_numbers():
    # Test constructor
    f = FuzzyNumber([0, 2.5, 2.5, 5])
    assert f.average == 2.5
    f2 = FuzzyNumber([1, 1, 1, 1])
    assert len(f2.intervals) == 1
    assert f2.intervals[0].dmin == f2.intervals[0].dmax
    assert f2(1) == 1
    assert f2(150) == 0
    with pytest.raises(Exception) as ex:
        FuzzyNumber([])
    assert ex.type == ValueError
    with pytest.raises(Exception) as ex:
        FuzzyNumber([0, 1, 2, 1.5])
    assert ex.type == ValueError
    assert f.continuous
    assert f.average == 2.5
    assert f.centre_of_gravity == 2.5
    assert f2.centre_of_gravity == 1
    assert f.centre_of_maximum == 2.5
    assert f.area == 2.5
    assert f != f.centre_of_gravity
    assert f != f2
    assert f == FuzzyNumber(f.abscissa.copy())


class TestCriterionFunction(unittest.TestCase):
    def setUp(self):
        self.function = CriterionFunction(
            lambda x: 2 * x,
            QuantitativeScale(Interval(-1, 1)),
            QuantitativeScale(Interval(-2, 2)),
            QuantitativeScale,
            QuantitativeScale,
        )
        self.data = CommensurableValues(Series([0, 0.5, 1, -0.6]))

    def test_constructor(self):
        CriterionFunction(self.function.function)
        CriterionFunction(
            self.function.function,
            self.function.in_scale,
            self.function.out_scale,
        )
        CriterionFunction(
            self.function.function,
            self.function.in_scale,
            self.function.out_scale,
            Scale,
            Scale,
        )
        CriterionFunction(
            self.function.function,
            in_stype=QuantitativeScale,
            out_stype=QuantitativeScale,
        )
        with self.assertRaises(TypeError):
            CriterionFunction(
                self.function.function,
                self.function.in_scale,
                self.function.out_scale,
                QualitativeScale,
                QuantitativeScale,
            )
        with self.assertRaises(TypeError):
            CriterionFunction(
                self.function.function,
                self.function.in_scale,
                self.function.out_scale,
                QuantitativeScale,
                QualitativeScale,
            )

    def test_within_in_scale(self):
        self.assertTrue(self.function.within_in_scale(self.data))
        self.assertTrue(self.function.within_in_scale(self.data.data))
        self.assertTrue(self.function.within_in_scale(0.5))
        self.assertFalse(self.function.within_in_scale("aa"))
        self.assertTrue(
            CriterionFunction(self.function.function).within_in_scale("aa")
        )

    def test_call(self):
        expected = CommensurableValues(
            Series([0, 1, 2, -1.2]),
            scale=self.function.out_scale,
        )
        self.assertEqual(self.function(self.data), expected)
        assert_series_equal(self.function(self.data.data), expected.data)
        self.assertEqual(self.function(1), 2)


class TestCriteriaFunctions(unittest.TestCase):
    def setUp(self):
        self.functions = {0: lambda x: x * 2, 1: lambda x: -2 * x + 50}
        self.scales = {
            0: QuantitativeScale(Interval(-1, 1)),
            1: QuantitativeScale(Interval(0, 100)),
        }
        self.partial_values = PartialValueMatrix([[[1, 10]]])
        self.table = PerformanceTable([[1, 10], [-1, 0]], scales=self.scales)
        self.function = CriteriaFunctions(
            {
                c: CriterionFunction(
                    self.functions[c], self.scales[c], self.scales[c]
                )
                for c in self.functions
            }
        )
        self.function2 = CriteriaFunctions(
            {c: CriterionFunction(f) for c, f in self.functions.items()}
        )

    def test_constructor(self):  # pragma: nocover
        # Coverage is weird on that test
        # It shows CriteriaFunctions calls as not jumping to exit???
        CriteriaFunctions(
            {
                0: CriterionFunction(lambda x: 2 * x),
                1: CriterionFunction(
                    lambda x: 2 * x,
                    in_scale=QuantitativeScale(),
                    out_scale=QuantitativeScale(),
                ),
                2: lambda x: 2 * x,
                3: lambda x: 2 * x,
            },
            {
                2: QuantitativeScale(),
            },
            {3: QuantitativeScale()},
        )
        CriteriaFunctions(
            {0: lambda x: 2 * x}, QuantitativeScale(), QuantitativeScale()
        )
        with self.assertRaises(TypeError):
            CriteriaFunctions(
                {
                    0: CriterionFunction(
                        lambda x: 2 * x, in_stype=QuantitativeScale
                    )
                },
                in_stype=QualitativeScale,
            )
        with self.assertRaises(TypeError):
            CriteriaFunctions(
                {
                    0: CriterionFunction(
                        lambda x: 2 * x, out_stype=QuantitativeScale
                    )
                },
                out_stype=QualitativeScale,
            )
        with self.assertRaises(TypeError):
            CriteriaFunctions(
                {
                    0: CriterionFunction(
                        lambda x: 2 * x, in_scale=QuantitativeScale()
                    )
                },
                in_stype=QualitativeScale,
            )
        with self.assertRaises(TypeError):
            CriteriaFunctions(
                {
                    0: CriterionFunction(
                        lambda x: 2 * x, out_scale=QuantitativeScale()
                    )
                },
                out_stype=QualitativeScale,
            )
        with self.assertRaises(TypeError):
            CriteriaFunctions(
                {0: lambda x: 2 * x},
                QuantitativeScale(),
                in_stype=QualitativeScale,
            )
        with self.assertRaises(TypeError):
            CriteriaFunctions(
                {0: lambda x: 2 * x},
                out_scales=QuantitativeScale(),
                out_stype=QualitativeScale,
            )

    def test_within_in_scale(self):
        self.assertTrue(self.function.within_in_scales(self.table))
        self.assertTrue(self.function.within_in_scales(self.table.data))
        self.assertTrue(
            self.function.within_in_scales(self.table.alternatives_values[0])
        )
        self.assertTrue(
            self.function.within_in_scales(
                self.table.alternatives_values[0].data
            )
        )
        self.assertTrue(self.function.within_in_scales(self.partial_values))
        data = Series([0, "aa"])
        self.assertFalse(self.function.within_in_scales(data))
        self.assertTrue(self.function2.within_in_scales(data))

    def test_call(self):
        res_table = PerformanceTable([[2, 30], [-2, 50]], scales=self.scales)
        self.assertEqual(self.function(self.table), res_table)
        self.assertEqual(
            self.function(self.table.alternatives_values[0]),
            res_table.alternatives_values[0],
        )
        assert_frame_equal(self.function(self.table.data), res_table.data)
        assert_series_equal(self.function(Series([0, 0])), Series([0, 50]))
        res_partial_values = PartialValueMatrix(
            [[[2, 30]]], scales=self.scales
        )
        self.assertEqual(
            self.function(self.partial_values), res_partial_values
        )


class TestAdditiveValueFunctions(unittest.TestCase):
    def setUp(self):
        self.functions = {0: lambda x: x * 2, 1: lambda x: -2 * x + 50}
        self.scales = {
            0: QuantitativeScale(Interval(-1, 1)),
            1: QuantitativeScale(Interval(0, 100)),
        }
        self.criterion_functions = {
            c: CriterionFunction(self.functions[c], self.scales[c])
            for c in self.scales
        }
        self.additive_value_functions = AdditiveValueFunctions(
            self.criterion_functions, aggregator_scale=QuantitativeScale()
        )
        self.table = PerformanceTable([[1, 10], [-1, 0]], scales=self.scales)
        self.values = Values(
            Series([1, 0]),
            scales=self.scales,
        )
        self.partial_values = PartialValueMatrix([[self.values.data]])
        self.applied_table = AdditivePerformanceTable(
            [[2, 30], [-2, 50]], aggregated_scale=QuantitativeScale()
        )
        self.applied_values = Values([2, 50])
        self.applied_partial_values = PartialValueMatrix(
            [[self.applied_values.data]]
        )
        self.aggregated_table = CommensurableValues(
            [32, 48], scale=QuantitativeScale()
        )
        self.aggregated_values = 52
        self.aggregated_partial_values = AdjacencyValueMatrix(
            [[self.aggregated_values]], scale=QuantitativeScale()
        )

    def test_within_in_scales(self):
        self.assertTrue(
            self.additive_value_functions.within_in_scales(self.values.data)
        )
        self.assertTrue(
            self.additive_value_functions.within_in_scales(self.values)
        )
        self.assertTrue(
            self.additive_value_functions.within_in_scales(self.table.data)
        )
        self.assertTrue(
            self.additive_value_functions.within_in_scales(self.table)
        )
        self.assertTrue(
            self.additive_value_functions.within_in_scales(self.partial_values)
        )

    def test_apply_series(self):
        assert_series_equal(
            self.additive_value_functions(self.values.data),
            self.applied_values.data,
        )

    def test_apply_values(self):
        self.assertEqual(
            self.additive_value_functions(self.values),
            self.applied_values,
        )

    def test_apply_dataframe(self):
        assert_frame_equal(
            self.additive_value_functions(self.table.data),
            self.applied_table.data,
        )

    def test_apply_table(self):
        res = self.additive_value_functions(self.table)
        self.assertEqual(
            res,
            self.applied_table,
        )
        self.assertEqual(
            res.aggregated_scale, self.applied_table.aggregated_scale
        )

    def test_apply_partial_values(self):
        self.assertEqual(
            self.additive_value_functions(self.partial_values),
            self.applied_partial_values,
        )

    def test_aggregate_series(self):
        self.assertEqual(
            self.additive_value_functions.aggregate(
                self.additive_value_functions(self.values.data)
            ),
            self.aggregated_values,
        )

    def test_aggregate_values(self):
        self.assertEqual(
            self.additive_value_functions.aggregate(
                self.additive_value_functions(self.values)
            ),
            self.aggregated_values,
        )

    def test_aggregate_dataframe(self):
        assert_series_equal(
            self.additive_value_functions.aggregate(
                self.additive_value_functions(self.table.data)
            ),
            self.aggregated_table.data,
        )

    def test_aggregate_value_matrix(self):
        self.assertEqual(
            self.additive_value_functions.aggregate(
                self.additive_value_functions(self.table)
            ),
            self.aggregated_table,
        )

    def test_aggregate_partial_value_matrix(self):
        self.assertEqual(
            self.additive_value_functions.aggregate(
                self.additive_value_functions(self.partial_values)
            ),
            self.aggregated_partial_values,
        )


class TestUShapeFunction(unittest.TestCase):
    def setUp(self):
        self.p = 1
        self.function = UShapeFunction(self.p)

    def test(self):
        self.assertEqual(self.function.p, self.p)
        self.assertEqual(self.function(-1), 0)
        self.assertEqual(self.function(1.5), 1)


class TestVShapeFunction(unittest.TestCase):
    def setUp(self):
        self.p = 1
        self.function = VShapeFunction(self.p)

    def test_constructor(self):
        with self.assertRaises(ValueError):
            VShapeFunction(1, 2)

    def test(self):
        self.assertEqual(self.function.p, self.p)
        self.assertEqual(self.function(-1), 0)
        self.assertEqual(self.function(1.5), 1)
        self.assertEqual(self.function(0.5), 0.5)


class TestLevelFunction(unittest.TestCase):
    def setUp(self):
        self.p = 2
        self.q = 1
        self.function = LevelFunction(self.p, self.q)

    def test(self):
        self.assertRaises(ValueError, LevelFunction, 1, 2)
        self.assertEqual(self.function.q, self.q)
        self.assertEqual(self.function.p, self.p)
        self.assertEqual(self.function(0.5), 0)
        self.assertEqual(self.function(1.5), 0.5)
        self.assertEqual(self.function(2.5), 1)


class TestLinearFunction(unittest.TestCase):
    def setUp(self):
        self.p = 2
        self.q = 1
        self.function = VShapeFunction(self.p, self.q)

    def test(self):
        self.assertEqual(self.function.q, self.q)
        self.assertEqual(self.function.p, self.p)
        self.assertEqual(self.function(0.5), 0)
        self.assertEqual(self.function(1.5), 0.5)
        self.assertEqual(self.function(2.5), 1)


class TestGaussianFunction(unittest.TestCase):
    def setUp(self):
        self.s = 1
        self.function = GaussianFunction(self.s)

    def test(self):
        self.assertEqual(self.function.s, self.s)
        self.assertEqual(self.function(-1), 0)
        self.assertEqual(self.function(1), 1 - exp(-1 / 2))
