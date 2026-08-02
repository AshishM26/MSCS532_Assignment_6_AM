"""Benchmark representative elementary data-structure operation patterns."""

from __future__ import annotations

import argparse
import csv
import math
import statistics
import sys
import time
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.array_stack import ArrayStack
from src.circular_queue import CircularQueue
from src.dynamic_array import DynamicArray
from src.matrix import Matrix
from src.singly_linked_list import SinglyLinkedList

DATA_STRUCTURE_SIZES = [100, 1000, 5000, 10000, 25000]
DEFAULT_TRIALS = 5
DATA_STRUCTURE_RESULTS_PATH = Path("results/data_structure_results.csv")
OPERATIONS_CHART_PATH = Path("results/data_structure_operations_chart.png")
EXPERIMENTS = (
    ("DynamicArray", "append"),
    ("DynamicArray", "indexed_access"),
    ("DynamicArray", "front_insert"),
    ("SinglyLinkedList", "prepend"),
    ("SinglyLinkedList", "sampled_indexed_access"),
    ("ArrayStack", "push_then_pop"),
    ("CircularQueue", "enqueue_then_dequeue"),
    ("Matrix", "full_traversal"),
)
CSV_FIELDS = [
    "structure",
    "operation",
    "size",
    "trial_count",
    "median_time_seconds",
    "mean_time_seconds",
    "standard_deviation_seconds",
    "status",
    "error_message",
]

PreparedExperiment = tuple[Callable[[], None], Callable[[], None]]


def validate_trial_count(trials: int) -> None:
    """Reject invalid benchmark trial counts."""
    if isinstance(trials, bool) or not isinstance(trials, int) or trials <= 0:
        raise ValueError("trials must be a positive integer")


def prepare_experiment(structure: str, operation: str, size: int) -> PreparedExperiment:
    """Prepare untimed state and return timed work plus correctness verification."""
    result: dict[str, int] = {}

    if (structure, operation) == ("DynamicArray", "append"):
        values: DynamicArray[int] = DynamicArray()

        def run() -> None:
            for value in range(size):
                values.append(value)

        def verify() -> None:
            if len(values) != size or values[0] != 0 or values[size - 1] != size - 1:
                raise AssertionError("DynamicArray append verification failed")

        return run, verify

    if (structure, operation) == ("DynamicArray", "indexed_access"):
        values = DynamicArray[int]()
        for value in range(size):
            values.append(value)

        def run() -> None:
            result["total"] = sum(values[index] for index in range(size))

        def verify() -> None:
            if result.get("total") != size * (size - 1) // 2:
                raise AssertionError("DynamicArray indexed-access verification failed")

        return run, verify

    if (structure, operation) == ("DynamicArray", "front_insert"):
        values = DynamicArray[int]()

        def run() -> None:
            for value in range(size):
                values.insert(0, value)

        def verify() -> None:
            if len(values) != size or values[0] != size - 1 or values[size - 1] != 0:
                raise AssertionError("DynamicArray front-insert verification failed")

        return run, verify

    if (structure, operation) == ("SinglyLinkedList", "prepend"):
        values: SinglyLinkedList[int] = SinglyLinkedList()

        def run() -> None:
            for value in range(size):
                values.prepend(value)

        def verify() -> None:
            if len(values) != size or values.get(0) != size - 1:
                raise AssertionError("linked-list prepend verification failed")

        return run, verify

    if (structure, operation) == ("SinglyLinkedList", "sampled_indexed_access"):
        values = SinglyLinkedList[int]()
        for value in range(size):
            values.append(value)
        sample_step = max(1, size // 100)
        indexes = list(range(0, size, sample_step))

        def run() -> None:
            result["total"] = sum(values.get(index) for index in indexes)

        def verify() -> None:
            if result.get("total") != sum(indexes):
                raise AssertionError("linked-list sampled-access verification failed")

        return run, verify

    if (structure, operation) == ("ArrayStack", "push_then_pop"):
        stack: ArrayStack[int] = ArrayStack()

        def run() -> None:
            for value in range(size):
                stack.push(value)
            total = 0
            while not stack.is_empty():
                total += stack.pop()
            result["total"] = total

        def verify() -> None:
            if result.get("total") != size * (size - 1) // 2 or not stack.is_empty():
                raise AssertionError("stack verification failed")

        return run, verify

    if (structure, operation) == ("CircularQueue", "enqueue_then_dequeue"):
        queue: CircularQueue[int] = CircularQueue()

        def run() -> None:
            for value in range(size):
                queue.enqueue(value)
            ordered = True
            for expected in range(size):
                ordered = ordered and queue.dequeue() == expected
            result["ordered"] = int(ordered)

        def verify() -> None:
            if result.get("ordered") != 1 or not queue.is_empty():
                raise AssertionError("queue verification failed")

        return run, verify

    if (structure, operation) == ("Matrix", "full_traversal"):
        rows = max(1, math.isqrt(size))
        columns = math.ceil(size / rows)
        matrix = Matrix(rows, columns, 1)

        def run() -> None:
            result["total"] = sum(
                int(matrix.get(row, column))
                for row in range(rows)
                for column in range(columns)
            )

        def verify() -> None:
            if result.get("total") != rows * columns:
                raise AssertionError("matrix traversal verification failed")

        return run, verify

    raise ValueError(f"unsupported experiment: {structure}/{operation}")


def benchmark_experiment(
    structure: str, operation: str, size: int, trials: int
) -> dict[str, object]:
    """Measure one data-structure operation pattern."""
    validate_trial_count(trials)
    times: list[float] = []
    status = "completed"
    error_message = ""
    try:
        warmup, verify_warmup = prepare_experiment(structure, operation, size)
        warmup()
        verify_warmup()
        for _ in range(trials):
            run, verify = prepare_experiment(structure, operation, size)
            start = time.perf_counter()
            run()
            elapsed = time.perf_counter() - start
            verify()
            times.append(elapsed)
    except Exception as error:  # Preserve failed combinations in the CSV.
        status = "failed"
        error_message = f"{type(error).__name__}: {error}"

    return {
        "structure": structure,
        "operation": operation,
        "size": size,
        "trial_count": len(times),
        "median_time_seconds": statistics.median(times) if times else "",
        "mean_time_seconds": statistics.mean(times) if times else "",
        "standard_deviation_seconds": statistics.pstdev(times) if times else "",
        "status": status,
        "error_message": error_message,
    }


def run_benchmark(trials: int) -> list[dict[str, object]]:
    """Run all configured data-structure experiments."""
    rows: list[dict[str, object]] = []
    total = len(EXPERIMENTS) * len(DATA_STRUCTURE_SIZES)
    completed = 0
    for structure, operation in EXPERIMENTS:
        for size in DATA_STRUCTURE_SIZES:
            completed += 1
            print(f"[{completed:>2}/{total}] {structure}; {operation}; n={size}")
            rows.append(benchmark_experiment(structure, operation, size, trials))
    return rows


def write_results(rows: list[dict[str, object]], path: Path) -> None:
    """Write data-structure benchmark rows to CSV."""
    output = ROOT / path
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def create_operations_chart(rows: list[dict[str, object]], path: Path) -> None:
    """Plot operation timings in four readable structure groups."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    panels = (
        ("DynamicArray",),
        ("SinglyLinkedList",),
        ("ArrayStack", "CircularQueue"),
        ("Matrix",),
    )
    figure, axes = plt.subplots(2, 2, figsize=(12, 8))
    for axis, structures in zip(axes.flat, panels):
        labels = sorted(
            {
                (str(row["structure"]), str(row["operation"]))
                for row in rows
                if row["structure"] in structures and row["status"] == "completed"
            }
        )
        for structure, operation in labels:
            selected = [
                row
                for row in rows
                if row["structure"] == structure
                and row["operation"] == operation
                and row["status"] == "completed"
            ]
            selected.sort(key=lambda row: int(row["size"]))
            axis.plot(
                [int(row["size"]) for row in selected],
                [float(row["median_time_seconds"]) for row in selected],
                marker="o",
                label=f"{structure}: {operation.replace('_', ' ')}",
            )
        axis.set_title(" / ".join(structures))
        axis.set_xlabel("Operation count or approximate elements")
        axis.set_ylabel("Median time (seconds)")
        axis.set_xscale("log")
        axis.set_yscale("log")
        axis.grid(alpha=0.3)
        axis.legend(fontsize=8)
    figure.suptitle("Elementary Data-Structure Operation Patterns")
    figure.tight_layout()
    output = ROOT / path
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, dpi=160)
    plt.close(figure)


def parse_args() -> argparse.Namespace:
    """Parse the optional trial count."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trials", type=int, default=DEFAULT_TRIALS)
    return parser.parse_args()


def main() -> None:
    """Run the experiment and write its CSV and chart."""
    args = parse_args()
    validate_trial_count(args.trials)
    rows = run_benchmark(args.trials)
    write_results(rows, DATA_STRUCTURE_RESULTS_PATH)
    create_operations_chart(rows, OPERATIONS_CHART_PATH)
    failures = sum(row["status"] != "completed" for row in rows)
    print(f"Wrote {len(rows)} rows; failures: {failures}.")


if __name__ == "__main__":
    main()
