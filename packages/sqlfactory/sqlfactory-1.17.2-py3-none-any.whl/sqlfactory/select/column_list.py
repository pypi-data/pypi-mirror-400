"""Column list for usage in SELECT statement."""

from __future__ import annotations

from typing import Any, Iterable, Self

from sqlfactory.entities import Column, ColumnArg
from sqlfactory.statement import Statement


class ColumnList(Statement, list[Statement]):  # type: ignore[misc]
    """
    Unique(ish) set of columns to be used in SELECT statement. This class is usefull when you want to dynamically build
    list of selected columns and you don't want to have duplicate selects in the list.

    Usage:

    >>> c = ColumnList(["column1", "column2", "column3"])
    >>> c.append("column4")  # append() works, as with any other list.
    >>> c.add("column5")  # add() works too.
    >>> c.append("column1")  # this will not be added, because column1 is already in the list.
    >>>
    >>> print(c)
    >>> "[`column1`, `column2`, `column3`, `column4`, `column5`]"
    >>>
    >>> Select(select=c, table="table")
    >>> "SELECT `column1`, `column2`, `column3`, `column4`, `column5` FROM `table`"

    You can also use any other statement:

    >>> c = ColumnList()
    >>> c.append(If(Eq("column", True), "column2", "column3"))
    >>> print(c, c.args)
    >>> "[IF(`column` = %s, `column2`, `column3`)], [True]"

    Few more examples:

    >>> ColumnList([
    >>>    "c1"
    >>>    Column("c2"),
    >>>    Count("*"),
    >>>    SelectColumn("c3", alias="otherColumn"),
    >>>    Aliased(If(Eq("column", True), "column2", "column3"), alias="condition")
    >>>    Table("t").id,
    >>> ])
    >>> "[`c1`, `c2`, COUNT(*), `c3` AS `otherColumn`, IF(`column` = %s, `column2`, `column3`) AS `condition`, `t`.`id`]"
    """

    def __init__(self, iterable: Iterable[Statement | ColumnArg] | None = None) -> None:
        """
        :param iterable: Initial content of the column list. Can be either string, which is parsed into
        `[[database.]table.]column` tuple and then escaped properly. Or it can be a `Column` instance, which is added
        directly to the list. Any other statement is added as is.
        """
        if iterable:
            super().__init__([Column(i) if not isinstance(i, Statement) else i for i in iterable])
        else:
            super().__init__()

    def __contains__(self, other: Statement) -> bool:  # type: ignore[override]
        """
        Checks whether the column is already in the list. Handles correctly parsing of columns, so Column("c1") == "c1".
        """
        if not isinstance(other, Statement):
            raise AttributeError("ColumnList can only contain Statement objects.")

        for item in self:
            if str(item) == str(other) and item.args == other.args:
                return True

        return False

    def add(self, element: Statement | str) -> Self:
        """
        Add new columns to the set. If the column is already in the list, it is not added again.

        :param element: New select column to be added. Can be either string (which is treated as `Column` automatically),
            `Column` instance or any generic statement such as function call (`Count('*')` for example).
        """
        return self.append(element)

    def append(self, element: Statement | str) -> Self:  # type: ignore[override]
        """
        Add new columns to the set. If the column is already in the list, it is not added again.

        This is alias for `ColumnList.add()`.

        :param element: New select column to be added. Can be either string (which is treated as `Column` automatically),
            `Column` instance or any generic statement such as function call (`Count('*')` for example).
        """
        if not isinstance(element, Statement):
            element = Column(element)

        if element not in self:
            super().append(element)

        return self

    def update(self, iterable: Iterable[Statement | str]) -> Self:
        """
        Add multiple new columns to the set.
        :param iterable: New select columns to be added. Can be either string (which is treated as `Column` automatically),
            `Column` instance or any generic statement such as function call (`Count('*')` for example). Added columns
            are checked for uniqueness and duplicates are automatically skipped.
        """
        for item in iterable:
            self.add(item)

        return self

    def __str__(self) -> str:
        """
        Returns string representation of the column list usable for SELECT statement building.
        """
        return ", ".join(map(str, self))

    def __repr__(self) -> str:
        return "[" + ", ".join(map(repr, self)) + "]"

    @property
    def args(self) -> list[Any]:
        """Argument values of the column list statement."""
        out = []

        for item in self:
            if isinstance(item, Statement):
                out.extend(item.args)

        return out
