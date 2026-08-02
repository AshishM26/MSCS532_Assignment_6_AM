"""Tests for ArrayStack."""

import unittest

from src.array_stack import ArrayStack


class ArrayStackTests(unittest.TestCase):
    def test_empty_stack(self) -> None:
        stack: ArrayStack[int] = ArrayStack()
        self.assertTrue(stack.is_empty())
        self.assertEqual(0, stack.size())

    def test_push_peek_and_lifo_pop(self) -> None:
        stack: ArrayStack[str] = ArrayStack()
        for value in ["validate", "deploy", "monitor"]:
            stack.push(value)
        self.assertEqual("monitor", stack.peek())
        self.assertEqual(["monitor", "deploy", "validate"], [stack.pop(), stack.pop(), stack.pop()])
        self.assertTrue(stack.is_empty())

    def test_empty_errors(self) -> None:
        stack: ArrayStack[int] = ArrayStack()
        with self.assertRaises(IndexError):
            stack.pop()
        with self.assertRaises(IndexError):
            stack.peek()

    def test_clear_and_copy_safe_output(self) -> None:
        stack: ArrayStack[int] = ArrayStack()
        stack.push(1)
        stack.push(2)
        copied = stack.to_list()
        copied.append(3)
        self.assertEqual([1, 2], stack.to_list())
        stack.clear()
        self.assertTrue(stack.is_empty())

    def test_backing_array_resizes(self) -> None:
        stack: ArrayStack[int] = ArrayStack()
        for value in range(20):
            stack.push(value)
        self.assertEqual(20, stack.size())
        self.assertEqual(list(reversed(range(20))), [stack.pop() for _ in range(20)])


if __name__ == "__main__":
    unittest.main()
