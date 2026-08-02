"""Tests for the shared three-way partition."""

import unittest

from src.metrics import SelectionMetrics
from src.partition import three_way_partition


class ThreeWayPartitionTests(unittest.TestCase):
    """Verify partition invariants and boundary behavior."""

    def test_partition_invariant_with_duplicates(self) -> None:
        values = [7, 3, 5, 3, 9, 3, 1]
        start, end = three_way_partition(values, 0, len(values) - 1, 3)
        self.assertTrue(all(value < 3 for value in values[:start]))
        self.assertTrue(all(value == 3 for value in values[start : end + 1]))
        self.assertTrue(all(value > 3 for value in values[end + 1 :]))

    def test_partition_preserves_outside_values(self) -> None:
        values = [99, 5, -1, 5, 8, 2, 77]
        start, end = three_way_partition(values, 1, 5, 5)
        self.assertEqual((99, 77), (values[0], values[-1]))
        self.assertTrue(all(value < 5 for value in values[1:start]))
        self.assertTrue(all(value == 5 for value in values[start : end + 1]))
        self.assertTrue(all(value > 5 for value in values[end + 1 : 6]))

    def test_all_equal_values(self) -> None:
        values = [4, 4, 4, 4]
        self.assertEqual((0, 3), three_way_partition(values, 0, 3, 4))

    def test_negative_values(self) -> None:
        values = [-2, -8, -2, -1]
        start, end = three_way_partition(values, 0, 3, -2)
        self.assertTrue(all(value < -2 for value in values[:start]))
        self.assertEqual([-2, -2], values[start : end + 1])

    def test_metrics_are_populated(self) -> None:
        values = [3, 1, 3, 2]
        metrics = SelectionMetrics()
        three_way_partition(values, 0, 3, 3, metrics)
        self.assertEqual(1, metrics.partition_calls)
        self.assertGreater(metrics.comparisons, 0)

    def test_invalid_bounds_are_rejected(self) -> None:
        with self.assertRaises(IndexError):
            three_way_partition([1, 2], 1, 0, 1)
        with self.assertRaises(IndexError):
            three_way_partition([1, 2], 0, 2, 1)

    def test_invalid_index_type_is_rejected(self) -> None:
        with self.assertRaises(TypeError):
            three_way_partition([1], True, 0, 1)

    def test_empty_input_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            three_way_partition([], 0, 0, 1)


if __name__ == "__main__":
    unittest.main()
