"""Tests for CircularQueue."""

import unittest

from src.circular_queue import CircularQueue


class CircularQueueTests(unittest.TestCase):
    def test_empty_queue(self) -> None:
        queue: CircularQueue[int] = CircularQueue()
        self.assertTrue(queue.is_empty())
        self.assertEqual(0, queue.size())

    def test_enqueue_peek_and_fifo_order(self) -> None:
        queue: CircularQueue[str] = CircularQueue()
        for value in ["job-a", "job-b", "job-c"]:
            queue.enqueue(value)
        self.assertEqual("job-a", queue.peek())
        self.assertEqual(["job-a", "job-b", "job-c"], [queue.dequeue(), queue.dequeue(), queue.dequeue()])

    def test_wrap_around_preserves_order(self) -> None:
        queue: CircularQueue[int] = CircularQueue(4)
        for value in range(4):
            queue.enqueue(value)
        self.assertEqual(0, queue.dequeue())
        self.assertEqual(1, queue.dequeue())
        queue.enqueue(4)
        queue.enqueue(5)
        self.assertEqual([2, 3, 4, 5], queue.to_list())

    def test_resize_after_wrap_around(self) -> None:
        queue: CircularQueue[int] = CircularQueue(3)
        for value in [1, 2, 3]:
            queue.enqueue(value)
        queue.dequeue()
        queue.enqueue(4)
        queue.enqueue(5)
        self.assertGreaterEqual(queue.capacity, 5)
        self.assertEqual([2, 3, 4, 5], queue.to_list())

    def test_empty_errors(self) -> None:
        queue: CircularQueue[int] = CircularQueue()
        with self.assertRaises(IndexError):
            queue.dequeue()
        with self.assertRaises(IndexError):
            queue.peek()

    def test_dequeue_to_empty_and_reuse(self) -> None:
        queue: CircularQueue[int] = CircularQueue()
        queue.enqueue(1)
        self.assertEqual(1, queue.dequeue())
        queue.enqueue(2)
        self.assertEqual(2, queue.peek())

    def test_clear_and_copy_safe_output(self) -> None:
        queue: CircularQueue[int] = CircularQueue(2)
        queue.enqueue(1)
        queue.enqueue(2)
        copied = queue.to_list()
        copied.append(3)
        self.assertEqual([1, 2], queue.to_list())
        queue.clear()
        self.assertEqual(2, queue.capacity)
        self.assertTrue(queue.is_empty())

    def test_invalid_capacity(self) -> None:
        for capacity in (0, -1, True):
            with self.subTest(capacity=capacity), self.assertRaises(ValueError):
                CircularQueue(capacity)


if __name__ == "__main__":
    unittest.main()
