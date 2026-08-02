"""A last-in, first-out stack backed by DynamicArray."""

from typing import Generic, TypeVar

from src.dynamic_array import DynamicArray

T = TypeVar("T")


class ArrayStack(Generic[T]):
    """Provide amortized constant-time push and pop operations."""

    def __init__(self) -> None:
        self._items: DynamicArray[T] = DynamicArray()

    def push(self, value: T) -> None:
        """Place a value on top of the stack."""
        self._items.append(value)

    def pop(self) -> T:
        """Remove and return the top value."""
        if self.is_empty():
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T:
        """Return the top value without removing it."""
        if self.is_empty():
            raise IndexError("peek from empty stack")
        return self._items[len(self._items) - 1]

    def is_empty(self) -> bool:
        """Return whether the stack contains no values."""
        return len(self._items) == 0

    def size(self) -> int:
        """Return the number of values."""
        return len(self._items)

    def clear(self) -> None:
        """Remove every value."""
        self._items.clear()

    def to_list(self) -> list[T]:
        """Return values from bottom to top."""
        return self._items.to_list()
