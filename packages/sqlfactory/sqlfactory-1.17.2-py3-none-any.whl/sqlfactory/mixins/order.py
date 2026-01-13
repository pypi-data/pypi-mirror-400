"""ORDER BY mixin for query generator"""

from __future__ import annotations

from enum import Enum
from typing import Any, Collection, Literal, Optional, Self

from sqlfactory.entities import Column, ColumnArg
from sqlfactory.statement import Statement


class Direction(str, Enum):
    """
    Ordering direction as enum

    Usage:

    >>> from sqlfactory import Order, Direction
    >>> Order([('column1', Direction.ASC), ('column2', Direction.DESC)])
    >>> "ORDER BY `column1` ASC, `column2` DESC"
    """

    ASC = "ASC"
    DESC = "DESC"


OrderColumn = ColumnArg | Statement


class Order(list[tuple[OrderColumn, Direction | Literal["ASC", "DESC"]]], Statement):  # type: ignore[misc]
    """
    ORDER BY statement as list of columns to use for ordering. For usage with SELECT, UPDATE and DELETE statements.

    Usage:

    >>> from sqlfactory import Order, Direction
    >>> Order([('column1', Direction.ASC), ('column2', Direction.DESC)])
    >>> "ORDER BY `column1` ASC, `column2` DESC"
    """

    def __str__(self) -> str:
        if not self:
            return ""

        out = []

        for column, direction in self:
            if isinstance(column, str):
                column = Column(column)

            out.append(f"{column!s} {direction.value if isinstance(direction, Direction) else direction}")

        return f"ORDER BY {', '.join(out)}"

    @property
    def args(self) -> list[Any]:
        """Argument values for the order by statement"""
        out = []
        for column, _ in self:
            if isinstance(column, Statement):
                out.extend(column.args)

        return out


class WithOrder:
    """Mixin to provide ORDER BY support for query generator."""

    def __init__(self, *args: Any, order: OrderArg | None = None, **kwargs: Any) -> None:
        """

        Example:

        >>> from sqlfactory import Select, Direction
        >>> query = Select(order=[('column1', Direction.ASC), ('column2', Direction.DESC)])

        >>> from sqlfactory import Select, Order, Direction
        >>> query = Select(order=Order([('column1', Direction.ASC), ('column2', Direction.DESC)]))

        :param order: Ordering specification - either instance of Order, or collection of columns and directions.
        """
        super().__init__(*args, **kwargs)
        if order:
            self._order: Optional[Order] = order if isinstance(order, Order) else Order(order)
        else:
            self._order = None

    def order_by(self, column: OrderColumn, direction: Direction) -> Self:
        """
        Add column to be used for ordering. Can be called multiple times, columns will be ordered by order of calls.

        Example:

        >>> from sqlfactory import Select, Direction
        >>> query = Select().order_by('column1', Direction.ASC).order_by('column2', Direction.DESC)

        :param column: Column to use for ordering
        :param direction: Ordering direction
        """
        if self._order is None:
            self._order = Order()

        self._order.append((column, direction))
        return self

    def ORDER_BY(self, column: OrderColumn, direction: Direction) -> Self:  # pylint: disable=invalid-name
        """Alias for `WithOrder.order_by()` to be more SQL-like with all capitals."""
        return self.order_by(column, direction)


# Ordering argument for class init (specify directly instance of Order, or collection of columns and directions).
OrderArg = Order | Collection[tuple[OrderColumn, Direction]]
