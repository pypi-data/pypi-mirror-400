"""INSERT statement builder."""

from __future__ import annotations

from collections.abc import Collection
from typing import Any, Self, TypeAlias

from sqlfactory.dialect import SQLDialect
from sqlfactory.entities import Column, ColumnArg, Table
from sqlfactory.execute import ConditionalExecutableStatement
from sqlfactory.insert.values import Values
from sqlfactory.select import Select
from sqlfactory.statement import Statement


class Insert(ConditionalExecutableStatement):
    # pylint: disable=too-many-instance-attributes

    """
    INSERT statement

    Statement is conditional, which means it won't be executed if no rows would be inserted (which throws SQL error).

    >>> Insert.into("table")("column1", "column2", "column3").values((1, 2, 3), (4, 5, 6))
    >>> "INSERT INTO `table` (`column1`, `column2`, `column3`) VALUES (1, 2, 3), (4, 5, 6)"

    >>> Insert("table", ignore=True)("column1", "column2", "column3").values((1, 2, 3), (4, 5, 6))
    >>> "INSERT IGNORE INTO `table` (`column1`, `column2`, `column3`) VALUES (1, 2, 3), (4, 5, 6)"

    There is also INSERT ... SELECT syntax support:

    >>> Insert("table")("column1", "column2").select(Select("a", "b", table="table2"))
    >>> "INSERT INTO `table` (`column1`, `column2`) SELECT `a`, `b` FROM `table2`"
    """

    def __init__(
        self,
        table: Table | str,
        ignore: bool = False,
        replace: bool = False,
        *,
        dialect: SQLDialect | None = None,
    ) -> None:
        """
        :param table: Table to insert into
        :param ignore: use INSERT IGNORE?
        :param replace: use REPLACE?
        """

        super().__init__(dialect=dialect)

        if ignore and replace:
            raise AttributeError("Only one of ignore or replace can be specified.")

        self._ignore = ignore
        self._replace = replace

        self._table = table if isinstance(table, Table) else Table(table)
        self._columns: list[Column] = []
        self._values: list[Collection[Any]] = []
        self._select: Select | None = None
        self._on_duplicate_key_update_set: list[tuple[Column, str]] = []
        self._on_duplicate_key_update_args: list[Any] = []

    @classmethod
    def into(cls, table: Table | str, *, ignore: bool = False, replace: bool = False) -> Self:
        """
        Specify table to insert into. Supplies passing arguments to the constructor, to provide better compatibility with
        plain SQL syntax.
        """
        return cls(table, ignore=ignore, replace=replace)

    # pylint: disable=invalid-name
    @classmethod
    def INTO(cls, table: Table | str, *, ignore: bool = False, replace: bool = False) -> Self:
        """Alias for `Insert.into()` to provide better SQL compatibility by using all caps."""
        return cls.into(table, ignore=ignore, replace=replace)

    def __call__(self, *columns: ColumnArg) -> Self:
        """
        Specify columns to be inserted. Columns can be specified as strings or Column objects.
        :param columns: Columns to insert.
        """
        if not columns:
            raise AttributeError("At least one column must be specified.")

        if self._columns:
            raise AttributeError("Insert columns has already been specified.")

        for column in columns:
            if not isinstance(column, (Column, str)):
                raise AttributeError("Statements cannot be used as INSERT columns.")

        self._columns = [column if isinstance(column, Column) else Column(column) for column in columns]
        return self

    def columns(self, *columns: ColumnArg) -> Self:
        """
        Alias for `Insert.__call__()`.
        """
        self(*columns)
        return self

    def values(self, *rows: Collection[Any]) -> Self:
        """
        Specify values to insert. Each row should be one collection. The semantics is identical to the SQL syntax.

        >>> Insert.into("table")("a", "b").values(
        ...    ("row 1, column a", "row 1, column b"),
        ...    ("row 2, column a", "row 2, column b")
        ... )

        Beware of common error of omitting the inner collection for single row inserts.
        """
        if self._select is not None:
            raise AttributeError("Unable to mix values() and select() in one insert statement.")

        self._values.extend(rows)
        return self

    # pylint: disable=invalid-name
    def VALUES(self, *rows: Collection[Any]) -> Self:
        """Alias for `Insert.values()` to provide better SQL compatibility by using all caps."""
        return self.values(*rows)

    def select(self, select: Select) -> Self:
        """
        Specify SELECT statement to insert from.

        >>> Insert.into("table")("a", "b").select(Select(
        ...    "a", "b", table="table2", where=Gt("a", 1)
        ... ))
        """

        if self._values:
            raise AttributeError("Unable to mix values() and select() in one insert statement.")

        self._select = select

        return self

    def SELECT(self, select: Select) -> Self:
        """Alias for select() to provide better SQL compatibility using all caps."""
        return self.select(select)

    def on_duplicate_key_update(self, **kwargs: Values | Statement | Any) -> Self:
        """
        MySQL / MariaDB specific. Specify columns to update if row already exists (duplicate key check is triggered).

        Specify individual columns to be updated as keyword arguments.

        You can use Values() function to access value from currently inserted row's values, e.g.:

        >>> Insert.into("table")("a", "b").values(
        >>>     (1, 2),
        >>>     (3, 4)
        >>> ).on_duplicate_key_update(
        >>>     a=Values("a"),          # Set column "a" to the value of column "a" from the row being inserted
        >>>     b=Column("b") + 1       # Increment value of column "b" by 1 each time the duplicate is detected.
        >>> )
        """
        for column, stmt in kwargs.items():
            column_stmt = Column(column)

            self._on_duplicate_key_update_set.append((column_stmt, str(stmt) if isinstance(stmt, Statement) else "%s"))
            if isinstance(stmt, Statement):
                self._on_duplicate_key_update_args.extend(stmt.args)
            elif not isinstance(stmt, Statement):
                self._on_duplicate_key_update_args.append(stmt)

        return self

    # pylint: disable=invalid-name
    def ON_DUPLICATE_KEY_UPDATE(self, **kwargs: Values | Statement | Any) -> Self:
        """Alias for `Insert.on_duplicate_key_update()` to provide better SQL compatibility by using all caps."""
        return self.on_duplicate_key_update(**kwargs)

    def __bool__(self) -> bool:
        """Checks whether there are any rows to insert. Usage for conditional execution of the statement."""
        return (bool(self._values) and self._select is None) or (self._select is not None and bool(self._select))

    def __str__(self) -> str:
        """Constructs INSERT statement from provided data."""

        with self.dialect:
            if not self._columns:
                raise AttributeError("At least one column must be specified.")

            if self._replace:
                q = [f"REPLACE INTO {self._table!s}"]
            else:
                q = [f"INSERT{' IGNORE' if self._ignore else ''} INTO {self._table!s}"]

            if self._columns:
                q.append(f"({', '.join(map(str, self._columns))})")

            if self._values:
                q.append("VALUES")

                count_columns = len(self._columns)

                for idx, row in enumerate(self._values):
                    row_placeholders = []

                    if len(row) != count_columns:
                        raise AttributeError(f"Row {idx} has different number of values than specified number of columns.")

                    for value in row:
                        if isinstance(value, Statement):
                            row_placeholders.append(str(value))
                        else:
                            row_placeholders.append(self.dialect.placeholder)

                    q.append(f"({', '.join(row_placeholders)}){',' if idx < len(self._values) - 1 else ''}")
            elif self._select:
                q.append(str(self._select))

            if self._on_duplicate_key_update_set:
                q.append("ON DUPLICATE KEY UPDATE")
                q.append(", ".join([f"{update_set[0]!s} = {update_set[1]}" for update_set in self._on_duplicate_key_update_set]))

            return " ".join(q)

    @property
    def args(self) -> list[Any]:
        """Argument values for the statement."""
        out = []

        if self._select:
            out.extend(self._select.args)
        else:
            for row in self._values:
                for v in row:
                    if isinstance(v, Statement):
                        out.extend(v.args)
                    elif not isinstance(v, Statement):
                        out.append(v)

        out.extend(self._on_duplicate_key_update_args)

        return out


# Alias for Insert, for better SQL compatibility
INSERT: TypeAlias = Insert  # pylint: disable=invalid-name
"""
Alias for `Insert` statement to provide better SQL compatibility, as SQL is often written in all caps.
"""
