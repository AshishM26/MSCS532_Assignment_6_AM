"""A generic resizable array built on fixed-capacity list storage."""

from collections.abc import Iterator
from typing import Generic, TypeVar

T = TypeVar("T")


class DynamicArray(Generic[T]):
    """Store values in a geometrically resized backing array."""

    def __init__(self, initial_capacity: int = 4) -> None:
        if (
            isinstance(initial_capacity, bool)
            or not isinstance(initial_capacity, int)
            or initial_capacity <= 0
        ):
            raise ValueError("initial_capacity must be a positive integer")
        self._minimum_capacity = initial_capacity
        self._capacity = initial_capacity
        self._size = 0
        self._storage: list[T | None] = [None] * self._capacity

    @property
    def capacity(self) -> int:
        """Return the current number of allocated positions."""
        return self._capacity

    def _validate_access_index(self, index: int) -> None:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index >= self._size:
            raise IndexError("array index out of range")

    def _validate_insert_index(self, index: int) -> None:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index > self._size:
            raise IndexError("array insertion index out of range")

    def _resize(self, capacity: int) -> None:
        new_storage: list[T | None] = [None] * capacity
        for index in range(self._size):
            new_storage[index] = self._storage[index]
        self._storage = new_storage
        self._capacity = capacity

    def append(self, value: T) -> None:
        """Append a value in amortized constant time."""
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        self._storage[self._size] = value
        self._size += 1

    def insert(self, index: int, value: T) -> None:
        """Insert a value at an index, shifting later values right."""
        self._validate_insert_index(index)
        if self._size == self._capacity:
            self._resize(self._capacity * 2)
        for position in range(self._size, index, -1):
            self._storage[position] = self._storage[position - 1]
        self._storage[index] = value
        self._size += 1

    def get(self, index: int) -> T:
        """Return the value at an index."""
        self._validate_access_index(index)
        return self._storage[index]  # type: ignore[return-value]

    def set(self, index: int, value: T) -> None:
        """Replace the value at an index."""
        self._validate_access_index(index)
        self._storage[index] = value

    def delete(self, index: int) -> T:
        """Delete and return a value, shifting later values left."""
        self._validate_access_index(index)
        removed = self._storage[index]
        for position in range(index, self._size - 1):
            self._storage[position] = self._storage[position + 1]
        self._size -= 1
        self._storage[self._size] = None
        if (
            self._capacity > self._minimum_capacity
            and self._size <= self._capacity // 4
        ):
            self._resize(max(self._minimum_capacity, self._capacity // 2))
        return removed  # type: ignore[return-value]

    def pop(self, index: int | None = None) -> T:
        """Delete and return the final value or a specified indexed value."""
        if self._size == 0:
            raise IndexError("pop from empty DynamicArray")
        selected_index = self._size - 1 if index is None else index
        return self.delete(selected_index)

    def clear(self) -> None:
        """Remove all values and restore the minimum capacity."""
        self._capacity = self._minimum_capacity
        self._size = 0
        self._storage = [None] * self._capacity

    def contains(self, value: T) -> bool:
        """Return whether the first ``size`` positions contain a value."""
        return self.index_of(value) != -1

    def index_of(self, value: T) -> int:
        """Return the first matching index, or -1 when absent."""
        for index in range(self._size):
            if self._storage[index] == value:
                return index
        return -1

    def to_list(self) -> list[T]:
        """Return a copy of the logical values."""
        return [self._storage[index] for index in range(self._size)]  # type: ignore[misc]

    def __len__(self) -> int:
        return self._size

    def __getitem__(self, index: int) -> T:
        return self.get(index)

    def __setitem__(self, index: int, value: T) -> None:
        self.set(index, value)

    def __iter__(self) -> Iterator[T]:
        for index in range(self._size):
            yield self._storage[index]  # type: ignore[misc]
