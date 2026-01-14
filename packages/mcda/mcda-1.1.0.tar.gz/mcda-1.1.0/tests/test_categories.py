import unittest

from pandas import Series

from mcda.categories import BoundedCategoryProfile, CentralCategoryProfile
from mcda.matrices import PerformanceTable
from mcda.scales import QuantitativeScale
from mcda.values import Values


class TestBoundedCategoryProfile(unittest.TestCase):
    def setUp(self):
        self.scales = {
            0: QuantitativeScale.normal(),
            1: QuantitativeScale.normal(),
            2: QuantitativeScale.normal(),
        }
        self.table = PerformanceTable(
            [[0.2, 0.2, 0.2], [0.4, 0.4, 0.4]], scales=self.scales
        )
        self.lowest = BoundedCategoryProfile(
            upper=self.table.alternatives_values[0]
        )
        self.upmost = BoundedCategoryProfile(
            lower=self.table.alternatives_values[1]
        )

    def test_constructor(self):
        p1 = self.table.alternatives_values[0]
        p2 = self.table.alternatives_values[1]
        c1 = BoundedCategoryProfile(p1, p2)
        c2 = BoundedCategoryProfile(p1)
        BoundedCategoryProfile(upper=p2)
        with self.assertRaises(ValueError):
            BoundedCategoryProfile(p2, p1)
        self.assertEqual(c1, BoundedCategoryProfile(p1, p2))
        self.assertNotEqual(c1, c2)
        self.assertNotEqual(c1, 2)

    def test_profiles_partition(self):
        partitions1 = BoundedCategoryProfile.profiles_partition(self.table)
        self.assertIn(self.lowest, partitions1)
        self.assertIn(self.upmost, partitions1)
        partitions2 = BoundedCategoryProfile.profiles_partition(
            self.table, lowest=False, upmost=False
        )
        self.assertNotIn(self.lowest, partitions2)
        self.assertNotIn(self.upmost, partitions2)
        bad_table = PerformanceTable(
            [[0.2, 0.2, 0.2], [0.1, 0.4, 0.4]], scales=self.scales
        )
        with self.assertRaises(ValueError):
            BoundedCategoryProfile.profiles_partition(bad_table)


class TestCentralCategoryProfile(unittest.TestCase):
    def test_constructor(self):
        scales = {
            0: QuantitativeScale.normal(),
            1: QuantitativeScale.normal(),
            2: QuantitativeScale.normal(),
        }
        p1 = Values(Series([0.4, 0.4, 0.4]), scales=scales)
        p2 = Values(Series([0.2, 0.4, 0.4]), scales=scales)
        c1 = CentralCategoryProfile(p1)
        c2 = CentralCategoryProfile(p2)
        self.assertEqual(c1, CentralCategoryProfile(p1))
        self.assertNotEqual(c1, c2)
        self.assertNotEqual(c1, 2)
