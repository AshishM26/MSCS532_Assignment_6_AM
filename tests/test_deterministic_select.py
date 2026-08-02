"""Tests for deterministic Median-of-Medians selection."""

import random
import unittest
from unittest.mock import patch

from src.deterministic_select import (
    _group_ranges,
    deterministic_select,
    deterministic_select_measured,
)


class DeterministicSelectTests(unittest.TestCase):
    """Check order-statistic correctness, validation, and metrics."""

    def assert_ranks(self, values: list[int]) -> None:
        expected = sorted(values)
        for k in range(1, len(values) + 1):
            self.assertEqual(expected[k - 1], deterministic_select(values, k))

    def test_single_element(self) -> None:
        self.assertEqual(7, deterministic_select([7], 1))

    def test_two_elements(self) -> None:
        self.assert_ranks([9, 2])

    def test_odd_length_minimum_median_and_maximum(self) -> None:
        values = [8, 1, 5, 3, 9]
        self.assertEqual(1, deterministic_select(values, 1))
        self.assertEqual(5, deterministic_select(values, 3))
        self.assertEqual(9, deterministic_select(values, 5))

    def test_even_length_selects_order_statistics(self) -> None:
        values = [4, 1, 3, 2]
        self.assertEqual(2, deterministic_select(values, 2))
        self.assertEqual(3, deterministic_select(values, 3))

    def test_sorted_input(self) -> None:
        self.assert_ranks(list(range(25)))

    def test_reverse_sorted_input(self) -> None:
        self.assert_ranks(list(range(25, 0, -1)))

    def test_random_input(self) -> None:
        generator = random.Random(532)
        self.assert_ranks([generator.randint(-100, 100) for _ in range(51)])

    def test_repeated_and_all_equal_values(self) -> None:
        self.assert_ranks([5, 1, 5, 2, 5, 1, 2])
        self.assert_ranks([6] * 20)

    def test_negative_and_mixed_values(self) -> None:
        self.assert_ranks([-4, -10, -1, -7])
        self.assert_ranks([0, 12, -5, 8, -2, 12, 3])

    def test_copy_mode_preserves_input(self) -> None:
        values = [5, 3, 4, 1, 2]
        original = list(values)
        deterministic_select(values, 3)
        self.assertEqual(original, values)

    def test_in_place_mode_returns_correct_value(self) -> None:
        values = [5, 4, 3, 2, 1]
        self.assertEqual(3, deterministic_select(values, 3, in_place=True))
        self.assertEqual([1, 2, 3, 4, 5], sorted(values))

    def test_empty_and_invalid_ranks_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            deterministic_select([], 1)
        for k in (0, -1, 4):
            with self.subTest(k=k), self.assertRaises(ValueError):
                deterministic_select([1, 2, 3], k)

    def test_invalid_rank_types_are_rejected(self) -> None:
        for k in (1.0, "1", True):
            with self.subTest(k=k), self.assertRaises(TypeError):
                deterministic_select([1], k)  # type: ignore[arg-type]

    def test_invalid_values_are_rejected(self) -> None:
        with self.assertRaises(TypeError):
            deterministic_select((1, 2), 1)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            deterministic_select([1, "2"], 1)  # type: ignore[list-item]
        with self.assertRaises(TypeError):
            deterministic_select([1, True], 1)

    def test_measured_output_and_metrics(self) -> None:
        selected, metrics = deterministic_select_measured([8, 2, 6, 4], 2)
        self.assertEqual(4, selected)
        self.assertGreater(metrics.comparisons, 0)
        self.assertGreater(metrics.pivot_selections, 0)
        self.assertGreater(metrics.groups_processed, 0)
        self.assertGreater(metrics.small_group_sorts, 0)

    def test_groups_contain_at_most_five_values(self) -> None:
        for low, high in _group_ranges(0, 27):
            self.assertLessEqual(high - low + 1, 5)

    def test_algorithm_does_not_use_random_pivots(self) -> None:
        with patch("random.Random", side_effect=AssertionError("unexpected random pivot")):
            self.assertEqual(4, deterministic_select([9, 4, 1], 2))

    def test_large_sorted_input_completes(self) -> None:
        values = list(range(3000))
        self.assertEqual(1499, deterministic_select(values, 1500))

    def test_large_repeated_input_completes(self) -> None:
        values = [index % 9 for index in range(5000)]
        self.assertEqual(sorted(values)[2499], deterministic_select(values, 2500))


if __name__ == "__main__":
    unittest.main()
