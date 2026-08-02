"""Worst-case linear-time selection using Median of Medians."""

from src.metrics import SelectionMetrics, record_swap
from src.partition import three_way_partition, validate_selection_request


def _insertion_sort_range(
    values: list[int], low: int, high: int, metrics: SelectionMetrics
) -> None:
    """Sort one small inclusive range without using a built-in sort."""
    for index in range(low + 1, high + 1):
        position = index
        while position > low:
            metrics.comparisons += 1
            if values[position - 1] <= values[position]:
                break
            record_swap(values, position - 1, position, metrics)
            position -= 1


def _group_ranges(low: int, high: int) -> list[tuple[int, int]]:
    """Return inclusive ranges containing at most five values each."""
    return [
        (start, min(start + 4, high))
        for start in range(low, high + 1, 5)
    ]


def _choose_pivot_median_of_medians(
    values: list[int], low: int, high: int, metrics: SelectionMetrics, depth: int
) -> int:
    """Choose a pivot by recursively selecting the median of group medians."""
    metrics.pivot_selections += 1
    medians: list[int] = []
    for group_low, group_high in _group_ranges(low, high):
        metrics.groups_processed += 1
        metrics.small_group_sorts += 1
        _insertion_sort_range(values, group_low, group_high, metrics)
        medians.append(values[(group_low + group_high) // 2])

    if len(medians) == 1:
        return medians[0]
    return _select_index(
        medians,
        0,
        len(medians) - 1,
        len(medians) // 2,
        metrics,
        depth + 1,
    )


def _select_index(
    values: list[int],
    low: int,
    high: int,
    target: int,
    metrics: SelectionMetrics,
    depth: int,
) -> int:
    """Select the value at a zero-based target index in the active range."""
    metrics.recursive_calls += 1
    metrics.maximum_depth = max(metrics.maximum_depth, depth)
    if low == high:
        return values[low]

    pivot = _choose_pivot_median_of_medians(values, low, high, metrics, depth)
    equal_start, equal_end = three_way_partition(values, low, high, pivot, metrics)
    if target < equal_start:
        return _select_index(values, low, equal_start - 1, target, metrics, depth + 1)
    if target > equal_end:
        return _select_index(values, equal_end + 1, high, target, metrics, depth + 1)
    return values[target]


def deterministic_select(
    values: list[int], k: int, *, in_place: bool = False
) -> int:
    """Return the kth smallest value using one-based ``k``."""
    selected, _ = deterministic_select_measured(values, k, in_place=in_place)
    return selected


def deterministic_select_measured(
    values: list[int], k: int, *, in_place: bool = False
) -> tuple[int, SelectionMetrics]:
    """Return the kth smallest value and metrics from Median of Medians."""
    validate_selection_request(values, k)
    working = values if in_place else list(values)
    metrics = SelectionMetrics()
    selected = _select_index(working, 0, len(working) - 1, k - 1, metrics, 1)
    return selected, metrics
