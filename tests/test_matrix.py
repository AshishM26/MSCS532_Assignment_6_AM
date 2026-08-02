"""Tests for Matrix."""

import unittest

from src.matrix import Matrix


class MatrixTests(unittest.TestCase):
    def test_construction_access_and_set(self) -> None:
        matrix = Matrix(2, 3, 0)
        self.assertEqual((2, 3), matrix.shape)
        matrix.set(1, 2, 9)
        self.assertEqual(9, matrix.get(1, 2))

    def test_from_rows_and_to_lists(self) -> None:
        matrix = Matrix.from_rows([[1, 2], [3, 4]])
        self.assertEqual([[1, 2], [3, 4]], matrix.to_lists())

    def test_rectangular_validation(self) -> None:
        with self.assertRaises(ValueError):
            Matrix.from_rows([])
        with self.assertRaises(ValueError):
            Matrix.from_rows([[1], [2, 3]])
        with self.assertRaises(TypeError):
            Matrix.from_rows([[1], "bad"])  # type: ignore[list-item]

    def test_insert_append_and_delete_rows(self) -> None:
        matrix = Matrix.from_rows([[1, 2], [5, 6]])
        matrix.insert_row(1, [3, 4])
        matrix.append_row([7, 8])
        self.assertEqual((4, 2), matrix.shape)
        self.assertEqual([3, 4], matrix.delete_row(1))
        self.assertEqual([[1, 2], [5, 6], [7, 8]], matrix.to_lists())

    def test_insert_append_and_delete_columns(self) -> None:
        matrix = Matrix.from_rows([[1, 3], [4, 6]])
        matrix.insert_column(1, [2, 5])
        matrix.append_column([7, 8])
        self.assertEqual((2, 4), matrix.shape)
        self.assertEqual([2, 5], matrix.delete_column(1))
        self.assertEqual([[1, 3, 7], [4, 6, 8]], matrix.to_lists())

    def test_row_and_column_returns_are_copy_safe(self) -> None:
        matrix = Matrix.from_rows([[1, 2], [3, 4]])
        row = matrix.row(0)
        column = matrix.column(1)
        row[0] = 99
        column[0] = 88
        self.assertEqual([[1, 2], [3, 4]], matrix.to_lists())

    def test_invalid_dimensions_and_indexes(self) -> None:
        for dimensions in ((0, 2), (2, 0), (-1, 2), (True, 2)):
            with self.subTest(dimensions=dimensions), self.assertRaises(ValueError):
                Matrix(*dimensions)
        matrix = Matrix(2, 2)
        with self.assertRaises(IndexError):
            matrix.get(2, 0)
        with self.assertRaises(IndexError):
            matrix.set(0, 2, 1)

    def test_mismatched_inserted_values(self) -> None:
        matrix = Matrix(2, 2)
        with self.assertRaises(ValueError):
            matrix.insert_row(0, [1])
        with self.assertRaises(ValueError):
            matrix.insert_column(0, [1])

    def test_matrix_retains_positive_dimensions(self) -> None:
        matrix = Matrix(1, 1)
        with self.assertRaises(ValueError):
            matrix.delete_row(0)
        with self.assertRaises(ValueError):
            matrix.delete_column(0)


if __name__ == "__main__":
    unittest.main()
