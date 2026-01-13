"""IN condition, used for checking whether column value is in given list of values."""

from __future__ import annotations

from collections.abc import Collection
from typing import TYPE_CHECKING, Any, NoReturn, cast, overload

from sqlfactory.condition.base import And, ConditionBase, Or, StatementOrColumn
from sqlfactory.condition.simple import Eq, Ne
from sqlfactory.entities import Column
from sqlfactory.statement import Raw, Statement

if TYPE_CHECKING:
    from sqlfactory.select.cte import With  # pragma: no cover
    from sqlfactory.select.select import Select  # pragma: no cover


class In(ConditionBase):
    """
    `IN` condition for checking whether column value is in given list of values.

    Supports both single-column and multi-column comparisons.

    In expects first argument to be column, and second argument to be list of values to compare against. So if you are
    passing strings, this is what happens. If you want to specify something else, you must be explicit. See examples.

    Examples:

    ### Single column

    - Simple IN statement:
        ```python
        # `column` IN (%s, %s, %s)
        In("column", [1, 2, 3])
        "`column` IN (%s, %s, %s)", [1, 2, 3]
        ```
    - Statement IN values
        ```python
        # <statement> IN (%s, %s, %s)
        In(Date("column"), ["2021-01-01", "2021-01-02", "2021-01-03"])
        "Date(`column`) IN (%s, %s, %s)", ["2021-01-01", "2021-01-02", "2021-01-03"]
        ```
    - Column IN columns
        ```python
        # Note the explicit `Column` usage.
        In("column", [Column("column1"), Column("column2"), Column("column3")])
        ```
    - Value with None works out-of-the-box
        ```python
        In("column", [1, None, 3])
        "`column` IN (%s, %s) OR `column` IS NULL", [1, 3]
        ```

    ### Multi column

    - Agains tuples of values:
        ```python
        # (`column1`, `column2`) IN ((%s, %s), (%s, %s), (%s, %s))
        In(("column1", "column2"), [(1, 2), (3, 4), (5, 6)])
        "(`column1`, `column2`) IN ((%s, %s), (%s, %s), (%s, %s))", [1, 2, 3, 4, 5, 6]
        ```
    - Mix of statement and column
        ```python
        # (<statement>, `column`) IN ((%s, %s), (%s, %s), (%s, %s))
        In((Date("column1"), "column2"), [("2021-01-01", 2), ("2021-01-02", 4), ("2021-01-03", 6)])
        "(DATE(`column1`), `column2`) IN ((%s, %s), (%s, %s), (%s, %s))", ["2021-01-01", 2, "2021-01-02", 4, "2021-01-03", 6]
        ```
    - Only statements
        ```python
        # (<statement>, <statement>) IN ((%s, %s), (%s, %s), (%s, %s))
        In((Min("column1"), Max("column1")), [(1, 2), (3, 4), (5, 6)])
        "(`column1`, `column2`) IN ((%s, %s), (%s, %s), (%s, %s))", [1, 2, 3, 4, 5, 6]
        ```
    - Agains other columns or statements
        ```python
        In(("column1", Max("column2")), [(Min("column1"), 2), (3, Sum("column3")), (5, 6)])
        "(`column1`, MAX(`column2`)) IN ((MIN(`column1`), %s), (%s, SUM(`column3`)), (%s, %s))", [2, 3, 5, 6]
        ```
    - Values with `None`:
        ```python
        In(("column1", "column2"), [(1, 2), (3, None), (5, 6)])
        "(`column1`, `column2`) IN ((%s, %s), (%s, %s)) OR (`column1` = %s AND `column2` IS NULL)", [1, 2, 3, 5, 6]


    ### Subquery IN

    ```python
    In("column", Select("column", table="table", where=Eq("column", 1)))
    ```

    ```python
    In(("column1", "column2"), Select("column1", "column2", table="table", where=Eq("column", 1)))
    ```
    """

    @overload
    def __init__(
        self, columns: tuple[StatementOrColumn, ...], values: Collection[tuple[Any, ...]], /, negative: bool = False
    ) -> None:
        """Provides type definition for statement (`column1`, `column2`) IN ((%s, %s), (%s, %s), (%s, %s))"""

    @overload
    def __init__(self, columns: tuple[StatementOrColumn, ...], values: Select | With, /, negative: bool = False) -> None:
        """Provides type definition for statement (`column1`, `column2`) IN (SELECT ...)"""

    @overload
    def __init__(self, column: StatementOrColumn, values: Collection[Any], /, negative: bool = False) -> None:
        """Provides type definition for statement `column` IN (%s, %s, %s)"""

    @overload
    def __init__(self, column: StatementOrColumn, values: Select | With, /, negative: bool = False) -> None:
        """Provides type definition for statement `column` IN (SELECT ...)"""

    def __init__(
        self,
        column: StatementOrColumn | tuple[StatementOrColumn, ...],
        values: Collection[Any | tuple[Any, ...]] | Select | With,
        /,
        negative: bool = False,
    ) -> None:
        """
        :param column: Column to compare, or tuple of columns for multi-column comparison.
        :param values: Values to compare (list of values, or list of tuples of values for multi-column In).
        :param negative: Whether to perform negative comparison (NOT IN)
        """
        super().__init__()

        self._is_multi_column = isinstance(column, tuple)
        self._column = column
        self._values = values
        self._negative = negative

    def __str__(self) -> str:
        from sqlfactory.select.cte import With  # pylint: disable=import-outside-toplevel
        from sqlfactory.select.select import Select  # pylint: disable=import-outside-toplevel

        if isinstance(self._values, (Select, With)):
            stmt, _ = self._build_subquery_in(self._column, self._values, negative=self._negative)

        elif self._is_multi_column:
            stmt, _ = self._build_multi_in(cast(tuple[StatementOrColumn], self._column), self._values, negative=self._negative)
        else:
            stmt, _ = self._build_simple_in(cast(StatementOrColumn, self._column), self._values, negative=self._negative)

        return stmt

    @property
    def args(self) -> list[Any]:
        from sqlfactory.select.cte import With  # pylint: disable=import-outside-toplevel
        from sqlfactory.select.select import Select  # pylint: disable=import-outside-toplevel

        if isinstance(self._values, (Select, With)):
            _, args = self._build_subquery_in(self._column, self._values, negative=self._negative)

        elif self._is_multi_column:
            _, args = self._build_multi_in(cast(tuple[StatementOrColumn], self._column), self._values, negative=self._negative)
        else:
            _, args = self._build_simple_in(cast(StatementOrColumn, self._column), self._values, negative=self._negative)

        return args

    @staticmethod
    def _build_subquery_in(
        columns: StatementOrColumn | tuple[StatementOrColumn, ...], select: Select | With, *, negative: bool = False
    ) -> tuple[str, list[Any]]:
        # pylint: disable=consider-using-f-string
        args = []

        if isinstance(columns, tuple):
            in_columns = [Column(col) if not isinstance(col, Statement) else col for col in columns]

            for column in in_columns:
                args.extend(column.args)

            args.extend(select.args)

            in_stmt = "({}) {} ({})".format(
                ", ".join(map(str, in_columns)),
                "IN" if not negative else "NOT IN",
                str(select),
            )

        else:
            if not isinstance(columns, Statement):
                columns = Column(columns)

            args = [*columns.args, *select.args]
            in_stmt = "{} {} ({})".format(
                str(columns),
                "IN" if not negative else "NOT IN",
                str(select),
            )

        return in_stmt, args

    def _build_simple_in(
        self, column: StatementOrColumn, values: Collection[Any], *, negative: bool = False
    ) -> tuple[str, list[Any]]:
        # pylint: disable=consider-using-f-string
        if not isinstance(column, Statement):
            column = Column(column)

        add_none = any(value is None for value in values)
        if add_none:
            values = [value for value in values if value is not None]

        args = []

        if values:
            in_stmt = "{} {} ({})".format(
                str(column),
                "IN" if not negative else "NOT IN",
                ", ".join([self.dialect.placeholder if not isinstance(value, Statement) else str(value) for value in values]),
            )

            if isinstance(column, Statement):
                args.extend(column.args)

            for value in values:
                if isinstance(value, Statement):
                    args.extend(value.args)
                elif not isinstance(value, Statement):
                    args.append(value)

            if add_none:
                if isinstance(column, Statement):
                    args.extend(column.args)

                return (f"({in_stmt} {'OR' if not negative else 'AND'} {column!s} IS {'NOT ' if negative else ''}NULL)", args)

            return (in_stmt, args)

        if add_none:
            # This could happen only if there is just a one column, not multi-column statement.
            if isinstance(column, Statement):
                args.extend(column.args)

            return (f"{column!s} IS {'NOT ' if negative else ''}NULL", args)

        return "FALSE" if not negative else "TRUE", []

    def _build_multi_in(
        self, column: tuple[StatementOrColumn, ...], values: Collection[tuple[Any, ...]], *, negative: bool = False
    ) -> tuple[str, list[Any]]:
        # pylint: disable=consider-using-f-string
        column = tuple(Column(col) if not isinstance(col, Statement) else col for col in column)

        none_multi_values = [value_tuple for value_tuple in values if any(value is None for value in value_tuple)]
        values = [value_tuple for value_tuple in values if all(value is not None for value in value_tuple)]

        args = []

        for stmt in column:
            if isinstance(stmt, Statement):
                args.extend(stmt.args)

        for value_tuple in values:
            for value in value_tuple:
                if not isinstance(value, Statement):
                    args.append(value)
                elif isinstance(value, Statement):
                    args.extend(value.args)

        multi_in_stmt = "({}) {} ({})".format(
            ", ".join(map(str, column)),
            "IN" if not negative else "NOT IN",
            ", ".join(
                [
                    "("
                    + ", ".join(
                        [self.dialect.placeholder if not isinstance(value, Statement) else str(value) for value in value_tuple]
                    )
                    + ")"
                    for value_tuple in values
                ]
            ),
        )

        if not values and not none_multi_values:
            return "FALSE" if not negative else "TRUE", []

        if not none_multi_values:
            return (
                multi_in_stmt,
                args,
            )

        or_stmt = (Or if not negative else And)()

        if values:
            or_stmt.append(Raw(multi_in_stmt, *args))

        for value_tuple in none_multi_values:
            or_stmt.append(And(*[(Eq if not negative else Ne)(col, value) for col, value in zip(column, value_tuple)]))

        return (str(or_stmt), or_stmt.args)

    def __bool__(self) -> bool:
        return True

    def __invert__(self) -> "In":
        """
        Allows using the `~` operator to negate the IN condition, converting it to a NOT IN condition.
        Note: Cannot use ~ operator on NotIn conditions.
        """
        return NotIn(self._column, self._values)


class NotIn(In):
    """
    `NOT IN` condition for checking whether column value is not in given list of values.

    This is a dedicated class for NOT IN conditions, which is equivalent to using In with negative=True.
    It provides a more intuitive API for NOT IN conditions.

    Examples:

    ### Single column

    - Simple NOT IN statement:
        ```python
        # `column` NOT IN (%s, %s, %s)
        NotIn("column", [1, 2, 3])
        "`column` NOT IN (%s, %s, %s)", [1, 2, 3]
        ```
    - Statement NOT IN values
        ```python
        # <statement> NOT IN (%s, %s, %s)
        NotIn(Date("column"), ["2021-01-01", "2021-01-02", "2021-01-03"])
        "Date(`column`) NOT IN (%s, %s, %s)", ["2021-01-01", "2021-01-02", "2021-01-03"]
        ```
    - Value with None works out-of-the-box
        ```python
        NotIn("column", [1, None, 3])
        "`column` NOT IN (%s, %s) AND `column` IS NOT NULL", [1, 3]
        ```

    ### Multi column

    - Against tuples of values:
        ```python
        # (`column1`, `column2`) NOT IN ((%s, %s), (%s, %s), (%s, %s))
        NotIn(("column1", "column2"), [(1, 2), (3, 4), (5, 6)])
        "(`column1`, `column2`) NOT IN ((%s, %s), (%s, %s), (%s, %s))", [1, 2, 3, 4, 5, 6]
        ```
    - Values with `None`:
        ```python
        NotIn(("column1", "column2"), [(1, 2), (3, None), (5, 6)])
        "(`column1`, `column2`) NOT IN ((%s, %s), (%s, %s)) AND NOT (`column1` = %s AND `column2` IS NULL)", [1, 2, 3, 5, 6]
        ```

    ### Subquery NOT IN

    ```python
    NotIn("column", Select("column", table="table", where=Eq("column", 1)))
    ```

    ```python
    NotIn(("column1", "column2"), Select("column1", "column2", table="table", where=Eq("column", 1)))
    ```
    """

    @overload
    def __init__(self, columns: tuple[StatementOrColumn, ...], values: Collection[tuple[Any, ...]], /) -> None:
        """Provides type definition for statement (`column1`, `column2`) NOT IN ((%s, %s), (%s, %s), (%s, %s))"""

    @overload
    def __init__(self, columns: tuple[StatementOrColumn, ...], values: Select | With, /) -> None:
        """Provides type definition for statement (`column1`, `column2`) NOT IN (SELECT ...)"""

    @overload
    def __init__(self, column: StatementOrColumn, values: Collection[Any], /) -> None:
        """Provides type definition for statement `column` NOT IN (%s, %s, %s)"""

    @overload
    def __init__(self, column: StatementOrColumn, values: Select | With, /) -> None:
        """Provides type definition for statement `column` NOT IN (SELECT ...)"""

    def __init__(
        self,
        column: StatementOrColumn | tuple[StatementOrColumn, ...],
        values: Collection[Any | tuple[Any, ...]] | Select | With,
        /,
    ) -> None:
        """
        :param column: Column to compare, or tuple of columns for multi-column comparison.
        :param values: Values to compare (list of values, or list of tuples of values for multi-column Not_In).
        """
        super().__init__(column, values, negative=True)

    def __invert__(self) -> NoReturn:
        """
        Allows using the `~` operator to negate the NOT IN condition, converting it to an IN condition.
        Note: Cannot use ~ operator on NotIn conditions.
        """
        raise TypeError("Cannot use ~ operator on NotIn conditions")
