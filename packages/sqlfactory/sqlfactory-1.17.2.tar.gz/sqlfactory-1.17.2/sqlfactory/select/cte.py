from typing import Any, Collection, Self

from sqlfactory.dialect import SQLDialect
from sqlfactory.entities import Column, Table
from sqlfactory.execute import ExecutableStatement
from sqlfactory.select.select import Select
from sqlfactory.select.union import Union


class With(ExecutableStatement):
    """
    Common Table Expression (CTE) statement.

    Usage:

    >>> from sqlfactory import With, Select, Gt, Eq, Column
    >>> With('t').as_(
    ...     Select('a', table='t1', where=Gt('b', 1))
    ... ).select(
    ...     Select('a', 'b', 'c', table=['t2', 't'], where=Eq('t2.c', Column('t.a'))
    ... )
    ... "WITH `t` AS (SELECT `a` FROM `t1` WHERE `b` > 1) SELECT `a`, `b`, `c` FROM `t2`, `t` WHERE `t2`.`c` = `t`.`a`"

    Recursive CTE:

    >>> from sqlfactory import With, Select, Aliased, Union, Column
    >>> With('ancestors', recursive=True).as_(
    ...     Union(
    ...         Select('*', table='folks', where=Eq('name', 'Alex')),
    ...         Select(
    ...             'f.*',
    ...             table=[
    ...                 Table("folks", alias="f"),
    ...                 Table("ancestors", alias="a")
    ...             ],
    ...             where=Eq("f.id", Column("a.parent_id"))
    ...         )
    ...     )
    ... ).select(Select(
    ...     'id', 'name', 'parent_id',
    ...     table='ancestors'
    ... ))
    ... "WITH RECURSIVE `ancestors` AS ("
    ...    "SELECT `id`, `name`, `parent_id` FROM `folks` WHERE `name` = %s "
    ...    "UNION SELECT `f`.`*` FROM `folks` AS `f`, `ancestors` AS `a` WHERE `f`.`id` = `a`.`parent_id`"
    ... ") SELECT `id`, `name`, `parent_id` FROM `ancestors`"
    ... ["Alex"]
    """

    def __init__(
        self,
        name: str | Table,
        columns: Collection[str | Column] | None = None,
        cte: Select | Union | None = None,
        select: Select | None = None,
        dialect: SQLDialect | None = None,
        *,
        recursive: bool = False,
    ) -> None:
        """
        :param name: Name of the resulting table produced by the CTE.
        :param columns: Optional list of column names the table should have.
        :param cte: Expression to create the table. This can be Select or Union.
        :param select: Select statement that will be executed after the CTE table has been constructed. Can use the CTE table.
        :param dialect: SQL dialect to use for the statement. If not provided, the default dialect will be used.
        :param recursive: If True, the CTE will be recursive. This means that the CTE can refer to itself in its own definition.
        """

        super().__init__(dialect=dialect)

        self._name = name if isinstance(name, Table) else Table(name)
        self._columns = [column if isinstance(column, Column) else Column(column) for column in columns] if columns else None
        self._recursive = recursive
        self._cte = cte
        self._select = select

    def as_(self, select: Select | Union) -> Self:
        """
        Specify the definition of the CTE table. This can be a Select or Union statement, that will produce the results for the
        CTE.
        :param select: Statement.
        """

        self._cte = select
        return self

    def select(self, select: Select) -> Self:
        """
        Select that will be executed after the CTE has been constructed.
        :param select: Select to execute.
        """

        self._select = select
        return self

    def __str__(self) -> str:
        """Return serialized CTE string."""

        if not self._cte:
            raise AttributeError("Missing CTE part of the select.")

        if not self._select:
            raise AttributeError("Missing SELECT part of the CTE statement.")

        with self.dialect:
            columns = "" if not self._columns else f" ({', '.join(map(str, self._columns))})"

            return f"WITH {'RECURSIVE ' if self._recursive else ''}{self._name}{columns} AS ({self._cte}) {self._select}"

    def __bool__(self) -> bool:
        return self._cte is not None and bool(self._cte) and self._select is not None and bool(self._select)

    @property
    def args(self) -> list[Any]:
        """Arguments of the CTE statement."""

        args = [*self._name.args]

        if self._columns:
            for column in self._columns:
                args += column.args

        args.extend(
            [
                *(self._cte.args if self._cte else []),
                *(self._select.args if self._select else []),
            ]
        )

        return args
