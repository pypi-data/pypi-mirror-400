"""RLIKE statement"""

from typing import Any, NoReturn

from sqlfactory.condition.base import StatementOrColumn
from sqlfactory.condition.like import Like
from sqlfactory.statement import Statement


class RLike(Like):
    """
    SQL `RLIKE` condition performs a pattern match of a string expression against a pattern.

    Examples:

    - Simple
        ```python
        # `column` RLIKE %s
        RLike("column", "pattern")
        "`column` RLIKE %s", ["pattern"]
        ```
    - Negative
        ```python
        # `column` NOT RLIKE %s
        RLike("column", "pattern", negative=True)
        "`column` NOT RLIKE %s", ["pattern"]
        ```
    - Statement
        ```python
        RLike("column", Concat(".*", Column("other_column"), ".*"))
        "`column` RLIKE CONCAT(%s, `other_column`, %s)", [".*", ".*"]
        ```
    - Statement (negative)
        ```python
        RLike("column", Concat(".*", Column("other_column"), ".*"), negative=True)
        "`column` NOT RLIKE CONCAT(%s, `other_column`, %s)", [".*", ".*"]
        ```
    - Instead of column, you can also use any other expression
        ```python
        RLike(Concat("column", "other_column"), "pattern")
        "CONCAT(`column`, `other_column`) RLIKE %s", ["pattern"]
        ```
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement, negative: bool = False) -> None:
        """
        :param column: Column (or statement) on left side of RLIKE operator.
        :param value: Value to match the column (or statement) against.
        :param negative: Whether to use negative matching (NOT RLIKE).
        """
        # we want change init comment to be more specific
        # pylint: disable=useless-parent-delegation
        super().__init__(column, value, negative)

    def __str__(self) -> str:
        if isinstance(self._value, Statement):
            return f"{self._column!s}{' NOT' if self._negative else ''} RLIKE {self._value!s}"

        return f"{self._column!s}{' NOT' if self._negative else ''} RLIKE {self.dialect.placeholder}"

    def __invert__(self) -> "RLike":
        """
        Allows using the `~` operator to negate the RLIKE condition, converting it to a NOT RLIKE condition.
        Note: Cannot use ~ operator on NotRLike conditions.
        """
        return NotRLike(self._column, self._value)


class NotRLike(RLike):
    """
    SQL `NOT RLIKE` condition performs a pattern match of a string expression against a pattern.

    This is a dedicated class for NOT RLIKE conditions, which is equivalent to using RLike with negative=True.
    It provides a more intuitive API for NOT RLIKE conditions.

    Examples:

    - Simple
        ```python
        # `column` NOT RLIKE %s
        NotRLike("column", "pattern")
        "`column` NOT RLIKE %s", ["pattern"]
        ```
    - Statement
        ```python
        NotRLike("column", Concat("%", Column("other_column"), "%"))
        "`column` NOT RLIKE CONCAT(%s, `other_column`, %s)", ["%", "%"]
        ```
    - Instead of column, you can also use any other expression
        ```python
        NotRLike(Concat("column", "other_column"), "pattern")
        "CONCAT(`column`, `other_column`) NOT RLIKE %s", ["pattern"]
        ```
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement) -> None:
        """
        :param column: Column (or statement) on left side of NOT RLIKE operator.
        :param value: Value to match the column (or statement) against.
        """
        super().__init__(column, value, negative=True)

    def __invert__(self) -> NoReturn:
        """
        Allows using the `~` operator to negate the RLIKE condition, converting it to a NOT RLIKE condition.
        Note: Cannot use ~ operator on NotRLike conditions.
        """
        raise TypeError("Cannot use ~ operator on NotRLike conditions")
