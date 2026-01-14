from unittest import TestCase

import numpy as np
from pandas import Series

from mcda.functions import FuzzyNumber, Interval
from mcda.scales import (
    MAX,
    MIN,
    DiscreteQuantitativeScale,
    FuzzyScale,
    NominalScale,
    PreferenceDirection,
    QualitativeScale,
    QuantitativeScale,
    common_scale_type,
)
from mcda.types import BinaryScale, NormalScale, OrdinalScale, Scale


def test_preference_direction():
    assert PreferenceDirection.has_value(PreferenceDirection.MIN)
    assert PreferenceDirection.has_value(PreferenceDirection.MAX)
    assert MIN == PreferenceDirection.MIN
    assert MAX == PreferenceDirection.MAX


class NominalScaleTest(TestCase):
    def setUp(self):
        self.scale = NominalScale(["red", "green", "blue"])

    def test_equal(self):
        self.assertEqual(self.scale, NominalScale(self.scale.labels.copy()))
        self.assertNotEqual(self.scale, QuantitativeScale(0, 10))
        self.assertNotEqual(self.scale, NominalScale(["red", "GREEN", "blue"]))

    def test_contains(self):
        for label in self.scale.labels.copy():
            self.assertIn(label, self.scale)
        self.assertNotIn("GREEN", self.scale)

    def test_range(self):
        res = self.scale.labels.copy()
        self.assertEqual(res, self.scale.range())
        self.assertEqual(res, self.scale.range(nb=10))

    def test_is_better(self):
        with self.assertRaises(TypeError):
            self.scale.is_better("green", "red")

    def test_is_better_or_equal(self):
        with self.assertRaises(TypeError):
            self.scale.is_better_or_equal("green", "red")
        self.scale.is_better_or_equal("green", "green")
        with self.assertRaises(TypeError):
            self.scale.is_better_or_equal("AAAA", "AAAA")

    def test_fit(self):
        self.assertEqual(
            NominalScale.fit(Series([0, 10, "a"])), NominalScale([0, 10, "a"])
        )


class QuantitativeScaleTest(TestCase):
    def setUp(self):
        self.scale = QuantitativeScale(0, 10)
        self.min_scale = QuantitativeScale(
            0, 10, preference_direction=PreferenceDirection.MIN
        )

    def test_interval(self):
        self.assertEqual(self.scale.interval, Interval(0, 10))

    def test_numeric(self):
        self.assertEqual(self.scale.numeric, self.scale)

    def test_normal(self):
        self.assertEqual(QuantitativeScale.normal(), QuantitativeScale(0, 1))

    def test_equal(self):
        self.assertNotEqual(self.scale, NominalScale(["a"]))
        self.assertNotEqual(self.scale, self.min_scale)
        self.assertNotEqual(
            self.scale,
            QuantitativeScale(
                0, 10, preference_direction=PreferenceDirection.MAX
            ),
        )
        self.assertNotEqual(self.scale, QuantitativeScale(0, 10, min_in=False))
        self.assertEqual(self.scale, QuantitativeScale(self.scale.interval))

    def test_range(self):
        self.assertEqual(self.scale.range(), [0, 10])
        self.assertEqual(self.scale.range(nb=5), [0, 2.5, 5, 7.5, 10])

    def test_contains(self):
        self.assertIn(0, self.scale)
        self.assertIn(10, self.scale)
        self.assertIn(1, self.scale)
        self.assertNotIn(11, self.scale)

    def test_value(self):
        self.assertEqual(self.scale.value(5), 5)
        with self.assertRaises(ValueError):
            self.scale.value(11)

    def test_label(self):
        self.assertEqual(self.scale.label(5), 5)
        with self.assertRaises(ValueError):
            self.scale.label(11)

    def test_is_better(self):
        self.assertTrue(self.scale.is_better(5, 2))
        self.assertFalse(self.scale.is_better(1, 2))
        with self.assertRaises(ValueError):
            self.scale.is_better(11, 10)
        self.assertTrue(self.min_scale.is_better(0, 10))

    def test_is_better_or_equal(self):
        self.assertTrue(self.scale.is_better_or_equal(5, 2))
        self.assertFalse(self.scale.is_better_or_equal(1, 2))
        self.assertTrue(self.scale.is_better_or_equal(5, 5))
        with self.assertRaises(ValueError):
            self.scale.is_better_or_equal(11, 10)
        with self.assertRaises(ValueError):
            self.scale.is_better_or_equal(11, 11)
        self.assertTrue(self.min_scale.is_better_or_equal(0, 10))

    def test_fit(self):
        with self.assertRaises(TypeError):
            QuantitativeScale.fit(Series(["a", 0, 10]))
        self.assertEqual(
            QuantitativeScale.fit(Series([10, 2, 5, 0, 8])),
            QuantitativeScale(0, 10),
        )
        self.assertEqual(
            QuantitativeScale.fit(
                Series([10, 2, 5, 0, 8]),
                preference_direction=PreferenceDirection.MIN,
            ),
            QuantitativeScale(
                0, 10, preference_direction=PreferenceDirection.MIN
            ),
        )


class DiscreteQuantitativeScaleTest(TestCase):
    def setUp(self):
        self.scale = DiscreteQuantitativeScale([0, 5, 10])
        self.min_scale = DiscreteQuantitativeScale(
            [0, 5, 10], preference_direction=PreferenceDirection.MIN
        )

    def test_interval(self):
        self.assertEqual(self.scale.interval, Interval(0, 10))

    def test_numeric(self):
        self.assertEqual(self.scale.numeric, self.scale)

    def test_binary(self):
        self.assertEqual(
            DiscreteQuantitativeScale.binary(),
            DiscreteQuantitativeScale([0, 1]),
        )

    def test_equal(self):
        self.assertNotEqual(self.scale, QuantitativeScale(0, 10))
        self.assertNotEqual(self.scale, self.min_scale)
        self.assertNotEqual(
            self.scale,
            DiscreteQuantitativeScale(
                [0, 5, 10], preference_direction=PreferenceDirection.MAX
            ),
        )
        self.assertNotEqual(self.scale, DiscreteQuantitativeScale([0, 10]))
        self.assertEqual(self.scale, DiscreteQuantitativeScale([0, 5, 10]))

    def test_range(self):
        self.assertEqual(self.scale.range(), [0, 5, 10])
        self.assertEqual(self.scale.range(nb=5), [0, 5, 10])

    def test_contains(self):
        self.assertIn(0, self.scale)
        self.assertIn(10, self.scale)
        self.assertNotIn(1, self.scale)
        self.assertNotIn(11, self.scale)

    def test_value(self):
        self.assertEqual(self.scale.value(5), 5)
        with self.assertRaises(ValueError):
            self.scale.value(1)

    def test_label(self):
        self.assertEqual(self.scale.label(5), 5)
        with self.assertRaises(ValueError):
            self.scale.label(1)

    def test_is_better(self):
        self.assertTrue(self.scale.is_better(5, 0))
        self.assertFalse(self.scale.is_better(5, 10))
        with self.assertRaises(ValueError):
            self.scale.is_better(10, 1)
        self.assertTrue(self.min_scale.is_better(0, 10))

    def test_is_better_or_equal(self):
        self.assertTrue(self.scale.is_better_or_equal(5, 0))
        self.assertFalse(self.scale.is_better_or_equal(5, 10))
        self.assertTrue(self.scale.is_better_or_equal(5, 5))
        with self.assertRaises(ValueError):
            self.scale.is_better_or_equal(10, 1)
        with self.assertRaises(ValueError):
            self.scale.is_better_or_equal(11, 11)
        self.assertTrue(self.min_scale.is_better_or_equal(0, 10))

    def test_fit(self):
        with self.assertRaises(TypeError):
            DiscreteQuantitativeScale.fit(Series(["a", 0, 10]))
        self.assertEqual(
            DiscreteQuantitativeScale.fit(Series([10, 2, 5, 0, 8])),
            DiscreteQuantitativeScale([10, 2, 5, 0, 8]),
        )
        self.assertEqual(
            DiscreteQuantitativeScale.fit(
                Series([10, 2, 5, 0, 8]),
                preference_direction=PreferenceDirection.MIN,
            ),
            DiscreteQuantitativeScale(
                [10, 2, 5, 0, 8], preference_direction=PreferenceDirection.MIN
            ),
        )


class QualitativeScaleTest(TestCase):
    def setUp(self):
        self.scale = QualitativeScale(
            Series({"red": 3, "green": 2, "blue": 1})
        )
        self.min_scale = QualitativeScale(
            Series({"red": 3, "green": 2, "blue": 1}),
            preference_direction=PreferenceDirection.MIN,
        )

    def test_constructor(self):
        with self.assertRaises(TypeError):
            QualitativeScale(Series({"a": "a", "b": "c"}))

    def test_interval(self):
        self.assertEqual(self.scale.interval, Interval(1, 3))

    def test_numeric(self):
        self.assertEqual(
            self.scale.numeric, DiscreteQuantitativeScale([1, 2, 3])
        )

    def test_equal(self):
        self.assertNotEqual(self.scale, QuantitativeScale(0, 10))
        self.assertNotEqual(self.scale, self.min_scale)
        self.assertNotEqual(
            self.scale,
            QualitativeScale(
                Series({"red": 3, "green": 2, "blue": 1}),
                preference_direction=PreferenceDirection.MAX,
            ),
        )
        self.assertNotEqual(
            self.scale,
            QualitativeScale(Series({"red": 3, "GREEN": 2, "blue": 1})),
        )
        self.assertEqual(
            self.scale,
            QualitativeScale(Series({"red": 3, "green": 2, "blue": 1})),
        )

    def test_range(self):
        self.assertEqual(self.scale.range(), ["red", "green", "blue"])
        self.assertEqual(self.scale.range(nb=5), ["red", "green", "blue"])

    def test_contains(self):
        for label in self.scale.labels.copy():
            self.assertIn(label, self.scale)
        self.assertNotIn("GREEN", self.scale)
        self.assertNotIn(1, self.scale)

    def test_value(self):
        self.assertEqual(self.scale.value("red"), 3)
        with self.assertRaises(ValueError):
            self.scale.value("GREEN")

    def test_label(self):
        self.assertEqual(self.scale.label(2), "green")
        with self.assertRaises(ValueError):
            self.scale.label(0)

    def test_is_better(self):
        self.assertTrue(self.scale.is_better("red", "green"))
        self.assertFalse(self.scale.is_better("blue", "green"))
        with self.assertRaises(ValueError):
            self.scale.is_better("GREEN", "blue")
        self.assertTrue(self.min_scale.is_better("green", "red"))

    def test_is_better_or_equal(self):
        self.assertTrue(self.scale.is_better_or_equal("red", "green"))
        self.assertTrue(self.scale.is_better_or_equal("red", "red"))
        self.assertFalse(self.scale.is_better_or_equal("blue", "green"))
        with self.assertRaises(ValueError):
            self.scale.is_better_or_equal("GREEN", "blue")
        with self.assertRaises(ValueError):
            self.scale.is_better_or_equal("GREEN", "GREEN")
        self.assertTrue(self.min_scale.is_better_or_equal("green", "red"))

    def test_fit(self):
        self.assertEqual(
            QualitativeScale.fit(Series([1, 0, "a"])),
            QualitativeScale(Series({1: 0, 0: 1, "a": 2})),
        )


class FuzzyScaleTest(TestCase):
    def setUp(self):
        self.fuzzy_numbers = Series(
            {
                "red": FuzzyNumber([0, 0, 0.2, 0.3]),
                "green": FuzzyNumber([0.2, 0.4, 0.6, 0.8]),
                "blue": FuzzyNumber([0.7, 0.7, 1, 1]),
            }
        )
        self.scale = FuzzyScale(self.fuzzy_numbers)
        self.min_scale = FuzzyScale(
            self.fuzzy_numbers, preference_direction=PreferenceDirection.MIN
        )

    def test_constructor(self):
        with self.assertRaises(TypeError):
            FuzzyScale(Series({"a": 0, "b": 1}))

    def test_interval(self):
        self.assertEqual(self.scale.interval, Interval(0, 1))

    def test_numeric(self):
        self.assertEqual(self.scale.numeric, QuantitativeScale(0, 1))

    def test_equal(self):
        self.assertNotEqual(self.scale, QuantitativeScale(0, 1))
        self.assertNotEqual(self.scale, self.min_scale)
        self.assertNotEqual(
            self.scale,
            FuzzyScale(
                self.fuzzy_numbers,
                preference_direction=PreferenceDirection.MAX,
            ),
        )
        self.assertNotEqual(
            self.scale,
            FuzzyScale(
                Series(
                    {
                        "red": FuzzyNumber([0, 0, 0.2, 0.3]),
                        "GREEN": FuzzyNumber([0.2, 0.4, 0.6, 0.8]),
                        "blue": FuzzyNumber([0.7, 0.7, 1, 1]),
                    }
                )
            ),
        )
        scale = FuzzyScale(
            self.fuzzy_numbers, defuzzify_method="centre_of_maximum"
        )
        other_scale = FuzzyScale(
            Series(
                {
                    "red": FuzzyNumber([0, 0, 0.2, 0.3]),
                    "green": FuzzyNumber([0.2, 0.4, 0.6, 1]),
                    "blue": FuzzyNumber([0.7, 0.7, 1, 1]),
                }
            ),
            defuzzify_method="centre_of_maximum",
        )
        self.assertNotEqual(
            scale,
            other_scale,
        )
        self.assertEqual(
            self.scale,
            FuzzyScale(self.fuzzy_numbers),
        )

    def test_range(self):
        self.assertEqual(self.scale.range(), ["red", "green", "blue"])
        self.assertEqual(self.scale.range(nb=5), ["red", "green", "blue"])

    def test_contains(self):
        for label in self.scale.labels.copy():
            self.assertIn(label, self.scale)
        self.assertNotIn("GREEN", self.scale)
        self.assertNotIn(1, self.scale)

    def test_value(self):
        self.assertEqual(
            self.scale.value("red"),
            self.fuzzy_numbers["red"].centre_of_gravity,
        )
        with self.assertRaises(ValueError):
            self.scale.value("GREEN")

    def test_label(self):
        self.assertEqual(self.scale.label(self.scale.value("red")), "red")
        self.assertEqual(self.scale.label(0.2), "red")
        with self.assertRaises(ValueError):
            self.scale.label(1.1)

    def test_is_better(self):
        self.assertTrue(self.scale.is_better("green", "red"))
        self.assertFalse(self.scale.is_better("green", "blue"))
        with self.assertRaises(ValueError):
            self.scale.is_better("GREEN", "blue")
        self.assertTrue(self.min_scale.is_better("red", "green"))

    def test_is_better_or_equal(self):
        self.assertTrue(self.scale.is_better_or_equal("green", "red"))
        self.assertTrue(self.scale.is_better_or_equal("red", "red"))
        self.assertFalse(self.scale.is_better_or_equal("green", "blue"))
        with self.assertRaises(ValueError):
            self.scale.is_better_or_equal("GREEN", "blue")
        with self.assertRaises(ValueError):
            self.scale.is_better_or_equal("GREEN", "GREEN")
        self.assertTrue(self.min_scale.is_better_or_equal("red", "green"))

    def test_defuzzify(self):
        values = self.scale.defuzzify("centre_of_maximum")
        for k in self.scale.labels:
            self.assertEqual(values[k], self.scale.fuzzy[k].centre_of_maximum)

    def test_is_fuzzy_partition(self):
        self.assertFalse(self.scale.is_fuzzy_partition)
        s = FuzzyScale(
            Series(
                {
                    "Bad": FuzzyNumber([0.0, 0.0, 0.0, 2.0]),
                    "Medium": FuzzyNumber([0.0, 2.0, 2.0, 5.0]),
                    "Good": FuzzyNumber([2.0, 5.0, 5.0, 6.0]),
                }
            )
        )
        self.assertTrue(s.is_fuzzy_partition)

    def test_similarity(self):
        self.assertEqual(
            self.scale.similarity(
                self.fuzzy_numbers["red"], self.fuzzy_numbers["red"]
            ),
            1,
        )
        fa = FuzzyNumber([0] * 4)
        fb = FuzzyNumber([1] * 4)
        self.assertEqual(self.scale.similarity(fa, fb), 0)

    def test_fuzzyness(self):
        self.assertEqual(
            self.scale.fuzziness(FuzzyNumber([0.5, 0.5, 0.5, 0.5])), 0
        )
        self.assertEqual(
            self.scale.fuzziness(FuzzyNumber([0, 0.5, 0.5, 1])), 0.5
        )

    def test_specificity(self):
        self.assertEqual(self.scale.specificity(FuzzyNumber([1, 1, 1, 1])), 1)
        self.assertEqual(
            self.scale.specificity(FuzzyNumber([0, 0.5, 0.5, 1])), 0.5
        )
        self.assertEqual(self.scale.specificity(FuzzyNumber([0, 0, 1, 1])), 0)

    def test_ordinal_distance(self):
        self.assertEqual(self.scale.ordinal_distance("red", "red"), 0)
        self.assertEqual(self.scale.ordinal_distance("blue", "green"), 1)
        with self.assertRaises(ValueError):
            self.scale.ordinal_distance("god", "red")
        with self.assertRaises(ValueError):
            self.scale.ordinal_distance("blue", "worst")

    def test_fit(self):
        series = Series(["A", "C", "B", "B"])
        points = np.linspace(0, 1, num=8).tolist()
        expected = FuzzyScale(
            Series(
                {
                    "A": FuzzyNumber(points[:4]),
                    "C": FuzzyNumber(points[2:6]),
                    "B": FuzzyNumber(points[4:]),
                }
            )
        )
        self.assertEqual(expected, FuzzyScale.fit(series))


def test_common_scale_type():
    scales = [QuantitativeScale, NominalScale, FuzzyScale]
    assert common_scale_type(scales) == Scale
    scales = [QuantitativeScale, QualitativeScale, FuzzyScale]
    assert common_scale_type(scales) == OrdinalScale
    scales = [QuantitativeScale, BinaryScale, NormalScale]
    assert common_scale_type(scales) == QuantitativeScale
    assert common_scale_type([]) == Scale
