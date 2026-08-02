"""Tests for randomized Quickselect."""

import random
import unittest

from src.randomized_select import randomized_select, randomized_select_measured


class RandomizedSelectTests(unittest.TestCase):
    """Check correctness, local randomness, validation, and reproducibility."""

    def assert_ranks(self, values: list[int], seed: int = 532) -> None:
        expected = sorted(values)
        for k in range(1, len(values) + 1):
            self.assertEqual(expected[k - 1], randomized_select(values, k, seed=seed))

    def test_single_and_two_elements(self) -> None:
        self.assertEqual(7, randomized_select([7], 1, seed=1))
        self.assert_ranks([9, 2])

    def test_minimum_median_and_maximum(self) -> None:
        values = [8, 1, 5, 3, 9]
        self.assertEqual(1, randomized_select(values, 1, seed=2))
        self.assertEqual(5, randomized_select(values, 3, seed=2))
        self.assertEqual(9, randomized_select(values, 5, seed=2))

    def test_even_length_order_statistics(self) -> None:
        values = [4, 1, 3, 2]
        self.assertEqual(2, randomized_select(values, 2, seed=3))
        self.assertEqual(3, randomized_select(values, 3, seed=3))

    def test_sorted_and_reverse_sorted_inputs(self) -> None:
        self.assert_ranks(list(range(30)))
        self.assert_ranks(list(range(30, 0, -1)))

    def test_random_input(self) -> None:
        generator = random.Random(101)
        self.assert_ranks([generator.randint(-50, 50) for _ in range(61)])

    def test_repeated_all_equal_and_negative_values(self) -> None:
        self.assert_ranks([4, 1, 4, 2, 4, 1])
        self.assert_ranks([3] * 40)
        self.assert_ranks([-4, -10, -1, -7, -4])

    def test_copy_and_in_place_modes(self) -> None:
        values = [5, 4, 3, 2, 1]
        original = list(values)
        self.assertEqual(3, randomized_select(values, 3, seed=4))
        self.assertEqual(original, values)
        self.assertEqual(3, randomized_select(values, 3, seed=4, in_place=True))
        self.assertEqual(original, sorted(values, reverse=True))

    def test_empty_and_invalid_ranks_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            randomized_select([], 1)
        for k in (0, -1, 4):
            with self.subTest(k=k), self.assertRaises(ValueError):
                randomized_select([1, 2, 3], k)

    def test_invalid_types_are_rejected(self) -> None:
        for k in (1.0, "1", True):
            with self.subTest(k=k), self.assertRaises(TypeError):
                randomized_select([1], k)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            randomized_select((1, 2), 1)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            randomized_select([1, "2"], 1)  # type: ignore[list-item]
        with self.assertRaises(TypeError):
            randomized_select([False, 1], 1)

    def test_fixed_seed_reproduces_metrics(self) -> None:
        values = [9, 1, 8, 2, 7, 3, 6, 4, 5]
        first = randomized_select_measured(values, 5, seed=99)
        second = randomized_select_measured(values, 5, seed=99)
        self.assertEqual(first, second)

    def test_different_seeds_remain_correct(self) -> None:
        values = [10, 3, 7, 2, 8, 5, 1]
        for seed in range(10):
            self.assertEqual(5, randomized_select(values, 4, seed=seed))

    def test_global_random_state_is_unchanged(self) -> None:
        state = random.getstate()
        randomized_select([5, 1, 3], 2, seed=123)
        self.assertEqual(state, random.getstate())

    def test_measured_metrics_are_populated(self) -> None:
        selected, metrics = randomized_select_measured([8, 2, 6, 4], 2, seed=8)
        self.assertEqual(4, selected)
        self.assertGreater(metrics.comparisons, 0)
        self.assertGreater(metrics.partition_calls, 0)
        self.assertGreater(metrics.pivot_selections, 0)

    def test_large_inputs_complete(self) -> None:
        sorted_values = list(range(5000))
        repeated_values = [index % 7 for index in range(5000)]
        self.assertEqual(2499, randomized_select(sorted_values, 2500, seed=532))
        self.assertEqual(
            sorted(repeated_values)[2499],
            randomized_select(repeated_values, 2500, seed=532),
        )


if __name__ == "__main__":
    unittest.main()
