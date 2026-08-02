"""Benchmark deterministic and randomized kth-selection algorithms."""

from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
import sys
import time
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.deterministic_select import deterministic_select_measured
from src.metrics import SelectionMetrics
from src.randomized_select import randomized_select_measured

DATASET_SIZES = [100, 1000, 3500, 5000, 7000, 10000]
DATASET_TYPES = ("random", "sorted", "reverse_sorted", "repeated_values")
RANK_LABELS = ("minimum", "median", "p90")
DEFAULT_TRIALS = 5
SELECTION_RESULTS_PATH = Path("results/selection_results.csv")
RUNTIME_CHART_PATH = Path("results/selection_runtime_chart.png")
COMPARISONS_CHART_PATH = Path("results/selection_comparisons_chart.png")
CSV_FIELDS = [
    "algorithm",
    "dataset_type",
    "size",
    "rank_label",
    "k",
    "trial_count",
    "median_time_seconds",
    "mean_time_seconds",
    "standard_deviation_seconds",
    "minimum_time_seconds",
    "maximum_time_seconds",
    "comparisons",
    "swaps",
    "partition_calls",
    "pivot_selections",
    "recursive_calls",
    "maximum_depth",
    "groups_processed",
    "small_group_sorts",
    "status",
    "error_message",
]

MeasuredSelector = Callable[..., tuple[int, SelectionMetrics]]
ALGORITHMS: dict[str, MeasuredSelector] = {
    "Median of Medians": deterministic_select_measured,
    "Randomized Quickselect": randomized_select_measured,
}


def generate_dataset(dataset_type: str, size: int, seed: int = 532) -> list[int]:
    """Create one deterministic synthetic dataset."""
    if dataset_type not in DATASET_TYPES:
        raise ValueError(f"unsupported dataset type: {dataset_type}")
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        raise ValueError("size must be a positive integer")
    if dataset_type == "sorted":
        return list(range(size))
    if dataset_type == "reverse_sorted":
        return list(range(size, 0, -1))
    if dataset_type == "repeated_values":
        return [index % 10 for index in range(size)]
    generator = random.Random(seed + size)
    return [generator.randint(-10 * size, 10 * size) for _ in range(size)]


def rank_positions(size: int) -> dict[str, int]:
    """Return valid one-based ranks for the required benchmark labels."""
    if isinstance(size, bool) or not isinstance(size, int) or size <= 0:
        raise ValueError("size must be a positive integer")
    return {
        "minimum": 1,
        "median": (size + 1) // 2,
        "p90": max(1, math.ceil(0.90 * size)),
    }


def pivot_seed(dataset_type: str, size: int, rank_label: str) -> int:
    """Return a stable seed for a benchmark combination."""
    return 532_000 + DATASET_TYPES.index(dataset_type) * 10_000 + size + RANK_LABELS.index(rank_label)


def validate_trial_count(trials: int) -> None:
    """Reject invalid benchmark trial counts."""
    if isinstance(trials, bool) or not isinstance(trials, int) or trials <= 0:
        raise ValueError("trials must be a positive integer")


def filtered_sizes(max_size: int | None) -> list[int]:
    """Return configured sizes at or below an optional maximum."""
    if max_size is None:
        return list(DATASET_SIZES)
    if isinstance(max_size, bool) or not isinstance(max_size, int) or max_size <= 0:
        raise ValueError("max_size must be a positive integer")
    sizes = [size for size in DATASET_SIZES if size <= max_size]
    if not sizes:
        raise ValueError("max_size is smaller than every configured dataset size")
    return sizes


def expected_combination_count(sizes: list[int] | None = None) -> int:
    """Return the number of algorithm/distribution/size/rank combinations."""
    selected_sizes = DATASET_SIZES if sizes is None else sizes
    return len(ALGORITHMS) * len(DATASET_TYPES) * len(selected_sizes) * len(RANK_LABELS)


def verify_result(actual: int, expected: int) -> None:
    """Raise when a selector returns an incorrect order statistic."""
    if actual != expected:
        raise AssertionError(f"expected {expected}, received {actual}")


def _run_selector(
    algorithm_name: str,
    selector: MeasuredSelector,
    dataset: list[int],
    k: int,
    seed: int,
) -> tuple[int, SelectionMetrics]:
    if algorithm_name == "Randomized Quickselect":
        return selector(dataset, k, seed=seed)
    return selector(dataset, k)


def benchmark_combination(
    algorithm_name: str,
    selector: MeasuredSelector,
    dataset_type: str,
    size: int,
    rank_label: str,
    trials: int,
) -> dict[str, object]:
    """Measure one algorithm/distribution/size/rank combination."""
    validate_trial_count(trials)
    dataset = generate_dataset(dataset_type, size)
    k = rank_positions(size)[rank_label]
    expected = sorted(dataset)[k - 1]
    seed = pivot_seed(dataset_type, size, rank_label)
    times: list[float] = []
    metrics = SelectionMetrics()
    status = "completed"
    error_message = ""

    try:
        warmup, _ = _run_selector(algorithm_name, selector, dataset, k, seed)
        verify_result(warmup, expected)
        for _ in range(trials):
            start = time.perf_counter()
            actual, metrics = _run_selector(algorithm_name, selector, dataset, k, seed)
            elapsed = time.perf_counter() - start
            verify_result(actual, expected)
            times.append(elapsed)
    except Exception as error:  # Preserve failed combinations in the CSV.
        status = "failed"
        error_message = f"{type(error).__name__}: {error}"

    return {
        "algorithm": algorithm_name,
        "dataset_type": dataset_type,
        "size": size,
        "rank_label": rank_label,
        "k": k,
        "trial_count": len(times),
        "median_time_seconds": statistics.median(times) if times else "",
        "mean_time_seconds": statistics.mean(times) if times else "",
        "standard_deviation_seconds": statistics.pstdev(times) if times else "",
        "minimum_time_seconds": min(times) if times else "",
        "maximum_time_seconds": max(times) if times else "",
        "comparisons": metrics.comparisons,
        "swaps": metrics.swaps,
        "partition_calls": metrics.partition_calls,
        "pivot_selections": metrics.pivot_selections,
        "recursive_calls": metrics.recursive_calls,
        "maximum_depth": metrics.maximum_depth,
        "groups_processed": metrics.groups_processed,
        "small_group_sorts": metrics.small_group_sorts,
        "status": status,
        "error_message": error_message,
    }


def run_benchmark(sizes: list[int], trials: int) -> list[dict[str, object]]:
    """Run all configured selection benchmark combinations."""
    rows: list[dict[str, object]] = []
    total = expected_combination_count(sizes)
    completed = 0
    for algorithm_name, selector in ALGORITHMS.items():
        for dataset_type in DATASET_TYPES:
            for size in sizes:
                for rank_label in RANK_LABELS:
                    completed += 1
                    print(
                        f"[{completed:>3}/{total}] {algorithm_name}; "
                        f"{dataset_type}; n={size}; rank={rank_label}"
                    )
                    rows.append(
                        benchmark_combination(
                            algorithm_name,
                            selector,
                            dataset_type,
                            size,
                            rank_label,
                            trials,
                        )
                    )
    return rows


def write_results(rows: list[dict[str, object]], path: Path) -> None:
    """Write benchmark rows using the required CSV schema."""
    output = ROOT / path
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def create_runtime_chart(rows: list[dict[str, object]], path: Path) -> None:
    """Plot median-rank runtime by distribution and input size."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    figure, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    for axis, dataset_type in zip(axes.flat, DATASET_TYPES):
        for algorithm_name in ALGORITHMS:
            selected = [
                row
                for row in rows
                if row["dataset_type"] == dataset_type
                and row["algorithm"] == algorithm_name
                and row["rank_label"] == "median"
                and row["status"] == "completed"
            ]
            selected.sort(key=lambda row: int(row["size"]))
            if selected:
                axis.plot(
                    [int(row["size"]) for row in selected],
                    [float(row["median_time_seconds"]) for row in selected],
                    marker="o",
                    label=algorithm_name,
                )
        axis.set_title(dataset_type.replace("_", " ").title())
        axis.set_xlabel("Input size")
        axis.set_ylabel("Median time (seconds)")
        axis.grid(alpha=0.3)
    axes.flat[0].legend()
    figure.suptitle("Selection Runtime for the Median Rank")
    figure.tight_layout()
    output = ROOT / path
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)


def create_comparisons_chart(rows: list[dict[str, object]], path: Path) -> None:
    """Plot largest-size comparison counts for each required rank."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    completed_sizes = [int(row["size"]) for row in rows if row["status"] == "completed"]
    if not completed_sizes:
        raise ValueError("no completed rows are available for charting")
    largest_size = max(completed_sizes)
    figure, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    x_positions = list(range(len(DATASET_TYPES)))
    width = 0.36
    for axis, rank_label in zip(axes, RANK_LABELS):
        for offset, algorithm_name in enumerate(ALGORITHMS):
            values = []
            for dataset_type in DATASET_TYPES:
                match = next(
                    (
                        row
                        for row in rows
                        if row["algorithm"] == algorithm_name
                        and row["dataset_type"] == dataset_type
                        and int(row["size"]) == largest_size
                        and row["rank_label"] == rank_label
                        and row["status"] == "completed"
                    ),
                    None,
                )
                values.append(int(match["comparisons"]) if match else 0)
            shift = -width / 2 if offset == 0 else width / 2
            axis.bar(
                [position + shift for position in x_positions],
                values,
                width,
                label=algorithm_name,
            )
        axis.set_title(rank_label.upper())
        axis.set_xticks(x_positions)
        axis.set_xticklabels(
            [name.replace("_", "\n") for name in DATASET_TYPES], rotation=15
        )
        axis.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("Value-to-pivot comparisons")
    axes[0].legend()
    figure.suptitle(f"Selection Comparisons at n={largest_size:,}")
    figure.tight_layout()
    output = ROOT / path
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)


def parse_args() -> argparse.Namespace:
    """Parse command-line benchmark controls."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    parser.add_argument("--max-size", type=int)
    return parser.parse_args()


def main() -> None:
    """Run the benchmark and write its CSV and charts."""
    args = parse_args()
    validate_trial_count(args.trials)
    sizes = filtered_sizes(args.max_size)
    if args.trials != DEFAULT_TRIALS or sizes != DATASET_SIZES:
        print("WARNING: this reduced run overwrites the full result files.")
    rows = run_benchmark(sizes, args.trials)
    write_results(rows, SELECTION_RESULTS_PATH)
    create_runtime_chart(rows, RUNTIME_CHART_PATH)
    create_comparisons_chart(rows, COMPARISONS_CHART_PATH)
    failures = sum(row["status"] != "completed" for row in rows)
    print(f"Wrote {len(rows)} rows; failures: {failures}.")


if __name__ == "__main__":
    main()
