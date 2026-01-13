from __future__ import annotations

from typing import TYPE_CHECKING, Any, Collection, Self, overload

from sqlfactory.condition import ConditionBase
from sqlfactory.entities import Table
from sqlfactory.statement import Statement

if TYPE_CHECKING:
    from sqlfactory.select import Select  # pragma: no cover


class Join(Statement):
    """
    Produces `JOIN` statement

    Usage:

    >>> from sqlfactory import Join, Eq
    >>> Join("table2", on=Eq("table1.id", "table2.id"))
    >>> "JOIN `table2` ON `table1`.`id` = `table2`.`id`"

    >>> from sqlfactory import Join, Eq
    >>> Join("table2", on=Eq("table1.id", "t2.id"), alias="t2")
    >>> "JOIN `table2` AS `t2` ON `table1`.`id` = `t2`.`id`"

    With subquery:

    >>> from sqlfactory import Join, Eq, Select, Column
    >>> from sqlfactory.func.agg import Sum
    >>> Join(
    ...     Select("table2.product_id", Sum("price"), table="table2", where=Eq("table2.enabled", True)),
    ...     alias="t2",
    ...     on=Eq("t2.product_id", Column("table.id"))
    ... )
    >>> "JOIN ("
    ... "SELECT `table2`.`product_id`, SUM(`price`) "
    ... "FROM `table2` "
    ... "WHERE `table2`.`enabled` = %s"
    ... ") AS `t2` ON `t2`.`product_id` = `table`.`id`"

    Note that for subquery join, alias must be always specified.
    """

    def __init__(self, table: str | Table | Select, on: ConditionBase | None = None, alias: str | None = None) -> None:
        """
        :param table: Table to be joined
        :param on: ON condition
            **Note:** `Eq()` and all other condition functions are expecting first argument to be column and second argument to
            be value. If you want to have column on the right side or value on the left, you must explicitly use `Column()`
            function. And if you want literal value on the left side, you must explicitly use `Value()` function.
        :param alias: Optional alias of the joined table.
        """
        super().__init__()

        if isinstance(table, str):
            table = Table(table)

        self.table = table
        """Table to be joined"""

        self.on = on
        """ON join condition"""

        self.alias = alias
        """Optional alias for the joined table."""

        from sqlfactory.select import Select  # pylint: disable=import-outside-toplevel, cyclic-import

        if isinstance(self.table, Select) and not self.alias:
            raise AttributeError("When joining a subselect, alias must be specified.")

    @property
    def join_spec(self) -> str:
        """
        Returns the JOIN type itself for generation of SQL query.
        @private
        """
        return "JOIN"

    def __str__(self) -> str:
        from sqlfactory.select import Select  # pylint: disable=import-outside-toplevel, cyclic-import

        if self.alias:
            if isinstance(self.table, Select):
                table = f"({self.table!s}) AS `{self.alias}`"
            else:
                table = f"{self.table!s} AS `{self.alias}`"
        else:
            table = str(self.table)

        if self.on:
            return f"{self.join_spec} {table} ON {self.on!s}"

        return f"{self.join_spec} {table}"

    @property
    def args(self) -> list[Any]:
        """Argument values of the JOIN statement."""
        return [*(self.table.args if isinstance(self.table, Statement) else []), *(self.on.args if self.on else [])]


class LeftJoin(Join):
    """
    Produces `LEFT JOIN` statement

    Usage:

    >>> from sqlfactory import LeftJoin, Eq, Column
    >>> LeftJoin("table2", on=Eq("table1.id", Column("table2.id")))
    >>> "LEFT JOIN `table2` ON `table1`.`id` = `table2`.`id`"
    """

    @property
    def join_spec(self) -> str:
        return "LEFT JOIN"


class LeftOuterJoin(Join):
    """
    Produces `LEFT OUTER JOIN` statement

    Usage:

    >>> from sqlfactory import LeftOuterJoin, Eq, Column
    >>> LeftOuterJoin("table2", on=Eq("table1.id", Column("table2.id")))
    >>> "LEFT OUTER JOIN `table2` ON `table1`.`id` = `table2`.`id`"
    """

    @property
    def join_spec(self) -> str:
        return "LEFT OUTER JOIN"


class RightJoin(Join):
    """
    Produces `RIGHT JOIN` statement

    Usage:

    >>> from sqlfactory import RightJoin, Eq, Column
    >>> RightJoin("table2", on=Eq("table1.id", Column("table2.id")))
    >>> "RIGHT JOIN `table2` ON `table1`.`id` = `table2`.`id`"
    """

    @property
    def join_spec(self) -> str:
        return "RIGHT JOIN"


class RightOuterJoin(Join):
    """
    Produces `RIGHT OUTER JOIN` statement

    Usage:

    >>> from sqlfactory import RightOuterJoin, Eq, Column
    >>> RightOuterJoin("table2", on=Eq("table1.id", Column("table2.id")))
    >>> "RIGHT OUTER JOIN `table2` ON `table1`.`id` = `table2`.`id`"
    """

    @property
    def join_spec(self) -> str:
        return "RIGHT OUTER JOIN"


class InnerJoin(Join):
    """
    Produces `INNER JOIN` statement

    Usage:

    >>> from sqlfactory import InnerJoin, Eq, Column
    >>> InnerJoin("table2", on=Eq("table1.id", Column("table2.id")))
    >>> "INNER JOIN `table2` ON `table1`.`id` = `table2`.`id`"
    """

    @property
    def join_spec(self) -> str:
        return "INNER JOIN"


class CrossJoin(Join):
    """
    Produces `CROSS JOIN` statement

    Usage:

    >>> from sqlfactory import CrossJoin, Eq, Column
    >>> CrossJoin("table2", on=Eq("table1.id", Column("table2.id")))
    >>> "CROSS JOIN `table2` ON `table1`.`id` = `table2`.`id`"
    """

    @property
    def join_spec(self) -> str:
        return "CROSS JOIN"


class WithJoin:
    """Mixin to provide JOIN support for query generator."""

    def __init__(self, *args: Any, join: Collection[Join] | None = None, **kwargs: Any) -> None:
        """
        :param join: List of JOIN clauses
        """
        super().__init__(*args, **kwargs)
        self._join = list(join) if join is not None else []

    def _append_join(self, join: Join) -> Self:
        """Append join to list of joins."""
        if not self._join:
            self._join = []

        if join not in self._join:
            self._join.append(join)

        return self

    @overload
    def join(self, join: Join, /) -> Self:
        """Append JOIN clause to the query (any Join instance)."""

    @overload
    def join(self, table: str | Table | Select, on: ConditionBase | None = None, alias: str | None = None) -> Self:
        """
        Append JOIN clause to the query.
        JOIN `table` AS <alias> ON (<condition>)

        :param table: Table to be joined
        :param on: ON condition
            **Note:** `Eq()` and all other condition functions are expecting first argument to be column and second argument to
            be value. If you want to have column on the right side or value on the left, you must explicitly use `Column()`
            function. And if you want literal value on the left side, you must explicitly use `Value()` function.
        :param alias: Optional alias of the joined table.
        """

    def join(self, table: str | Table | Join | Select, on: ConditionBase | None = None, alias: str | None = None) -> Self:
        """
        Append JOIN clause to the query.
        JOIN `table` AS <alias> ON (<condition>)

        :param table: Table to be joined (or instance of the Join class)
        :param on: ON condition (when first argument is not instance of Join class)
            **Note:** `Eq()` and all other condition functions are expecting first argument to be column and second argument to
            be value. If you want to have column on the right side or value on the left, you must explicitly use `Column()`
            function. And if you want literal value on the left side, you must explicitly use `Value()` function.
        :param alias: Optional alias of the joined table, if table is not instance of the Join class.
        """
        if isinstance(table, Join):
            if on is not None or alias is not None:
                raise AttributeError("When passing Join instance directly, on or alias attributes cannot be specified.")

            return self._append_join(table)

        return self._append_join(Join(table, on, alias))

    @overload
    def JOIN(self, join: Join, /) -> Self:  # pylint: disable=invalid-name
        """Alias for join() to be more SQL-like with all capitals."""

    @overload
    def JOIN(self, table: str | Table | Select, on: ConditionBase | None = None, alias: str | None = None) -> Self:
        # pylint: disable=invalid-name
        """Alias for join() to be more SQL-like with all capitals."""

    def JOIN(self, table: str | Table | Select | Join, on: ConditionBase | None = None, alias: str | None = None) -> Self:
        # pylint: disable=invalid-name
        """Alias for join() to be more SQL-like with all capitals."""
        return self.join(table, on, alias)  # type: ignore[arg-type]  # mypy searches in overloads

    def left_join(self, table: str | Table | Select, on: ConditionBase | None = None, alias: str | None = None) -> Self:
        """
        Append LEFT JOIN clause to the query.

        :param table: Table to be joined
        :param on: ON condition
            **Note:** `Eq()` and all other condition functions are expecting first argument to be column and second argument to
            be value. If you want to have column on the right side or value on the left, you must explicitly use `Column()`
            function. And if you want literal value on the left side, you must explicitly use `Value()` function.
        :param alias: Optional alias of the joined table.
        """
        return self.join(LeftJoin(table, on, alias))

    def LEFT_JOIN(self, table: str | Table | Select, on: ConditionBase | None = None, alias: str | None = None) -> Self:
        # pylint: disable=invalid-name
        """Alias for left_join() to be more SQL-like with all capitals."""
        return self.left_join(table, on, alias)

    def right_join(self, table: str | Table | Select, on: ConditionBase | None = None, alias: str | None = None) -> Self:
        """
        Append RIGHT JOIN clause to the query.

        :param table: Table to be joined
        :param on: ON condition
            **Note:** `Eq()` and all other condition functions are expecting first argument to be column and second argument to
            be value. If you want to have column on the right side or value on the left, you must explicitly use `Column()`
            function. And if you want literal value on the left side, you must explicitly use `Value()` function.
        :param alias: Optional alias of the joined table.
        """
        return self.join(RightJoin(table, on, alias))

    def RIGHT_JOIN(self, table: str | Table | Select, on: ConditionBase | None = None, alias: str | None = None) -> Self:
        # pylint: disable=invalid-name
        """Alias for right_join() to be more SQL-like with all capitals."""
        return self.right_join(table, on, alias)
