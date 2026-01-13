# noqa: A005

"""SELECT statement builder."""

from __future__ import annotations

from collections.abc import Collection
from functools import reduce
from typing import Any, Self, TypeAlias, cast

from sqlfactory.condition.base import And, ConditionBase
from sqlfactory.dialect import SQLDialect
from sqlfactory.entities import Column, ColumnArg, Table
from sqlfactory.execute import ExecutableStatement
from sqlfactory.mixins.join import WithJoin
from sqlfactory.mixins.limit import Limit, WithLimit
from sqlfactory.mixins.order import OrderArg, WithOrder
from sqlfactory.mixins.where import WithWhere
from sqlfactory.select.column_list import ColumnList
from sqlfactory.select.join import Join
from sqlfactory.statement import Statement


class Select(ExecutableStatement, WithWhere, WithOrder, WithLimit, WithJoin):
    # pylint: disable=too-many-arguments  # Yes, SELECT is complex.
    """
    `SELECT` statement to create complex select queries.

    Example:

    >>> from sqlfactory import Eq
    >>> cursor: Cursor = ...
    >>>
    >>> (
    ...     Select("column1", "column2", "column3", table="table_name")
    ...     .where(Eq("column1", 1))
    ...     .order_by("column2")
    ...     .limit(2, 10)
    ...     .execute(cursor)
    ... )

    **Note:** `Eq()` and all other condition functions are expecting first argument to be column and second argument to be value.
    If you want to have column on the right side or value on the left, you must explicitely use `Column()` function. And if you
    want literal value on the left side, you must explicitely use `Value()` function.

    Subqueries are also supported:

    >>> from sqlfactory import Select, Aliased
    >>> from sqlfactory.func.agg import Sum
    >>>
    >>> Select(
    ...     "t1.id", "t2.price",
    ...     table=[
    ...         "t1",
    ...         Aliased(Select(Aliased(Sum("price"), alias="price"), table="product_prices"), alias="t2")
    ...     ]
    ... )

    Known limitations:
    - JOINs are not checked for uniqueness, so it is possible to add same JOIN multiple times. For now, it is up to
      user to ensure that JOINs are unique. This may be changed in the future, but it is not simple task, as joins
      needs to be in certain order.
    """

    def __init__(
        self,
        *columns: Statement | ColumnArg,
        select: ColumnList | list[str] | None = None,
        table: Table | str | Statement | Collection[Table | str | Statement] | None = None,
        join: Collection[Join] | None = None,
        where: ConditionBase | None = None,
        group_by: ColumnList | Collection[Statement | ColumnArg] | None = None,
        having: ConditionBase | None = None,
        order: OrderArg | None = None,
        limit: Limit | None = None,
        for_update: bool = False,
        dialect: SQLDialect | None = None,
    ) -> None:
        """
        :param columns: Columns to select.
        :param select: Columns to select as instance of ColumnList instead of specifying positional arguments.
        :param table: Table to select from.
        :param join: Join statements
        :param where: Where condition
        :param group_by: Group by columns
        :param having: Having condition
        :param order: Order by columns
        :param limit: Limit results
        :param for_update: Lock rows for update
        """
        super().__init__(where=where, order=order, limit=limit, join=join, dialect=dialect)

        if columns and select:
            raise AttributeError("Cannot specify individual columns when attribute select is present.")

        if select and not isinstance(select, ColumnList):
            select = ColumnList(select)

        self.columns: ColumnList = cast(ColumnList | None, select) or ColumnList(columns)
        """Columns to select."""

        if (table is not None and not isinstance(table, Collection)) or isinstance(table, str):
            table = [table]

        self.table: list[Statement] = [Table(t) if isinstance(t, str) else t for t in table] if table is not None else []
        """Table (or tables) to select from."""

        self._group_by = ColumnList(group_by) if group_by is not None and not isinstance(group_by, ColumnList) else group_by
        self._having = having
        self._for_update = for_update

    def add(self, column: Statement | Any) -> Self:
        """Add new statement or column to the set of selected columns"""
        self.columns.add(column)
        return self

    def group_by(self, column: Statement | ColumnArg, *columns: Statement | ColumnArg) -> Self:
        """
        `GROUP BY` clause.

        >>> Select().group_by("column1", "column2", "column3")
        >>> "SELECT ... GROUP BY `column1`, `column2`, `column3`"

        **Note:** When calling `Select.group_by()` multiple times, it will join the grouped columns together.
        """
        if self._group_by is not None:
            self._group_by.append(column)

            if columns:
                self._group_by.extend([Column(column) if not isinstance(column, Statement) else column for column in columns])

        else:
            self._group_by = ColumnList([column, *list(columns)])

        return self

    # pylint: disable=invalid-name
    def GROUP_BY(self, column: Statement | ColumnArg, *columns: Statement | ColumnArg) -> Self:
        """Alias for `Select.group_by()` to be more SQL-like with all capitals."""
        return self.group_by(column, *columns)

    def having(self, condition: ConditionBase) -> Self:
        """
        `HAVING` clause

        >>> Select().having(Eq("column1", 3))
        >>> "SELECT ... HAVING `column1` = %s", [3]
        """
        if self._having is not None:
            if isinstance(self._having, And):
                self._having.append(condition)
            else:
                self._having = And(self._having, condition)
        else:
            self._having = condition

        return self

    # pylint: disable=invalid-name
    def HAVING(self, condition: ConditionBase) -> Self:
        """Alias for `Select.having()` to be more SQL-like with all capitals."""
        return self.having(condition)

    def __str__(self) -> str:
        with self.dialect:
            if not self.columns and not self.table:
                return ""

            out: list[str] = ["SELECT", str(self.columns) if self.columns else "*"]

            if self.table:
                out.append(f"FROM {', '.join(map(str, self.table))}")

            if self._join:
                out.extend(map(str, self._join))

            if self._where:
                out.append("WHERE")
                out.append(str(self._where))

            if self._group_by:
                out.append("GROUP BY")
                out.append(str(self._group_by))

            if self._having:
                out.append("HAVING")
                out.append(str(self._having))

            if self._order:
                out.append(str(self._order))

            if self._limit:
                out.append(str(self._limit))

            if self._for_update:
                out.append("FOR UPDATE")

            return " ".join(out)

    @property
    def args(self) -> list[Any]:
        """Argument values for the SELECT statement."""
        return (
            self.columns.args
            + reduce(lambda acc, t: acc + (t.args if isinstance(t, Statement) else []), self.table, [])
            + (reduce(lambda x, y: x + (y.args), self._join, []) if self._join else [])
            + (self._where.args if self._where else [])
            + (self._group_by.args if self._group_by else [])
            + (self._having.args if self._having else [])
            + (self._order.args if self._order else [])
            + (self._limit.args if self._limit else [])
        )

    def __bool__(self) -> bool:
        return bool(self.columns) or bool(self.table)


SELECT: TypeAlias = Select  # pylint: disable=invalid-name
"""
Alias for `Select` statement to provide better SQL compatibility, as SQL is often written in all caps.
"""
