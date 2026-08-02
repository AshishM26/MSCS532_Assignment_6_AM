"""Fast contract tests for benchmark configuration and helpers."""

import tempfile
import unittest
from pathlib import Path

from benchmarks import benchmark_data_structures as data_benchmark
from benchmarks import benchmark_selection as selection_benchmark


class BenchmarkContractTests(unittest.TestCase):
    def test_dataset_generation_is_deterministic(self) -> None:
        for dataset_type in selection_benchmark.DATASET_TYPES:
            self.assertEqual(
                selection_benchmark.generate_dataset(dataset_type, 100),
                selection_benchmark.generate_dataset(dataset_type, 100),
            )

    def test_required_selection_configuration(self) -> None:
        self.assertEqual(
            [100, 1000, 3500, 5000, 7000, 10000],
            selection_benchmark.DATASET_SIZES,
        )
        self.assertEqual(
            {"random", "sorted", "reverse_sorted", "repeated_values"},
            set(selection_benchmark.DATASET_TYPES),
        )
        self.assertEqual(144, selection_benchmark.expected_combination_count())

    def test_rank_labels_produce_valid_k_values(self) -> None:
        for size in selection_benchmark.DATASET_SIZES:
            ranks = selection_benchmark.rank_positions(size)
            self.assertEqual(set(selection_benchmark.RANK_LABELS), set(ranks))
            self.assertTrue(all(1 <= k <= size for k in ranks.values()))

    def test_fixed_pivot_seeds_are_reproducible(self) -> None:
        first = selection_benchmark.pivot_seed("random", 1000, "median")
        second = selection_benchmark.pivot_seed("random", 1000, "median")
        self.assertEqual(first, second)

    def test_trial_count_validation(self) -> None:
        for invalid in (0, -1, True):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                selection_benchmark.validate_trial_count(invalid)
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                data_benchmark.validate_trial_count(invalid)

    def test_csv_schemas_and_paths(self) -> None:
        self.assertEqual("algorithm", selection_benchmark.CSV_FIELDS[0])
        self.assertIn("status", selection_benchmark.CSV_FIELDS)
        self.assertEqual("structure", data_benchmark.CSV_FIELDS[0])
        self.assertIn("error_message", data_benchmark.CSV_FIELDS)
        self.assertFalse(selection_benchmark.SELECTION_RESULTS_PATH.is_absolute())
        self.assertFalse(data_benchmark.DATA_STRUCTURE_RESULTS_PATH.is_absolute())

    def test_verification_detects_wrong_results(self) -> None:
        selection_benchmark.verify_result(4, 4)
        with self.assertRaises(AssertionError):
            selection_benchmark.verify_result(3, 4)

    def test_reduced_size_filtering(self) -> None:
        self.assertEqual(
            [100, 1000, 3500, 5000], selection_benchmark.filtered_sizes(5000)
        )
        with self.assertRaises(ValueError):
            selection_benchmark.filtered_sizes(50)

    def test_data_structure_configuration(self) -> None:
        self.assertEqual([100, 1000, 5000, 10000, 25000], data_benchmark.DATA_STRUCTURE_SIZES)
        self.assertEqual(8, len(data_benchmark.EXPERIMENTS))
        for structure, operation in data_benchmark.EXPERIMENTS:
            run, verify = data_benchmark.prepare_experiment(structure, operation, 10)
            run()
            verify()

    def test_chart_functions_accept_small_synthetic_rows(self) -> None:
        selection_rows = []
        for algorithm in selection_benchmark.ALGORITHMS:
            for dataset_type in selection_benchmark.DATASET_TYPES:
                for rank_label in selection_benchmark.RANK_LABELS:
                    selection_rows.append(
                        {
                            "algorithm": algorithm,
                            "dataset_type": dataset_type,
                            "size": 100,
                            "rank_label": rank_label,
                            "median_time_seconds": 0.001,
                            "comparisons": 100,
                            "status": "completed",
                        }
                    )
        data_rows = [
            {
                "structure": structure,
                "operation": operation,
                "size": 100,
                "median_time_seconds": 0.001,
                "status": "completed",
            }
            for structure, operation in data_benchmark.EXPERIMENTS
        ]
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            selection_benchmark.create_runtime_chart(
                selection_rows, directory / "runtime.png"
            )
            selection_benchmark.create_comparisons_chart(
                selection_rows, directory / "comparisons.png"
            )
            data_benchmark.create_operations_chart(
                data_rows, directory / "operations.png"
            )
            self.assertTrue((directory / "runtime.png").is_file())
            self.assertTrue((directory / "comparisons.png").is_file())
            self.assertTrue((directory / "operations.png").is_file())


if __name__ == "__main__":
    unittest.main()
