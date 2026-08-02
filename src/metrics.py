"""Instrumentation used by the selection algorithms."""

from dataclasses import dataclass


@dataclass
class SelectionMetrics:
    """Counters collected during one selection operation.

    A comparison is counted whenever an input value is compared with a pivot.
    A swap is counted only when different indexes exchange values. Partition,
    pivot, group, and small-sort counters record one completed occurrence.
    """

    comparisons: int = 0
    swaps: int = 0
    partition_calls: int = 0
    pivot_selections: int = 0
    recursive_calls: int = 0
    maximum_depth: int = 0
    groups_processed: int = 0
    small_group_sorts: int = 0


def record_swap(
    values: list[int], first: int, second: int, metrics: SelectionMetrics | None
) -> None:
    """Exchange two positions and count exchanges between different indexes."""
    if first == second:
        return
    values[first], values[second] = values[second], values[first]
    if metrics is not None:
        metrics.swaps += 1
