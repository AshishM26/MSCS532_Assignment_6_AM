"""Deterministic examples using generic synthetic cloud-operations data."""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.array_stack import ArrayStack
from src.circular_queue import CircularQueue
from src.deterministic_select import deterministic_select
from src.dynamic_array import DynamicArray
from src.matrix import Matrix
from src.randomized_select import randomized_select
from src.singly_linked_list import SinglyLinkedList


def main() -> None:
    """Run all Assignment 6 examples without external services."""
    durations = [84, 61, 95, 73, 68, 110, 57, 76, 89, 64]
    median_k = (len(durations) + 1) // 2
    p90_k = math.ceil(0.90 * len(durations))
    deterministic_median = deterministic_select(durations, median_k)
    randomized_median = randomized_select(durations, median_k, seed=532)
    deterministic_p90 = deterministic_select(durations, p90_k)
    randomized_p90 = randomized_select(durations, p90_k, seed=532)
    assert (deterministic_median, deterministic_p90) == (
        randomized_median,
        randomized_p90,
    )
    print("Order statistics")
    print(f"  Durations: {durations}")
    print(f"  Median-rank duration: {deterministic_median} seconds")
    print(f"  P90-rank duration: {deterministic_p90} seconds")

    inventory: DynamicArray[str] = DynamicArray()
    inventory.append("compute-service")
    inventory.append("object-storage")
    inventory.insert(1, "network-gateway")
    accessed = inventory.get(1)
    removed = inventory.delete(0)
    print("DynamicArray")
    print(f"  Accessed: {accessed}; removed: {removed}; remaining: {inventory.to_list()}")

    capacity = Matrix.from_rows([[12, 8], [7, 5]])
    selected_cell = capacity.get(0, 1)
    capacity.append_column([4, 3])
    removed_region = capacity.delete_column(0)
    print("Matrix")
    print(
        f"  Selected cell: {selected_cell}; removed region: {removed_region}; "
        f"shape: {capacity.shape}; values: {capacity.to_lists()}"
    )

    rollback: ArrayStack[str] = ArrayStack()
    for step in ["database-migration", "backend-deployment", "frontend-deployment"]:
        rollback.push(step)
    rollback_order = [rollback.pop(), rollback.pop(), rollback.pop()]
    print(f"ArrayStack rollback order: {rollback_order}")

    jobs: CircularQueue[str] = CircularQueue()
    for job in ["network-check", "secret-validation", "monitoring-validation"]:
        jobs.enqueue(job)
    processing_order = [jobs.dequeue(), jobs.dequeue(), jobs.dequeue()]
    print(f"CircularQueue processing order: {processing_order}")

    workflow: SinglyLinkedList[str] = SinglyLinkedList()
    workflow.append("network-check")
    workflow.append("backend-deployment")
    workflow.insert(1, "secret-validation")
    workflow.delete_value("network-check")
    forward = workflow.traverse()
    workflow.reverse()
    print(f"SinglyLinkedList workflow: {forward}; reversed: {workflow.traverse()}")


if __name__ == "__main__":
    main()
