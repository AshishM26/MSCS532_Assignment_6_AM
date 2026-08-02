"""A rectangular matrix backed by nested DynamicArray instances."""

from typing import TypeVar

from src.dynamic_array import DynamicArray

T = TypeVar("T")


class Matrix:
    """Maintain a positive rectangular grid with row and column operations."""

    def __init__(self, rows: int, columns: int, default: object = None) -> None:
        self._validate_dimension(rows, "rows")
        self._validate_dimension(columns, "columns")
        self._rows = rows
        self._columns = columns
        self._data: DynamicArray[DynamicArray[object]] = DynamicArray()
        for _ in range(rows):
            row = DynamicArray[object]()
            for _ in range(columns):
                row.append(default)
            self._data.append(row)

    @staticmethod
    def _validate_dimension(value: int, name: str) -> None:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{name} must be a positive integer")

    @classmethod
    def from_rows(cls, rows: list[list[object]]) -> "Matrix":
        """Construct a matrix from a nonempty rectangular list of rows."""
        if not isinstance(rows, list) or not rows:
            raise ValueError("rows must be a nonempty list")
        if any(not isinstance(row, list) for row in rows):
            raise TypeError("each row must be a list")
        width = len(rows[0])
        if width == 0 or any(len(row) != width for row in rows):
            raise ValueError("rows must form a nonempty rectangular matrix")
        matrix = cls(len(rows), width)
        for row_index, row in enumerate(rows):
            for column_index, value in enumerate(row):
                matrix.set(row_index, column_index, value)
        return matrix

    @property
    def shape(self) -> tuple[int, int]:
        """Return ``(rows, columns)``."""
        return self._rows, self._columns

    def _validate_row(self, index: int) -> None:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("row index must be an integer")
        if index < 0 or index >= self._rows:
            raise IndexError("row index out of range")

    def _validate_column(self, index: int) -> None:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("column index must be an integer")
        if index < 0 or index >= self._columns:
            raise IndexError("column index out of range")

    def _validate_row_insert(self, index: int) -> None:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("row index must be an integer")
        if index < 0 or index > self._rows:
            raise IndexError("row insertion index out of range")

    def _validate_column_insert(self, index: int) -> None:
        if isinstance(index, bool) or not isinstance(index, int):
            raise TypeError("column index must be an integer")
        if index < 0 or index > self._columns:
            raise IndexError("column insertion index out of range")

    def get(self, row: int, column: int) -> object:
        """Return one cell value."""
        self._validate_row(row)
        self._validate_column(column)
        return self._data[row][column]

    def set(self, row: int, column: int, value: object) -> None:
        """Replace one cell value."""
        self._validate_row(row)
        self._validate_column(column)
        self._data[row][column] = value

    def insert_row(self, index: int, values: list[object]) -> None:
        """Insert a complete row while preserving rectangular shape."""
        self._validate_row_insert(index)
        if not isinstance(values, list) or len(values) != self._columns:
            raise ValueError("inserted row length must match the column count")
        row = DynamicArray[object]()
        for value in values:
            row.append(value)
        self._data.insert(index, row)
        self._rows += 1

    def append_row(self, values: list[object]) -> None:
        """Append a complete row."""
        self.insert_row(self._rows, values)

    def delete_row(self, index: int) -> list[object]:
        """Delete and return a row; a matrix retains at least one row."""
        self._validate_row(index)
        if self._rows == 1:
            raise ValueError("a matrix must retain at least one row")
        removed = self._data.delete(index).to_list()
        self._rows -= 1
        return removed

    def insert_column(self, index: int, values: list[object]) -> None:
        """Insert a column while preserving rectangular shape."""
        self._validate_column_insert(index)
        if not isinstance(values, list) or len(values) != self._rows:
            raise ValueError("inserted column length must match the row count")
        for row_index, value in enumerate(values):
            self._data[row_index].insert(index, value)
        self._columns += 1

    def append_column(self, values: list[object]) -> None:
        """Append a complete column."""
        self.insert_column(self._columns, values)

    def delete_column(self, index: int) -> list[object]:
        """Delete and return a column; a matrix retains at least one column."""
        self._validate_column(index)
        if self._columns == 1:
            raise ValueError("a matrix must retain at least one column")
        removed = [self._data[row].delete(index) for row in range(self._rows)]
        self._columns -= 1
        return removed

    def row(self, index: int) -> list[object]:
        """Return a copy of one row."""
        self._validate_row(index)
        return self._data[index].to_list()

    def column(self, index: int) -> list[object]:
        """Return a copy of one column."""
        self._validate_column(index)
        return [self._data[row][index] for row in range(self._rows)]

    def to_lists(self) -> list[list[object]]:
        """Return a deep-enough copy of the matrix rows."""
        return [self._data[row].to_list() for row in range(self._rows)]
