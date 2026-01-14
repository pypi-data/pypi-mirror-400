import unittest

from pandas import DataFrame, Series
from pandas.testing import assert_frame_equal, assert_series_equal

from mcda.set_functions import HashableSet, Mobius, SetFunction


class HashableSetTestCase(unittest.TestCase):
    def setUp(self):
        self.set = HashableSet(("a", "b"))

    def test_hash(self):
        self.assertEqual(hash(self.set), hash(HashableSet(("b", "a"))))

    def test_str(self):
        self.assertTrue(str(self.set) == "{a, b}" or str(self.set) == "{b, a}")

    def test_from_index(self):
        set_ = HashableSet.from_index(6)
        self.assertEqual(set_, HashableSet((1, 2)))
        set_ = HashableSet.from_index(6, ["_", "a", "b"])
        self.assertEqual(set_, self.set)
        self.assertRaises(ValueError, HashableSet.from_index, 3, [0])

    def test_from_mask(self):
        set_ = HashableSet.from_mask("110")
        self.assertEqual(set_, HashableSet((1, 2)))
        set_ = HashableSet.from_mask("110", ["_", "a", "b"])
        self.assertEqual(set_, self.set)

    def test_cardinal_range(self):
        res = HashableSet.cardinal_range(8)
        expected = [0, 1, 2, 4, 3, 5, 6, 7]
        self.assertEqual(expected, res)

        res = HashableSet.cardinal_range(2, 8)
        expected = [2, 4, 3, 5, 6, 7]
        self.assertEqual(expected, res)

    def test_natural_order(self):
        res = HashableSet.natural_order([0, 1, 2])
        expected = [
            HashableSet(),
            HashableSet((0,)),
            HashableSet((1,)),
            HashableSet((2,)),
            HashableSet((0, 1)),
            HashableSet((0, 2)),
            HashableSet((1, 2)),
            HashableSet((0, 1, 2)),
        ]
        self.assertEqual(res, expected)

    def test_logical_order(self):
        res = HashableSet.logical_order([0, 1, 2])
        expected = [
            HashableSet(),
            HashableSet((0,)),
            HashableSet((1,)),
            HashableSet((0, 1)),
            HashableSet((2,)),
            HashableSet((0, 2)),
            HashableSet((1, 2)),
            HashableSet((0, 1, 2)),
        ]
        self.assertEqual(res, expected)


class SetFunctionTestCase(unittest.TestCase):
    def setUp(self):
        self.values = {
            HashableSet(): 0,
            HashableSet(("a",)): 0.2,
            HashableSet(("b",)): 0.25,
            HashableSet(("a", "b")): 0.5,
            HashableSet(("c",)): 0.4,
        }
        self.ensemble = ["a", "b", "c"]
        self.function = SetFunction(self.values, self.ensemble)
        self.capacity = SetFunction(
            [
                0.0,
                0.07692307692307693,
                0.15384615384615385,
                0.38461538461538464,
                0.23076923076923078,
                0.46153846153846156,
                0.6153846153846154,
                0.8461538461538461,
                0.3076923076923077,
                0.5384615384615384,
                0.6923076923076923,
                0.9230769230769231,
                0.7692307692307693,
                1.0,
                1,
                1,
            ]
        )
        self.mobius = Mobius(
            [
                0,
                0.07692308,
                0.15384615,
                0.15384615,
                0.23076923,
                0.15384615,
                0.23076923,
                -0.15384615,
                0.30769231,
                0.15384615,
                0.23076923,
                -0.15384615,
                0.23076923,
                -0.15384615,
                -0.38461538,
                -0.07692308,
            ]
        )
        self.shapley = Series([0.1346154, 0.2115385, 0.2884615, 0.3653846])
        self.interaction_indexes = DataFrame(
            [
                [float("nan"), -0.02564103, -0.02564103, -0.02564103],
                [-0.02564103, float("nan"), -0.06410256, -0.06410256],
                [-0.02564103, -0.06410256, float("nan"), -0.06410256],
                [-0.02564103, -0.06410256, -0.06410256, float("nan")],
            ]
        )

    def test_constructor(self):
        self.assertEqual(self.function.values, self.values)
        self.assertEqual(set(self.function.ensemble), set(self.ensemble))

        f1 = SetFunction(self.values)
        self.assertEqual(set(f1.ensemble), set(self.ensemble))

        f2 = SetFunction(self.function)
        self.assertEqual(set(f2.ensemble), set(self.ensemble))
        self.assertEqual(f2.values, self.values)

        f3 = SetFunction([0, 0.2, 0.25, 0.5, 0.4], self.ensemble)
        self.assertEqual(set(f3.ensemble), set(self.ensemble))
        self.assertEqual(f3.values, self.values)

        f4 = SetFunction([0, 0.2, 0.25, 0.5, 0.4])
        self.assertEqual(f4.ensemble, [0, 1, 2])

        self.assertRaises(KeyError, SetFunction, self.values, ["a", "b"])
        SetFunction(self.values, ["a", "b"], validate=False)

    def test_iter(self):
        self.assertEqual(
            set(v for v in self.function), set(self.function.values.keys())
        )

    def test_contains(self):
        for e in self.ensemble:
            self.assertIn(e, self.function)

    def test_length(self):
        self.assertEqual(len(self.function), len(self.values))

    def test_ensemble(self):
        self.assertEqual(self.function.ensemble, self.function.ensemble)
        ensemble = self.function.ensemble
        ensemble += ["d"]
        self.assertNotEqual(self.function.ensemble, ensemble)

    def test_values(self):
        self.assertEqual(self.function.values, self.function.values)
        values = self.function.values
        values[HashableSet(("d",))] = 10
        self.assertNotEqual(self.function.values, values)

    def test_size(self):
        self.assertEqual(self.function.size, len(self.ensemble))

    def test_is_powerset_function(self):
        self.assertFalse(self.function.is_powerset_function)
        self.assertTrue(self.capacity.is_powerset_function)

    def test_is_game(self):
        self.assertTrue(self.function.is_game)
        self.assertFalse(SetFunction([1]).is_game)

    def test_is_monotonous(self):
        self.assertTrue(self.function.is_monotonous)
        self.assertFalse(SetFunction([1, 0]).is_monotonous)

    def test_is_normal(self):
        self.assertFalse(self.function.is_normal)
        self.assertFalse(SetFunction([0, 1, 2, 3]).is_normal)
        self.assertTrue(self.capacity.is_normal)

    def test_is_additive(self):
        self.assertFalse(self.function.is_additive)
        self.assertTrue(SetFunction([0, 1, 1, 2]).is_additive)

    def test_is_cardinality_based(self):
        self.assertFalse(self.function.is_cardinality_based)
        self.assertTrue(SetFunction([0, 1, 1, 2]).is_cardinality_based)

    def test_shapley(self):
        assert_series_equal(self.capacity.shapley, self.shapley)

    def test_interaction_index(self):
        assert_frame_equal(
            self.capacity.interaction_index, self.interaction_indexes
        )

    def test_mobius(self):
        mobius = self.capacity.mobius
        for k in mobius.values.keys():
            self.assertAlmostEqual(
                mobius(*k), self.mobius(*k)
            )  # Has 7-digits accuracy as R

    def test_is_k_additive(self):
        self.assertFalse(self.capacity.is_k_additive(1))
        self.assertTrue(SetFunction([0, 1, 1, 2]).is_k_additive(1))

    def test_is_capacity(self):
        self.assertFalse(SetFunction([0, 1, 2]).is_capacity)
        self.assertFalse(SetFunction([1]).is_capacity)
        self.assertFalse(SetFunction([0, 1, 2, 0]).is_capacity)
        self.assertFalse(SetFunction([0, 1, 2, 3]).is_capacity)
        self.assertTrue(SetFunction([0, 0.2, 0.3, 1]).is_capacity)

    def test_as_capacity(self):
        with self.assertRaises(KeyError):
            SetFunction([0, 1, 2]).as_capacity
        with self.assertRaises(ValueError):
            SetFunction([1]).as_capacity
        with self.assertRaises(ValueError):
            SetFunction([0, 1, 2, 0]).as_capacity
        with self.assertRaises(ValueError):
            SetFunction([0, 1, 2, 3]).as_capacity
        sf = SetFunction([0, 0.2, 0.3, 1])
        self.assertEqual(sf.as_capacity, sf)

    def test_uniform(self):
        u = SetFunction.uniform_capacity([0, 1, 2])
        self.assertTrue(u.is_capacity)
        self.assertTrue(u.is_additive)
        self.assertTrue(u.is_cardinality_based)

    def test_call(self):
        self.assertEqual(self.function("a"), 0.2)


class MobiusTestCase(unittest.TestCase):
    def setUp(self):
        self.values = {
            HashableSet(): 0,
            HashableSet(("a",)): 0.2,
            HashableSet(("b",)): 0.25,
            HashableSet(("a", "b")): 0.5,
            HashableSet(("c",)): 0.4,
        }
        self.ensemble = ["a", "b", "c"]
        self.function = SetFunction(self.values, self.ensemble)
        self.capacity = SetFunction(
            [
                0.0,
                0.07692307692307693,
                0.15384615384615385,
                0.38461538461538464,
                0.23076923076923078,
                0.46153846153846156,
                0.6153846153846154,
                0.8461538461538461,
                0.3076923076923077,
                0.5384615384615384,
                0.6923076923076923,
                0.9230769230769231,
                0.7692307692307693,
                1.0,
                1,
                1,
            ]
        )
        self.mobius = Mobius(
            [
                0,
                0.07692308,
                0.15384615,
                0.15384615,
                0.23076923,
                0.15384615,
                0.23076923,
                -0.15384615,
                0.30769231,
                0.15384615,
                0.23076923,
                -0.15384615,
                0.23076923,
                -0.15384615,
                -0.38461538,
                -0.07692308,
            ]
        )
        self.shapley = Series([0.1346154, 0.2115385, 0.2884615, 0.3653846])
        self.interaction_indexes = DataFrame(
            [
                [float("nan"), -0.02564103, -0.02564103, -0.02564103],
                [-0.02564103, float("nan"), -0.06410256, -0.06410256],
                [-0.02564103, -0.06410256, float("nan"), -0.06410256],
                [-0.02564103, -0.06410256, -0.06410256, float("nan")],
            ]
        )

    def test_contains(self):
        self.assertIn(0, self.mobius)
        self.assertNotIn(4, self.mobius)

    def test_ensemble(self):
        self.assertEqual(self.mobius.ensemble, [0, 1, 2, 3])

    def test_length(self):
        self.assertEqual(len(self.mobius), 16)

    def test_size(self):
        self.assertEqual(self.mobius.size, 4)

    def test_values(self):
        self.assertEqual(Mobius(self.values).values, self.values)

    def test_iter(self):
        self.assertEqual(
            set(v for v in self.mobius), set(self.mobius.values.keys())
        )

    def test_set_function(self):
        set_function = self.mobius.set_function
        for k in set_function.values.keys():
            self.assertAlmostEqual(
                set_function(*k), self.capacity(*k)
            )  # Has 7-digits accuracy as R

    def test_is_game(self):
        self.assertTrue(self.mobius.is_game)
        self.assertFalse(Mobius([1]).is_game)

    def test_is_power_set_function(self):
        self.assertTrue(self.mobius.is_game)
        self.assertFalse(Mobius([1, 2, 3]).is_game)

    def test_is_monotonous(self):
        self.assertTrue(self.function.mobius.is_monotonous)
        self.assertFalse(SetFunction([1, 0]).mobius.is_monotonous)

    def test_is_normal(self):
        self.assertFalse(self.function.mobius.is_normal)
        self.assertFalse(SetFunction([0, 1, 2, 3]).mobius.is_normal)
        self.assertTrue(self.mobius.is_normal)

    def test_is_additive(self):
        self.assertFalse(self.function.mobius.is_additive)
        self.assertTrue(SetFunction([0, 1, 1, 2]).mobius.is_additive)

    def test_is_cardinality_based(self):
        self.assertFalse(self.function.mobius.is_cardinality_based)
        self.assertTrue(SetFunction([0, 1, 1, 2]).mobius.is_cardinality_based)

    def test_is_k_additive(self):
        self.assertFalse(Mobius([0, 1, 2, 2]).is_k_additive(1))
        self.assertFalse(Mobius([0, 0, 0, 0]).is_k_additive(1))
        self.assertTrue(Mobius([0, 1, 2, 0]).is_k_additive(1))
        self.assertTrue(Mobius([0, 1, 2, 3, 0, 0, 0, 0]).is_k_additive(2))
        self.assertFalse(Mobius([0, 1, 2, 3, 0, 0, 0, 0]).is_k_additive(1))

    def test_is_capacity(self):
        self.assertFalse(Mobius([0, 1, 2]).is_capacity)
        self.assertFalse(Mobius([1]).is_capacity)
        self.assertFalse(SetFunction([0, 1, 0, 0]).mobius.is_capacity)
        self.assertFalse(SetFunction([0, 1, 2, 3]).mobius.is_capacity)
        self.assertTrue(
            Mobius(
                [
                    0,
                    0.07692308,
                    0.15384615,
                    0.15384615,
                    0.23076923,
                    0.15384615,
                    0.23076923,
                    -0.15384615,
                    0.30769231,
                    0.15384615,
                    0.23076923,
                    -0.15384615,
                    0.23076923,
                    -0.15384615,
                    -0.38461538,
                    -0.07692308,
                ]
            ).is_capacity
        )

    def test_as_capacity(self):
        with self.assertRaises(KeyError):
            Mobius([0, 1, 2]).as_capacity
        with self.assertRaises(ValueError):
            Mobius([1]).as_capacity
        with self.assertRaises(ValueError):
            SetFunction([0, 1, 0, 0]).mobius.as_capacity
        with self.assertRaises(ValueError):
            SetFunction([0, 1, 2, 3]).mobius.as_capacity
        m = Mobius(
            [
                0,
                0.07692308,
                0.15384615,
                0.15384615,
                0.23076923,
                0.15384615,
                0.23076923,
                -0.15384615,
                0.30769231,
                0.15384615,
                0.23076923,
                -0.15384615,
                0.23076923,
                -0.15384615,
                -0.38461538,
                -0.07692308,
            ]
        )
        self.assertEqual(m.as_capacity, m)

    def test_shapley(self):
        assert_series_equal(self.mobius.shapley, self.shapley)

    def test_interaction_index(self):
        assert_frame_equal(
            self.mobius.interaction_index, self.interaction_indexes
        )

    def test_call(self):
        self.assertEqual(self.mobius(), 0)
        self.assertEqual(self.mobius(0), 0.07692308)
        self.assertEqual(self.mobius(0, 1, 2, 3), -0.07692308)
