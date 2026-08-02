"""Tests for DynamicArray."""

import unittest

from src.dynamic_array import DynamicArray


class DynamicArrayTests(unittest.TestCase):
    def test_empty_initialization(self) -> None:
        values: DynamicArray[int] = DynamicArray()
        self.assertEqual(0, len(values))
        self.assertEqual([], values.to_list())

    def test_append_and_growth(self) -> None:
        values: DynamicArray[int] = DynamicArray(2)
        for value in range(5):
            values.append(value)
        self.assertEqual([0, 1, 2, 3, 4], values.to_list())
        self.assertGreaterEqual(values.capacity, 5)

    def test_get_set_and_dunder_access(self) -> None:
        values: DynamicArray[str] = DynamicArray()
        values.append("network")
        values.append("compute")
        values.set(1, "storage")
        values[0] = "gateway"
        self.assertEqual("gateway", values.get(0))
        self.assertEqual("storage", values[1])

    def test_insert_beginning_middle_and_end(self) -> None:
        values: DynamicArray[int] = DynamicArray()
        values.append(2)
        values.insert(0, 1)
        values.insert(1, 9)
        values.insert(len(values), 3)
        self.assertEqual([1, 9, 2, 3], values.to_list())

    def test_delete_beginning_middle_and_end(self) -> None:
        values: DynamicArray[int] = DynamicArray()
        for value in [1, 2, 3, 4, 5]:
            values.append(value)
        self.assertEqual(1, values.delete(0))
        self.assertEqual(3, values.delete(1))
        self.assertEqual(5, values.delete(len(values) - 1))
        self.assertEqual([2, 4], values.to_list())

    def test_pop_default_and_indexed(self) -> None:
        values: DynamicArray[int] = DynamicArray()
        for value in [1, 2, 3]:
            values.append(value)
        self.assertEqual(3, values.pop())
        self.assertEqual(1, values.pop(0))
        self.assertEqual([2], values.to_list())

    def test_empty_pop_and_invalid_indexes(self) -> None:
        values: DynamicArray[int] = DynamicArray()
        with self.assertRaises(IndexError):
            values.pop()
        values.append(1)
        for index in (-1, 1):
            with self.subTest(index=index), self.assertRaises(IndexError):
                values.get(index)
        with self.assertRaises(IndexError):
            values.insert(2, 3)

    def test_iteration_search_and_contains(self) -> None:
        values: DynamicArray[str] = DynamicArray()
        for value in ["a", "b", "c"]:
            values.append(value)
        self.assertEqual(["a", "b", "c"], list(values))
        self.assertTrue(values.contains("b"))
        self.assertFalse(values.contains("z"))
        self.assertEqual(1, values.index_of("b"))
        self.assertEqual(-1, values.index_of("z"))

    def test_clear_and_capacity_floor(self) -> None:
        values: DynamicArray[int] = DynamicArray(2)
        for value in range(16):
            values.append(value)
        for _ in range(14):
            values.pop()
        self.assertGreaterEqual(values.capacity, 2)
        values.clear()
        self.assertEqual(2, values.capacity)
        self.assertEqual([], values.to_list())

    def test_invalid_initial_capacity(self) -> None:
        for capacity in (0, -1, True, 2.5):
            with self.subTest(capacity=capacity), self.assertRaises(ValueError):
                DynamicArray(capacity)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
