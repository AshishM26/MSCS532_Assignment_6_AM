"""A first-in, first-out queue implemented as a circular array."""

from typing import Generic, TypeVar

T = TypeVar("T")


class CircularQueue(Generic[T]):
    """Avoid front-removal shifts by wrapping head and tail indexes."""

    def __init__(self, initial_capacity: int = 4) -> None:
        if (
            isinstance(initial_capacity, bool)
            or not isinstance(initial_capacity, int)
            or initial_capacity <= 0
        ):
            raise ValueError("initial_capacity must be a positive integer")
        self._minimum_capacity = initial_capacity
        self._capacity = initial_capacity
        self._storage: list[T | None] = [None] * initial_capacity
        self._head = 0
        self._tail = 0
        self._size = 0

    @property
    def capacity(self) -> int:
        """Return the current backing-storage capacity."""
        return self._capacity

    def _resize(self) -> None:
        new_capacity = self._capacity * 2
        new_storage: list[T | None] = [None] * new_capacity
        for index in range(self._size):
            new_storage[index] = self._storage[(self._head + index) % self._capacity]
        self._storage = new_storage
        self._capacity = new_capacity
        self._head = 0
        self._tail = self._size

    def enqueue(self, value: T) -> None:
        """Add a value at the logical tail."""
        if self._size == self._capacity:
            self._resize()
        self._storage[self._tail] = value
        self._tail = (self._tail + 1) % self._capacity
        self._size += 1

    def dequeue(self) -> T:
        """Remove and return the oldest value."""
        if self.is_empty():
            raise IndexError("dequeue from empty queue")
        value = self._storage[self._head]
        self._storage[self._head] = None
        self._head = (self._head + 1) % self._capacity
        self._size -= 1
        if self._size == 0:
            self._head = 0
            self._tail = 0
        return value  # type: ignore[return-value]

    def peek(self) -> T:
        """Return the oldest value without removing it."""
        if self.is_empty():
            raise IndexError("peek from empty queue")
        return self._storage[self._head]  # type: ignore[return-value]

    def is_empty(self) -> bool:
        """Return whether the queue contains no values."""
        return self._size == 0

    def size(self) -> int:
        """Return the number of queued values."""
        return self._size

    def clear(self) -> None:
        """Remove every value and restore the initial capacity."""
        self._capacity = self._minimum_capacity
        self._storage = [None] * self._capacity
        self._head = 0
        self._tail = 0
        self._size = 0

    def to_list(self) -> list[T]:
        """Return a copy in FIFO order."""
        return [
            self._storage[(self._head + index) % self._capacity]
            for index in range(self._size)
        ]  # type: ignore[misc]
