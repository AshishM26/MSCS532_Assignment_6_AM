"""A generic singly linked list with head and tail references."""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Node(Generic[T]):
    """Store one linked-list value and its successor reference."""

    value: T
    next: "Node[T] | None" = None


class SinglyLinkedList(Generic[T]):
    """Maintain a mutable sequence with constant-time endpoint insertion."""

    def __init__(self) -> None:
        self.head: Node[T] | None = None
        self.tail: Node[T] | None = None
        self.size = 0

    def _validate_access_index(self, index: int) -> None:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index >= self.size:
            raise IndexError("linked-list index out of range")

    def _validate_insert_index(self, index: int) -> None:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("index must be an integer")
        if index < 0 or index > self.size:
            raise IndexError("linked-list insertion index out of range")

    def _node_at(self, index: int) -> Node[T]:
        self._validate_access_index(index)
        current = self.head
        for _ in range(index):
            current = current.next  # type: ignore[union-attr]
        return current  # type: ignore[return-value]

    def prepend(self, value: T) -> None:
        """Insert a value at the head."""
        node = Node(value, self.head)
        self.head = node
        if self.tail is None:
            self.tail = node
        self.size += 1

    def append(self, value: T) -> None:
        """Insert a value after the tail."""
        node = Node(value)
        if self.tail is None:
            self.head = node
        else:
            self.tail.next = node
        self.tail = node
        self.size += 1

    def insert(self, index: int, value: T) -> None:
        """Insert a value at a sequence index."""
        self._validate_insert_index(index)
        if index == 0:
            self.prepend(value)
        elif index == self.size:
            self.append(value)
        else:
            previous = self._node_at(index - 1)
            previous.next = Node(value, previous.next)
            self.size += 1

    def get(self, index: int) -> T:
        """Return the value at an index."""
        return self._node_at(index).value

    def set(self, index: int, value: T) -> None:
        """Replace the value at an index."""
        self._node_at(index).value = value

    def delete(self, index: int) -> T:
        """Delete and return the value at an index."""
        self._validate_access_index(index)
        if index == 0:
            removed = self.head
            self.head = removed.next  # type: ignore[union-attr]
            self.size -= 1
            if self.size == 0:
                self.tail = None
            return removed.value  # type: ignore[union-attr]

        previous = self._node_at(index - 1)
        removed = previous.next
        previous.next = removed.next  # type: ignore[union-attr]
        self.size -= 1
        if index == self.size:
            self.tail = previous
        return removed.value  # type: ignore[union-attr]

    def delete_value(self, value: T) -> bool:
        """Delete the first matching value and report whether it existed."""
        current = self.head
        previous: Node[T] | None = None
        while current is not None:
            if current.value == value:
                if previous is None:
                    self.head = current.next
                else:
                    previous.next = current.next
                if current is self.tail:
                    self.tail = previous
                self.size -= 1
                return True
            previous = current
            current = current.next
        return False

    def find(self, value: T) -> int:
        """Return the first matching index, or -1 when absent."""
        for index, item in enumerate(self):
            if item == value:
                return index
        return -1

    def traverse(self) -> list[T]:
        """Return all values in sequence order."""
        return list(self)

    def reverse(self) -> None:
        """Reverse successor references in linear time."""
        previous: Node[T] | None = None
        current = self.head
        self.tail = self.head
        while current is not None:
            following = current.next
            current.next = previous
            previous = current
            current = following
        self.head = previous

    def clear(self) -> None:
        """Remove every node."""
        self.head = None
        self.tail = None
        self.size = 0

    def __len__(self) -> int:
        return self.size

    def __iter__(self) -> Iterator[T]:
        current = self.head
        while current is not None:
            yield current.value
            current = current.next
