"""Expected linear-time randomized Quickselect."""

import random

from src.metrics import SelectionMetrics
from src.partition import three_way_partition, validate_selection_request


def randomized_select(
    values: list[int],
    k: int,
    *,
    seed: int | None = None,
    in_place: bool = False,
) -> int:
    """Return the kth smallest value using a local randomized pivot generator."""
    selected, _ = randomized_select_measured(
        values, k, seed=seed, in_place=in_place
    )
    return selected


def randomized_select_measured(
    values: list[int],
    k: int,
    *,
    seed: int | None = None,
    in_place: bool = False,
) -> tuple[int, SelectionMetrics]:
    """Return the kth smallest value and metrics from randomized Quickselect."""
    validate_selection_request(values, k)
    working = values if in_place else list(values)
    generator = random.Random(seed)
    metrics = SelectionMetrics()
    low = 0
    high = len(working) - 1
    target = k - 1
    depth = 1

    while low <= high:
        metrics.recursive_calls += 1
        metrics.maximum_depth = max(metrics.maximum_depth, depth)
        if low == high:
            return working[low], metrics

        pivot_index = generator.randint(low, high)
        metrics.pivot_selections += 1
        equal_start, equal_end = three_way_partition(
            working, low, high, working[pivot_index], metrics
        )
        if target < equal_start:
            high = equal_start - 1
        elif target > equal_end:
            low = equal_end + 1
        else:
            return working[target], metrics
        depth += 1

    raise RuntimeError("selection did not find the requested rank")
