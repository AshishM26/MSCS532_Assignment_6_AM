# MSCS 532 Assignment 6

**Student:** Ashish Mahajan

**Course:** MSCS 532-B01 - Algorithms and Data Structures

**Instructor:** Dr. Michael Solomon

**Assignment:** Assignment 6 - Medians and Order Statistics & Elementary Data Structures

**Repository:** [MSCS532_Assignment_6_AM](https://github.com/AshishM26/MSCS532_Assignment_6_AM)

## Overview

This project implements two algorithms for selecting the kth smallest value without fully sorting the input:

- deterministic Median of Medians with worst-case `Theta(n)` time;
- randomized Quickselect with expected `Theta(n)` time.

Both algorithms use one-based ranks and a shared three-way partition that handles duplicate values directly. The project also implements a dynamic array, matrix, array-based stack, circular array queue, and singly linked list from scratch. Tests, reproducible benchmarks, charts, and a generic cloud-operations demonstration connect the theoretical analysis to observed behavior.

The detailed design, proofs, empirical analysis, applications, and references are in [report.md](report.md).

## Assignment Requirements and Learning Objectives

The repository addresses both required parts of the assignment:

1. Implement and analyze deterministic and randomized order-statistic selection.
2. Implement and compare elementary data structures and their operations.

The main objectives are to explain why selection can avoid full sorting, distinguish worst-case and expected complexity, measure algorithm behavior across different inputs, and connect data-structure choices to access, insertion, deletion, memory, and workload requirements.

## Algorithms

`deterministic_select(values, k)` divides the active range into groups of at most five, insertion-sorts each small group, recursively selects the median of the group medians, and continues only in the partition containing the target rank. The group-of-five pivot guarantee gives the recurrence

`T(n) <= T(ceil(n/5)) + T(7n/10 + c) + O(n)`,

which resolves to worst-case `Theta(n)`.

`randomized_select(values, k, seed=...)` chooses a uniformly random pivot from the active range using a local `random.Random` instance. It iteratively narrows the active range, giving expected `Theta(n)` time and worst-case `Theta(n^2)` time.

The public APIs preserve the caller's list by default. Passing `in_place=True` permits rearrangement. The measured variants also return a `SelectionMetrics` instance.

## Data Structures

- `DynamicArray` uses fixed-capacity backing storage, doubling when full and shrinking only when substantially underused.
- `Matrix` maintains a positive rectangular shape using nested `DynamicArray` rows.
- `ArrayStack` provides LIFO operations on a `DynamicArray`.
- `CircularQueue` provides FIFO operations without shifting the remaining values after a dequeue.
- `SinglyLinkedList` maintains head, tail, and size for constant-time endpoint insertion.

## Repository Structure

```text
MSCS532_Assignment_6_AM/
├── benchmarks/
│   ├── benchmark_data_structures.py
│   └── benchmark_selection.py
├── examples/
│   └── cloud_operations_demo.py
├── results/
│   ├── data_structure_operations_chart.png
│   ├── data_structure_results.csv
│   ├── selection_comparisons_chart.png
│   ├── selection_results.csv
│   └── selection_runtime_chart.png
├── src/
│   ├── array_stack.py
│   ├── circular_queue.py
│   ├── deterministic_select.py
│   ├── dynamic_array.py
│   ├── matrix.py
│   ├── metrics.py
│   ├── partition.py
│   ├── randomized_select.py
│   └── singly_linked_list.py
├── tests/
├── README.md
├── report.md
└── requirements.txt
```

## Setup

Python 3.11 or newer is recommended. The algorithms and data structures use only the standard library; Matplotlib is used to create charts.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Run the Tests

```bash
python3 -m unittest discover -s tests -v
```

The validated repository contains 93 meaningful tests covering algorithms, edge cases, metrics, data-structure invariants, and benchmark contracts.

## Run the Benchmarks

```bash
python3 benchmarks/benchmark_selection.py
python3 benchmarks/benchmark_selection.py --trials 3
python3 benchmarks/benchmark_selection.py --max-size 5000
python3 benchmarks/benchmark_data_structures.py
```

Reduced selection runs warn that they overwrite the full result files. The committed results contain the required full runs: 144 selection rows and 40 data-structure rows, each with five completed trials and no failures.

## Run the Demonstration

```bash
python3 examples/cloud_operations_demo.py
```

The deterministic demonstration selects a median-rank deployment duration of 73 seconds and a p90-rank duration of 95 seconds. It also demonstrates inventory updates, a region matrix, LIFO rollback steps, FIFO job processing, and mutable workflow steps without contacting external services.

## Generated Outputs

- [selection_results.csv](results/selection_results.csv): execution-time and operation metrics for two algorithms, four distributions, six sizes, and three ranks.
- [selection_runtime_chart.png](results/selection_runtime_chart.png): median-rank runtime by input distribution.
- [selection_comparisons_chart.png](results/selection_comparisons_chart.png): comparison counts for minimum, median, and p90 ranks at `n=10,000`.
- [data_structure_results.csv](results/data_structure_results.csv): timings for eight operation patterns across five sizes.
- [data_structure_operations_chart.png](results/data_structure_operations_chart.png): log-scaled operation trends grouped by structure.

## Actual Findings

At `n=10,000`, Median of Medians used 38,509 to 96,701 recorded comparisons across the tested distribution/rank combinations and completed in 4.244 to 12.258 ms. Its bounded pivot quality avoided an input-order worst case.

Randomized Quickselect used 22,537 to 79,236 comparisons and completed in 2.016 to 6.549 ms across the same cases. It was faster in every tested `n=10,000` combination, but this observation does not replace its expected-time analysis or remove its `Theta(n^2)` mathematical worst case.

Three-way partitioning handled repeated values without repeatedly separating equal keys. At `n=10,000`, randomized selection used 4, 6, and 6 partitions for the minimum, median, and p90 ranks on the repeated-value dataset.

The data-structure experiment showed the expected operation patterns. At 25,000 operations, DynamicArray front insertion took a measured median of 9.700062 seconds because accumulated shifting is quadratic, while linked-list prepend took 0.004656 seconds. DynamicArray indexed access took 0.003227 seconds, whereas 100 sampled linked-list indexed accesses took 0.017541 seconds because each sample requires traversal. Circular queue enqueue/dequeue preserved FIFO order without front shifts.

No statistical significance test was performed, and the measured constants are specific to this Python implementation and execution environment.

## Complexity Summary

| Component or operation | Time complexity | Auxiliary-space note |
|---|---:|---|
| Median of Medians selection | `Theta(n)` worst case | `O(n)` in this implementation for copied input and group-median lists |
| Randomized Quickselect | `Theta(n)` expected; `Theta(n^2)` worst case | `O(1)` algorithmic in-place; copy mode adds `O(n)` |
| DynamicArray access/set | `O(1)` | Capacity can exceed size |
| DynamicArray append | `O(1)` amortized | Resize is `O(n)` |
| DynamicArray arbitrary insert/delete | `O(n)` | Values may shift |
| Matrix cell access/set | `O(1)` | Matrix storage is `O(rows x columns)` |
| Matrix column insert/delete | `O(rows x columns)` worst case | Each row may shift |
| ArrayStack push/pop | `O(1)` amortized | Backing array may resize |
| CircularQueue enqueue/dequeue | `O(1)` amortized / `O(1)` | Storage is `O(capacity)` |
| SinglyLinkedList prepend/append | `O(1)` | Each node stores a next reference |
| SinglyLinkedList indexed access/search | `O(n)` | Sequential traversal |

## Known Limitations

- Selection accepts a Python `list[int]` and one-based `k`; Boolean values are rejected.
- The Matrix intentionally retains at least one row and one column.
- Python object overhead and instrumentation affect measured constants.
- The benchmarks compare operation patterns and do not claim that unlike structures are interchangeable.
- Randomized Quickselect improves expected behavior but cannot eliminate its worst case.

## Version Control

The local history separates repository setup, algorithms, tests and benchmark framework, data structures, demonstrations and data-structure benchmarks, generated results, and final documentation. The work remains unpushed until human review.

## References

- Blum, M., Floyd, R. W., Pratt, V. R., Rivest, R. L., & Tarjan, R. E. (1973). Time bounds for selection. *Journal of Computer and System Sciences, 7*(4), 448-461. https://doi.org/10.1016/S0022-0000(73)80033-9
- Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2022). *Introduction to algorithms* (4th ed.). MIT Press.
- Hoare, C. A. R. (1961). Algorithm 65: FIND. *Communications of the ACM, 4*(7), 321-322. https://doi.org/10.1145/366622.366647
- Python Software Foundation. [random — Generate pseudo-random numbers](https://docs.python.org/3/library/random.html).
- Python Software Foundation. [time — Time access and conversions](https://docs.python.org/3/library/time.html#time.perf_counter).
