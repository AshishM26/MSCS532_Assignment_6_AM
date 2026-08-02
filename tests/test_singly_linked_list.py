"""Tests for SinglyLinkedList."""

import unittest

from src.singly_linked_list import SinglyLinkedList


class SinglyLinkedListTests(unittest.TestCase):
    def test_empty_list(self) -> None:
        values: SinglyLinkedList[int] = SinglyLinkedList()
        self.assertEqual(0, len(values))
        self.assertIsNone(values.head)
        self.assertIsNone(values.tail)

    def test_prepend_append_head_and_tail(self) -> None:
        values: SinglyLinkedList[int] = SinglyLinkedList()
        values.append(2)
        values.prepend(1)
        values.append(3)
        self.assertEqual([1, 2, 3], values.traverse())
        self.assertEqual(1, values.head.value)  # type: ignore[union-attr]
        self.assertEqual(3, values.tail.value)  # type: ignore[union-attr]
        self.assertEqual(3, values.size)

    def test_insert_beginning_middle_and_end(self) -> None:
        values: SinglyLinkedList[int] = SinglyLinkedList()
        values.insert(0, 2)
        values.insert(0, 1)
        values.insert(1, 9)
        values.insert(len(values), 3)
        self.assertEqual([1, 9, 2, 3], values.traverse())

    def test_delete_beginning_middle_and_end(self) -> None:
        values: SinglyLinkedList[int] = SinglyLinkedList()
        for value in [1, 2, 3, 4, 5]:
            values.append(value)
        self.assertEqual(1, values.delete(0))
        self.assertEqual(3, values.delete(1))
        self.assertEqual(5, values.delete(len(values) - 1))
        self.assertEqual([2, 4], values.traverse())
        self.assertEqual(4, values.tail.value)  # type: ignore[union-attr]

    def test_delete_only_element_resets_endpoints(self) -> None:
        values: SinglyLinkedList[int] = SinglyLinkedList()
        values.append(1)
        self.assertEqual(1, values.delete(0))
        self.assertIsNone(values.head)
        self.assertIsNone(values.tail)
        self.assertEqual(0, values.size)

    def test_delete_value_found_and_missing(self) -> None:
        values: SinglyLinkedList[str] = SinglyLinkedList()
        for value in ["a", "b", "c"]:
            values.append(value)
        self.assertTrue(values.delete_value("b"))
        self.assertFalse(values.delete_value("z"))
        self.assertTrue(values.delete_value("c"))
        self.assertEqual(["a"], values.traverse())
        self.assertEqual("a", values.tail.value)  # type: ignore[union-attr]

    def test_get_set_find_traverse_and_iteration(self) -> None:
        values: SinglyLinkedList[int] = SinglyLinkedList()
        for value in [4, 5, 6]:
            values.append(value)
        values.set(1, 9)
        self.assertEqual(9, values.get(1))
        self.assertEqual(2, values.find(6))
        self.assertEqual(-1, values.find(7))
        self.assertEqual([4, 9, 6], list(values))

    def test_reverse_empty_one_and_many(self) -> None:
        values: SinglyLinkedList[int] = SinglyLinkedList()
        values.reverse()
        values.append(1)
        values.reverse()
        self.assertEqual([1], values.traverse())
        values.append(2)
        values.append(3)
        values.reverse()
        self.assertEqual([3, 2, 1], values.traverse())
        self.assertEqual(3, values.head.value)  # type: ignore[union-attr]
        self.assertEqual(1, values.tail.value)  # type: ignore[union-attr]

    def test_invalid_indexes(self) -> None:
        values: SinglyLinkedList[int] = SinglyLinkedList()
        with self.assertRaises(IndexError):
            values.get(0)
        values.append(1)
        for index in (-1, 1):
            with self.subTest(index=index), self.assertRaises(IndexError):
                values.delete(index)
        with self.assertRaises(IndexError):
            values.insert(2, 3)

    def test_clear_resets_state(self) -> None:
        values: SinglyLinkedList[int] = SinglyLinkedList()
        values.append(1)
        values.append(2)
        values.clear()
        self.assertEqual([], values.traverse())
        self.assertIsNone(values.head)
        self.assertIsNone(values.tail)
        self.assertEqual(0, values.size)


if __name__ == "__main__":
    unittest.main()
