"""Column / Statement aliasing support"""

from typing import Any

from sqlfactory.entities import Column, ColumnArg
from sqlfactory.statement import Statement


class Aliased(Statement):
    """
    Aliased generic statement. Only to be used in SELECT statement, where AS statement is only valid.

    Usage:

    >>> from sqlfactory import Aliased
    >>> from sqlfactory.func.agg import Count
    >>> Aliased(Count('*'), alias='count')
    >>> "COUNT(*) AS `count`"

    >>> from sqlfactory import Select, Aliased
    >>> from sqlfactory.func.agg import Count
    >>> Select(Aliased(Count('*'), alias='count'), table='orders')
    >>> 'SELECT COUNT(*) AS `count` FROM `orders`'
    """

    def __init__(self, statement: Statement | ColumnArg, alias: str | None = None) -> None:
        """
        :param statement: Statement to be aliased
        :param alias: Alias of the statement.
        """
        super().__init__()
        self._statement = statement if isinstance(statement, Statement) else Column(statement)

        self.alias = alias
        """Alias of the statement"""

    def __str__(self) -> str:
        if self.alias is None:
            return str(self._statement)

        from sqlfactory.select import Select  # pylint: disable=import-outside-toplevel, cyclic-import

        if isinstance(self._statement, Select):
            return f"({self._statement!s}) AS `{self.alias}`"

        return f"{self._statement!s} AS `{self.alias}`"

    @property
    def args(self) -> list[Any]:
        """Argument values of the aliased statement"""
        return self._statement.args

    def __getattr__(self, name: str) -> Any:
        """Proxy to access attributes of inner (non-aliased) statement."""
        return getattr(self._statement, name)


class SelectColumn(Aliased):
    """
    Aliased column. Shortcut for `Aliased(Column(column), alias)`

    Usage:

    >>> from sqlfactory import Select, SelectColumn
    >>> Select(SelectColumn("table.column", alias="otherColumn"), table="table")
    >>> "SELECT `table`.`column` AS `otherColumn` FROM `table`"

    >>> from sqlfactory import Select, SelectColumn
    >>> Select(SelectColumn("table.column", distinct=True), table="table")
    >>> "SELECT DISTINCT `table`.`column` FROM `table`"

    >>> from sqlfactory import Select, SelectColumn
    >>> Select(SelectColumn("table.column", alias="otherColumn", distinct=True), table="table")
    >>> "SELECT DISTINCT `table`.`column` AS `otherColumn` FROM `table`"
    """

    def __init__(self, column: ColumnArg, alias: str | None = None, distinct: bool = False):
        """
        :param column: Column to be selected
        :param alias: Optional alias of the column
        :param distinct: Whether to select only distinct values (prepend DISTINCT to column name)
        """
        super().__init__(column, alias)
        self.distinct = distinct
        """Whether to select only distinct values (adds DISTINCT to the column selector)."""

    def __str__(self) -> str:
        if self.distinct:
            return f"DISTINCT {super().__str__()}"

        return super().__str__()
