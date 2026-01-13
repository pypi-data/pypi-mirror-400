"""LIKE statement"""

from typing import Any, NoReturn

from sqlfactory.condition.base import ConditionBase, StatementOrColumn
from sqlfactory.entities import Column
from sqlfactory.statement import Statement


class Like(ConditionBase):
    """
    SQL `LIKE` condition for comparing strings against pattern.

    Examples:

    - Simple
        ```python
        # `column` LIKE %s
        Like("column", "pattern")
        "`column` LIKE %s", ["pattern"]
        ```
    - Negative
        ```python
        # `column` NOT LIKE %s
        Like("column", "pattern", negative=True)
        "`column` NOT LIKE %s", ["pattern"]
        ```
    - Statement
        ```python
        Like("column", Concat("%", Column("other_column"), "%"))
        "`column` LIKE CONCAT(%s, `other_column`, %s)", ["%", "%"]
        ```
    - Statement (negative)
        ```python
        Like("column", Concat("%", Column("other_column"), "%"), negative=True)
        "`column` NOT LIKE CONCAT(%s, `other_column`, %s)", ["%", "%"]
        ```
    - Instead of column, you can also use any other expression
        ```python
        Like(Concat("column", "other_column"), "pattern")
        "CONCAT(`column`, `other_column`) LIKE %s", ["pattern"]
        ```
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement, negative: bool = False) -> None:
        """
        :param column: Column (or statement) on left side of LIKE operator.
        :param value: Value to match the column (or statement) against.
        :param negative: Whether to use negative matching (NOT LIKE).
        """

        super().__init__()

        if not isinstance(column, Statement):
            column = Column(column)

        self._column = column
        self._value = value
        self._negative = negative

    @staticmethod
    def escape(s: str) -> str:
        """
        Escape string for use in LIKE statement
        :param s: String to be escaped
        :return: String with escaped characters - % -> %%, _ -> __, to be safely used as part of pattern in LIKE statement.
        """
        return s.replace("%", "%%").replace("_", "__")

    def __str__(self) -> str:
        if isinstance(self._value, Statement):
            return f"{self._column!s}{' NOT' if self._negative else ''} LIKE {self._value!s}"

        return f"{self._column!s}{' NOT' if self._negative else ''} LIKE {self.dialect.placeholder}"

    @property
    def args(self) -> list[Any]:
        """Like statement arguments."""

        args = [*self._column.args]

        if isinstance(self._value, Statement):
            args.extend(self._value.args)
        else:
            args.append(self._value)

        return args

    def __bool__(self) -> bool:
        return True

    def __invert__(self) -> "Like":
        """
        Allows using the `~` operator to negate the LIKE condition, converting it to a NOT LIKE condition.
        Note: Cannot use ~ operator on NotLike conditions.
        """
        return NotLike(self._column, self._value)


class NotLike(Like):
    """
    SQL `NOT LIKE` condition for comparing strings against pattern.

    This is a dedicated class for NOT LIKE conditions, which is equivalent to using Like with negative=True.
    It provides a more intuitive API for NOT LIKE conditions.

    Examples:

    - Simple
        ```python
        # `column` NOT LIKE %s
        NotLike("column", "pattern")
        "`column` NOT LIKE %s", ["pattern"]
        ```
    - Statement
        ```python
        NotLike("column", Concat("%", Column("other_column"), "%"))
        "`column` NOT LIKE CONCAT(%s, `other_column`, %s)", ["%", "%"]
        ```
    - Instead of column, you can also use any other expression
        ```python
        NotLike(Concat("column", "other_column"), "pattern")
        "CONCAT(`column`, `other_column`) NOT LIKE %s", ["pattern"]
        ```
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement) -> None:
        """
        :param column: Column (or statement) on left side of NOT LIKE operator.
        :param value: Value to match the column (or statement) against.
        """
        super().__init__(column, value, negative=True)

    def __invert__(self) -> NoReturn:
        """
        Allows using the `~` operator to negate the LIKE condition, converting it to a NOT LIKE condition.
        Note: Cannot use ~ operator on NotLike conditions.
        """
        raise TypeError("Cannot use ~ operator on NotLike conditions")
