import unittest

from pandas import Series
from pandas.testing import assert_series_equal

from mcda.scales import (
    DiscreteQuantitativeScale,
    PreferenceDirection,
    QualitativeScale,
    QuantitativeScale,
)
from mcda.values import CommensurableValues, Value, Values, series_equals


def test_series_equals():
    s1 = Series([0, 1, 2, 3])
    s2 = Series([3, 2, 1, 0], index=[3, 2, 1, 0])
    assert series_equals(s1, s2)
    assert not series_equals(s1, Series({"0": 0, 1: 1, 2: 2, 3: 3}))
    assert not series_equals(s1, Series([1, 1, 2, 3]))


class TestValue(unittest.TestCase):
    def setUp(self):
        self.value1 = Value(10, QuantitativeScale(0, 100))
        self.value2 = Value(15, QuantitativeScale(0, 100))
        self.value3 = Value(1, QuantitativeScale(0, 1))
        self.value4 = Value(10, QuantitativeScale(0, 100))

    def test_constructor(self):
        self.assertEqual(self.value1.value, 10)
        self.assertEqual(self.value1.scale, QuantitativeScale(0, 100))

    def test_comparisons(self):
        self.assertGreater(self.value2, self.value1)
        self.assertGreaterEqual(self.value2, self.value1)
        self.assertGreaterEqual(self.value4, self.value1)
        self.assertNotEqual(self.value1, self.value2)
        self.assertLess(self.value1, self.value2)
        self.assertLessEqual(self.value1, self.value2)
        self.assertLessEqual(self.value1, self.value4)
        self.assertEqual(self.value1, self.value4)
        with self.assertRaises(TypeError):
            self.value1 == self.value1.value
        with self.assertRaises(TypeError):
            self.value1 != self.value1.value
        with self.assertRaises(TypeError):
            self.value1 >= self.value1.value
        with self.assertRaises(TypeError):
            self.value1 > self.value1.value
        with self.assertRaises(TypeError):
            self.value1 <= self.value1.value
        with self.assertRaises(TypeError):
            self.value1 < self.value1.value
        with self.assertRaises(ValueError):
            self.value1 == self.value3
        with self.assertRaises(ValueError):
            self.value1 != self.value3
        with self.assertRaises(ValueError):
            self.value1 >= self.value3
        with self.assertRaises(ValueError):
            self.value1 > self.value3
        with self.assertRaises(ValueError):
            self.value1 <= self.value3
        with self.assertRaises(ValueError):
            self.value1 < self.value3


class TestValues(unittest.TestCase):
    def setUp(self):
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
        self.name = "a00"
        self.labels = ["c01", "c02", "c03"]
        self.data = Series(
            ["**", "Perfect", 12000], index=self.labels, name=self.name
        )
        self.values = Values(self.data, self.scales)
        self.numeric_values = Values(
            Series([2, 1, 12000], index=self.labels, name=self.name),
            scales={c: s.numeric for c, s in self.scales.items()},
        )

    def test_constructor(self):
        assert_series_equal(self.data, self.values.data)
        self.assertEqual(self.values.scales, self.scales)
        v1 = Values(Series([0, 1, 2]))
        self.assertEqual(
            v1.scales,
            {k: QuantitativeScale(0, 2) for k in range(3)},
        )
        v2 = Values(Series([0, -10, 5, 12]), QuantitativeScale(-20, 20))
        self.assertEqual(
            v2.scales,
            {k: QuantitativeScale(-20, 20) for k in range(4)},
        )
        with self.assertRaises(KeyError):
            Values(Series([0, 1, 2], index=["a", "b", "a"]))
        with self.assertRaises(TypeError):
            Values(self.data, scales=self.scales, stype=QuantitativeScale)
        with self.assertRaises(TypeError):
            Values(
                self.data, scales=QuantitativeScale(), stype=QualitativeScale
            )
        for a, b in zip(self.values.data, self.data):
            self.assertEqual(a, b)

    def test_name(self):
        self.assertEqual(self.values.name, self.name)
        self.assertEqual(self.numeric_values.name, self.name)

    def test_labels(self):
        self.assertEqual(self.values.labels, self.labels)
        self.assertEqual(self.numeric_values.labels, self.labels)

    def test_equal(self):
        self.assertNotEqual(self.values, self.data)
        self.assertNotEqual(
            self.values,
            Values(Series([0, 1, 2], index=["c01", "c02", "c03"], name="a00")),
        )
        self.assertEqual(
            Values(self.data, self.scales),
            self.values,
        )
        self.assertNotEqual(self.values, 12)

    def test_bounds(self):
        v1 = Values(Series([0, 1, 2]))
        self.assertEqual(v1.bounds, QuantitativeScale(0, 2))

    def test_within_scales(self):
        self.assertTrue(self.values.within_scales.all(axis=None))

    def test_is_within_criteria_scales(self):
        self.assertTrue(self.values.is_within_scales)

    def test_is_numeric(self):
        self.assertFalse(self.values.is_numeric)
        self.assertTrue(self.numeric_values.is_numeric)

    def test_is_ordinal(self):
        self.assertTrue(self.values.is_ordinal)
        self.assertFalse(Values(self.data).is_ordinal)

    def test_to_numeric(self):
        self.assertEqual(self.values.to_numeric, self.numeric_values)
        self.assertEqual(self.numeric_values.to_numeric, self.numeric_values)
        with self.assertRaises(TypeError):
            Values(self.data).to_numeric

    def test_sum(self):
        self.assertRaises(TypeError, self.values.sum)
        self.assertEqual(self.values.to_numeric.sum(), 12003)

    def test_dominate(self):
        a1 = Values(
            Series(
                ["**", "Bad", 10000],
                index=["c01", "c02", "c03"],
                name="a00",
            ),
            self.scales,
        )
        a2 = Values(
            Series(
                ["**", "Good", 12000],
                index=["c01", "c02", "c03"],
                name="a00",
            ),
            self.scales,
        )
        a3 = Values(
            Series(
                ["***", "Perfect", 12000],
                index=["c01", "c02", "c03"],
                name="a00",
            ),
            self.scales,
        )
        self.assertFalse(self.values.dominate(a1))
        self.assertTrue(self.values.dominate(a2))
        self.assertFalse(self.values.dominate(a3))
        self.assertFalse(self.values.dominate(self.values.copy()))
        with self.assertRaises(TypeError):
            Values(self.data).dominate(self.values)

    def test_dominate_strongly(self):
        a1 = Values(
            Series(
                ["*", "Bad", 25000],
                index=["c01", "c02", "c03"],
                name="a00",
            ),
            self.scales,
        )
        a2 = Values(
            Series(
                ["**", "Good", 12000],
                index=["c01", "c02", "c03"],
                name="a00",
            ),
            self.scales,
        )
        a3 = Values(
            Series(
                ["***", "Perfect", 12000],
                index=["c01", "c02", "c03"],
                name="a00",
            ),
            self.scales,
        )
        self.assertTrue(self.values.dominate_strongly(a1))
        self.assertFalse(self.values.dominate_strongly(a2))
        self.assertFalse(self.values.dominate_strongly(a3))
        self.assertFalse(self.values.dominate_strongly(self.values.copy()))
        with self.assertRaises(TypeError):
            Values(self.data).dominate_strongly(self.values)

    def test_sort(self):
        expected = Values(
            Series(
                ["Perfect", 12000, "**"],
                index=["c02", "c03", "c01"],
                name="a00",
            ),
            self.scales,
        )
        self.assertEqual(self.values.sort(), expected)
        with self.assertRaises(TypeError):
            Values(self.data).sort()

    def test_copy(self):
        copy = self.values.copy()
        assert_series_equal(copy.data, self.values.data)
        self.assertEqual(copy.scales, self.values.scales)

    def test_items(self):
        values = Values(self.data, self.scales)
        values.data["c01"] = "*"
        self.assertEqual(values["c01"], Value("*", self.scales["c01"]))

    def test_multiply(self):
        v = Values(
            Series([10, 30, 2], index=["c01", "c02", "c03"], name="a00"),
        )
        self.assertEqual(
            self.numeric_values * v,
            Values(
                Series(
                    [20, 30, 24000], index=["c01", "c02", "c03"], name="a00"
                )
            ),
        )
        self.assertEqual(
            self.numeric_values * 10,
            Values(
                Series(
                    [20, 10, 120000], index=["c01", "c02", "c03"], name="a00"
                )
            ),
        )

    def test_addition(self):
        v = Values(
            Series([10, 30, 5000], index=["c01", "c02", "c03"], name="a00"),
        )
        self.assertEqual(
            self.numeric_values + v,
            Values(
                Series(
                    [12, 31, 17000], index=["c01", "c02", "c03"], name="a00"
                )
            ),
        )
        self.assertEqual(
            self.numeric_values + 10,
            Values(
                Series(
                    [12, 11, 12010], index=["c01", "c02", "c03"], name="a00"
                )
            ),
        )

    def test_subtract(self):
        v = Values(
            Series([10, 30, 5000], index=["c01", "c02", "c03"], name="a00"),
        )
        self.assertEqual(
            self.numeric_values - v,
            Values(
                Series(
                    [-8, -29, 7000], index=["c01", "c02", "c03"], name="a00"
                )
            ),
        )
        self.assertEqual(
            self.numeric_values - 10,
            Values(
                Series(
                    [-8, -9, 11990], index=["c01", "c02", "c03"], name="a00"
                )
            ),
        )


class TestCommensurableValues(unittest.TestCase):
    def setUp(self):
        self.scale = QuantitativeScale(0, 2)
        self.data = Series([2, 0.5, 1, 1, 2])
        self.values = CommensurableValues(self.data, scale=self.scale)

    def test_constructor(self):
        assert_series_equal(self.data, self.values.data)
        self.assertEqual(self.values.scale, self.scale)
        with self.assertRaises(KeyError):
            CommensurableValues(Series([0, 1, 2], index=["a", "b", "a"]))
        with self.assertRaises(TypeError):
            CommensurableValues(
                self.data, scale=self.scale, stype=QualitativeScale
            )
        for a, b in zip(self.values.data, self.data):
            self.assertEqual(a, b)

    def test_name(self):
        self.assertIsNone(self.values.name)

    def test_labels(self):
        self.assertEqual(self.values.labels, list(range(len(self.data))))

    def test_bounds(self):
        self.assertEqual(self.values.bounds, QuantitativeScale(0.5, 2))

    def test_within_scales(self):
        self.assertTrue(self.values.within_scales.all(axis=None))

    def test_is_within_criteria_scales(self):
        self.assertTrue(self.values.is_within_scales)

    def test_is_numeric(self):
        self.assertTrue(self.values.is_numeric)

    def test_is_ordinal(self):
        self.assertTrue(self.values.is_ordinal)

    def test_sum(self):
        self.assertEqual(self.values.to_numeric.sum(), 6.5)

    def test_dominate(self):
        a1 = CommensurableValues(
            Series(
                [1, 0, 2, 1, 2],
            ),
            self.scale,
        )
        a2 = CommensurableValues(
            Series(
                [2, 0, 1, 0, 2],
            ),
            self.scale,
        )
        a3 = CommensurableValues(
            Series(
                [2, 1, 1, 1, 2],
            ),
            self.scale,
        )
        self.assertFalse(self.values.dominate(a1))
        self.assertTrue(self.values.dominate(a2))
        self.assertFalse(self.values.dominate(a3))
        self.assertFalse(self.values.dominate(self.values.copy()))

    def test_dominate_strongly(self):
        a1 = CommensurableValues(
            Series([1, 0, 0, 0, 1]),
            self.scale,
        )
        a2 = CommensurableValues(
            Series([2, 1, 2, 2, 2]),
            self.scale,
        )
        a3 = Values(
            Series([2, 0, 1, 1, 2]),
            self.scale,
        )
        self.assertTrue(self.values.dominate_strongly(a1))
        self.assertFalse(self.values.dominate_strongly(a2))
        self.assertFalse(self.values.dominate_strongly(a3))
        self.assertFalse(self.values.dominate_strongly(self.values.copy()))

    def test_copy(self):
        copy = self.values.copy()
        assert_series_equal(copy.data, self.values.data)
        self.assertEqual(copy.scale, self.values.scale)

    def test_items(self):
        values = Values(self.data, self.scale)
        values.data[0] = 0
        self.assertEqual(values[0], Value(0, self.scale))

    def test_multiply(self):
        Series([2, 0.5, 1, 1, 2])
        v = Values(
            Series([10, 30, 2, 0, 0]),
        )
        self.assertEqual(
            self.values * v,
            CommensurableValues(Series([20, 15, 2, 0, 0])),
        )
        self.assertEqual(
            self.values * 10,
            CommensurableValues(Series([20, 5, 10, 10, 20])),
        )

    def test_addition(self):
        v = Values(
            Series([10, 30, 5000, 0, 0]),
        )
        self.assertEqual(
            self.values + v,
            CommensurableValues(Series([12, 30.5, 5001, 1, 2])),
        )
        self.assertEqual(
            self.values + 10,
            CommensurableValues(Series([12, 10.5, 11, 11, 12])),
        )

    def test_subtract(self):
        v = Values(
            Series([10, 30, 5000, 0, 0]),
        )
        self.assertEqual(
            self.values - v,
            CommensurableValues(Series([-8, -29.5, -4999, 1, 2])),
        )
        self.assertEqual(
            self.values - 10,
            CommensurableValues(Series([-8, -9.5, -9, -9, -8])),
        )

    def test_equal(self):
        self.assertNotEqual(self.values, Values(self.data))
        self.assertNotEqual(
            self.values,
            CommensurableValues(self.data, stype=DiscreteQuantitativeScale),
        )
        self.assertEqual(
            self.values, CommensurableValues(self.data, self.scale)
        )

    def test_to_numeric(self):
        self.assertEqual(self.values.to_numeric, self.values)
        scale = QualitativeScale(Series({"a": 0, "b": 1, "c": 2}))
        r = CommensurableValues(Series(["c", "a", "b", "b", "c"]), scale=scale)
        self.assertEqual(
            r.to_numeric,
            CommensurableValues(
                Series([2, 0, 1, 1, 2]),
                scale=DiscreteQuantitativeScale([0, 1, 2]),
            ),
        )
        with self.assertRaises(TypeError):
            CommensurableValues(Series(["c", "a", "b", "b", "c"])).to_numeric

    def test_sort(self):
        expected = CommensurableValues(
            Series({0: 2, 4: 2, 2: 1, 3: 1, 1: 0.5}), scale=self.scale
        )
        self.assertEqual(self.values.sort(), expected)
        with self.assertRaises(TypeError):
            CommensurableValues(Series(["c", "a", "b", "b", "c"])).sort()
