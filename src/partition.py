"""Shared three-way partitioning for order-statistic selection."""

from src.metrics import SelectionMetrics, record_swap


def validate_selection_request(values: list[int], k: int) -> None:
    """Validate the public list and one-based rank arguments."""
    if not isinstance(values, list):
        raise TypeError("values must be a Python list")
    if not values:
        raise ValueError("cannot select an element from an empty list")
    if any(isinstance(value, bool) or not isinstance(value, int) for value in values):
        raise TypeError("values must contain integers and not Boolean values")
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError("k must be an integer and not a Boolean value")
    if not 1 <= k <= len(values):
        raise ValueError("k must be between 1 and the number of values")


def three_way_partition(
    values: list[int],
    low: int,
    high: int,
    pivot_value: int,
    metrics: SelectionMetrics | None = None,
) -> tuple[int, int]:
    """Partition ``values[low:high + 1]`` into less, equal, and greater regions."""
    if not isinstance(values, list):
        raise TypeError("values must be a Python list")
    if not values:
        raise ValueError("values must not be empty")
    if any(isinstance(index, bool) or not isinstance(index, int) for index in (low, high)):
        raise TypeError("low and high must be integer indexes")
    if low < 0 or high >= len(values) or low > high:
        raise IndexError("partition bounds are outside the list")
    if isinstance(pivot_value, bool) or not isinstance(pivot_value, int):
        raise TypeError("pivot_value must be an integer")
    if metrics is not None:
        metrics.partition_calls += 1

    less = low
    current = low
    greater = high
    while current <= greater:
        if metrics is not None:
            metrics.comparisons += 1
        if values[current] < pivot_value:
            record_swap(values, less, current, metrics)
            less += 1
            current += 1
            continue

        if metrics is not None:
            metrics.comparisons += 1
        if values[current] > pivot_value:
            record_swap(values, current, greater, metrics)
            greater -= 1
        else:
            current += 1

    return less, greater
