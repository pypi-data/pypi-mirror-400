from typing import Any, Self, TypeAlias

from sqlfactory.dialect import SQLDialect
from sqlfactory.execute import ExecutableStatement
from sqlfactory.mixins.limit import Limit, WithLimit
from sqlfactory.mixins.order import OrderArg, WithOrder
from sqlfactory.select.select import Select


class Union(ExecutableStatement, WithOrder, WithLimit):
    """
    Construct UNION statement by combining multiple SELECTs.

    Example:

    >>> from sqlfactory import Select, Union
    >>> sel = Union(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) UNION (SELECT a, b FROM table2)

    Optionally you can specify ordering and limit:

    >>> from sqlfactory import Select, Union, Direction, Limit
    >>> sel = Union(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ...     order=[("a", Direction.ASC)],
    ...     limit=Limit(10),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) UNION (SELECT a, b FROM table2) ORDER BY a ASC LIMIT %s
    >>> print(sel.args)
    [10]

    The same options for ordering and limit apply as for `Select` statement.

    """

    def __init__(
        self,
        *selects: Select,
        order: OrderArg | None = None,
        limit: Limit | None = None,
        dialect: SQLDialect | None = None,
    ) -> None:
        """
        Construct UNION statement by combining multiple SELECTs.

        :param selects: SELECTs to be combined
        :param order: Ordering specification (same as for `Select`)
        :param limit: Limit specification (same as for `Select`)
        """
        super().__init__(order=order, limit=limit, dialect=dialect)
        self._selects = list(selects)

    def append(self, select: Select) -> Self:
        """
        Append another SELECT to the UNION.
        :param select: Select to be appended
        :return: Self for chaining
        """
        self._selects.append(select)
        return self

    @property
    def _joiner(self) -> str:
        return " UNION "

    def __str__(self) -> str:
        out = [self._joiner.join(f"({select!s})" for select in self._selects)]

        if self._order:
            out.append(str(self._order))

        if self._limit:
            out.append(str(self._limit))

        return " ".join(out)

    @property
    def args(self) -> list[Any]:
        """
        Argument values for the UNION statement and all sub-statements.
        """
        out: list[Any] = []

        for select in self._selects:
            out.extend(select.args)

        if self._order:
            out.extend(self._order.args)

        if self._limit:
            out.extend(self._limit.args)

        return out

    def __bool__(self) -> bool:
        return bool(self._selects)


class UnionAll(Union):
    """
    The same as `Union`, but uses `UNION ALL` instead of `UNION` to join SELECTs.

    Example:

    >>> from sqlfactory import Select, UnionAll
    >>> sel = UnionAll(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) UNION ALL (SELECT a, b FROM table2)

    """

    @property
    def _joiner(self) -> str:
        return " UNION ALL "


class UnionDistinct(Union):
    """
    The same as `Union`, but uses `UNION DISTINCT` instead of `UNION` to join SELECTs. UNION DISTINCT is in fact alias for
    plain UNION, but it is provided for clarity if you want to be explicit about the DISTINCT keyword.

    Example:

    >>> from sqlfactory import Select, UnionDistinct
    >>> sel = UnionDistinct(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) UNION DISTINCT (SELECT a, b FROM table2)

    """

    @property
    def _joiner(self) -> str:
        return " UNION DISTINCT "


UNION: TypeAlias = Union  # pylint: disable=invalid-name
"""
Alias for `Union` statement to provide better SQL compatibility, as SQL is often written in all caps.
"""

UNION_ALL: TypeAlias = UnionAll  # pylint: disable=invalid-name
"""
Alias for `UnionAll` statement to provide better SQL compatibility, as SQL is often written in all caps.
"""

UNION_DISTINCT: TypeAlias = UnionDistinct  # pylint: disable=invalid-name
"""
Alias for `UnionDistinct` statement to provide better SQL compatibility, as SQL is often written in all caps.
"""


class Except(Union):
    """
    Construct EXCEPT statement by combining multiple SELECTs.

    Example:

    >>> from sqlfactory import Select, Except
    >>> sel = Except(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) EXCEPT (SELECT a, b FROM table2)

    Optionally you can specify ordering and limit:

    >>> from sqlfactory import Select, Except, Direction, Limit
    >>> sel = Except(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ...     order=[("a", Direction.ASC)],
    ...     limit=Limit(10),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) EXCEPT (SELECT a, b FROM table2) ORDER BY a ASC LIMIT %s
    >>> print(sel.args)
    [10]

    """

    @property
    def _joiner(self) -> str:
        return " EXCEPT "


class ExceptAll(Except):
    """
    The same as `Except`, but uses `EXCEPT ALL` instead of `EXCEPT` to join SELECTs.

    Example:

    >>> from sqlfactory import Select, ExceptAll
    >>> sel = ExceptAll(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) EXCEPT ALL (SELECT a, b FROM table2)

    """

    @property
    def _joiner(self) -> str:
        return " EXCEPT ALL "


class ExceptDistinct(Except):
    """
    The same as `Except`, but uses `EXCEPT DISTINCT` instead of `EXCEPT` to join SELECTs. EXCEPT DISTINCT is in fact alias for
    plain EXCEPT, but it is provided for clarity if you want to be explicit about the DISTINCT keyword.

    Example:

    >>> from sqlfactory import Select, ExceptDistinct
    >>> sel = ExceptDistinct(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) EXCEPT DISTINCT (SELECT a, b FROM table2)

    """

    @property
    def _joiner(self) -> str:
        return " EXCEPT DISTINCT "


EXCEPT: TypeAlias = Except  # pylint: disable=invalid-name
"""
Alias for `Except` statement to provide better SQL compatibility, as SQL is often written in all caps.
"""

EXCEPT_ALL: TypeAlias = ExceptAll  # pylint: disable=invalid-name
"""
Alias for `ExceptAll` statement to provide better SQL compatibility, as SQL is often written in all caps.
"""

EXCEPT_DISTINCT: TypeAlias = ExceptDistinct  # pylint: disable=invalid-name
"""
Alias for `ExceptDistinct` statement to provide better SQL compatibility, as SQL is often written in all caps.
"""


class Intersect(Union):
    """
    Construct INTERSECT statement by combining multiple SELECTs.

    Example:

    >>> from sqlfactory import Select, Intersect
    >>> sel = Intersect(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) INTERSECT (SELECT a, b FROM table2)

    Optionally you can specify ordering and limit:

    >>> from sqlfactory import Select, Intersect, Direction, Limit
    >>> sel = Intersect(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ...     order=[("a", Direction.ASC)],
    ...     limit=Limit(10),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) INTERSECT (SELECT a, b FROM table2) ORDER BY a ASC LIMIT %s
    >>> print(sel.args)
    [10]

    """

    @property
    def _joiner(self) -> str:
        return " INTERSECT "


class IntersectAll(Intersect):
    """
    The same as `Intersect`, but uses `INTERSECT ALL` instead of `INTERSECT` to join SELECTs.

    Example:

    >>> from sqlfactory import Select, IntersectAll
    >>> sel = IntersectAll(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) INTERSECT ALL (SELECT a, b FROM table2)

    """

    @property
    def _joiner(self) -> str:
        return " INTERSECT ALL "


class IntersectDistinct(Intersect):
    """
    The same as `Intersect`, but uses `INTERSECT DISTINCT` instead of `INTERSECT` to join SELECTs. INTERSECT DISTINCT is in fact
    alias for plain INTERSECT, but it is provided for clarity if you want to be explicit about the DISTINCT keyword.

    Example:

    >>> from sqlfactory import Select, IntersectDistinct
    >>> sel = IntersectDistinct(
    ...     Select("a", "b", table="table1"),
    ...     Select("a", "b", table="table2"),
    ... )
    >>> print(sel)
    (SELECT a, b FROM table1) INTERSECT DISTINCT (SELECT a, b FROM table2)

    """

    @property
    def _joiner(self) -> str:
        return " INTERSECT DISTINCT "


INTERSECT: TypeAlias = Intersect  # pylint: disable=invalid-name
"""
Alias for `Intersect` statement to provide better SQL compatibility, as SQL is often written in all caps.
"""

INTERSECT_ALL: TypeAlias = IntersectAll  # pylint: disable=invalid-name
"""
Alias for `IntersectAll` statement to provide better SQL compatibility, as SQL is often written in all caps.
"""

INTERSECT_DISTINCT: TypeAlias = IntersectDistinct  # pylint: disable=invalid-name
"""
Alias for `IntersectDistinct` statement to provide better SQL compatibility, as SQL is often written in all caps.
"""
