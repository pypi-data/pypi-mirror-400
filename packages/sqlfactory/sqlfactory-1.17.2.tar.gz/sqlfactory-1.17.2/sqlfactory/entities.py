"""Classes representing database entities."""

from __future__ import annotations

from collections.abc import Collection
from typing import TYPE_CHECKING, Any

from sqlfactory.statement import Raw, Statement

if TYPE_CHECKING:
    from sqlfactory.condition.in_condition import In  # pragma: nocover
    from sqlfactory.condition.simple import Eq, Ge, Gt, Le, Lt, Ne  # pragma: nocover


class Expression(Statement):
    """
    Expression as statement

    Represents expression that can be used in SQL statements. It provides basic methods for creating complex
    expressions by combining columns, functions and literals together to one arithmetic function.
    """

    def __gt__(self, other: Statement | Any) -> Gt:
        """Shorthand to produce conditional SQL statement <column> > <other>."""
        from sqlfactory.condition.simple import Gt  # pylint: disable=import-outside-toplevel

        return Gt(self, other)

    def __ge__(self, other: Statement | Any) -> Ge:
        """Shorthand to produce conditional SQL statement <column> >= <other>."""
        from sqlfactory.condition.simple import Ge  # pylint: disable=import-outside-toplevel

        return Ge(self, other)

    def __lt__(self, other: Statement | Any) -> Lt:
        """Shorthand to produce conditional SQL statement <column> < <other>."""
        from sqlfactory.condition.simple import Lt  # pylint: disable=import-outside-toplevel

        return Lt(self, other)

    def __le__(self, other: Statement | Any) -> Le:
        """Shorthand to produce conditional SQL statement <column> <= <other>."""
        from sqlfactory.condition.simple import Le  # pylint: disable=import-outside-toplevel

        return Le(self, other)

    def __eq__(self, other: Statement | Any) -> Eq:  # type: ignore[override]
        """Shorthand to produce conditional SQL statement <column> = <other>."""
        from sqlfactory.condition.simple import Eq  # pylint: disable=import-outside-toplevel

        return Eq(self, other)

    def __ne__(self, other: Statement | Any) -> Ne:  # type: ignore[override]
        """Shorthand to produce conditional SQL statement <column> != <other>."""
        from sqlfactory.condition.simple import Ne  # pylint: disable=import-outside-toplevel

        return Ne(self, other)

    def __add__(self, other: Statement | Any) -> Expression:
        return BinaryExpression(self, "+", other)

    def __sub__(self, other: Statement | Any) -> Expression:
        return BinaryExpression(self, "-", other)

    def __mul__(self, other: Statement | Any) -> Expression:
        return BinaryExpression(self, "*", other)

    def __truediv__(self, other: Statement | Any) -> Expression:
        return BinaryExpression(self, "/", other)

    def __mod__(self, other: Statement | Any) -> Expression:
        return BinaryExpression(self, "%", other)

    def __and__(self, other: Statement | Any) -> Expression:
        return BinaryExpression(self, "&", other)

    def __or__(self, other: Statement | Any) -> Expression:
        return BinaryExpression(self, "|", other)

    def __xor__(self, other: Statement | Any) -> Expression:
        return BinaryExpression(self, "^", other)

    def __lshift__(self, other: Statement | Any) -> Expression:
        return BinaryExpression(self, "<<", other)

    def __rshift__(self, other: Statement | Any) -> Expression:
        return BinaryExpression(self, ">>", other)

    def __neg__(self) -> Expression:
        return UnaryExpression("~", self)

    def in_(self, args: Collection[Any]) -> In:
        """Shorthand to `In(column, args)`."""
        from sqlfactory.condition.in_condition import In  # pylint: disable=import-outside-toplevel

        return In(self, args)

    def IN(self, args: Collection[Any]) -> In:
        # pylint: disable=invalid-name
        """Shorthand to `In(column, args)`"""
        return self.in_(args)

    def not_in(self, args: Collection[Any]) -> In:
        """Shorthand to `In(column, args, negative=True)`."""
        from sqlfactory.condition.in_condition import In  # pylint: disable=import-outside-toplevel

        return In(self, args, negative=True)

    def NOT_IN(self, args: Collection[Any]) -> In:
        # pylint: disable=invalid-name
        """Shorthand to `In(column, ..., negative=True)`."""
        return self.not_in(args)


class UnaryExpression(Expression):
    """
    Expression where operator preceeds expression.
    """

    def __init__(self, operator: str, statement: Statement | Any) -> None:
        super().__init__()

        self.operator = operator
        self.statement = statement

    def __str__(self) -> str:
        stmt = self.statement if isinstance(self.statement, Statement) else self.dialect.placeholder
        return f"({self.operator}{stmt!s})"

    @property
    def args(self) -> list[Any]:
        return self.statement.args if isinstance(self.statement, Statement) else [self.statement]


class BinaryExpression(Expression):
    """
    Expression where left and right statements are combined using operator.
    """

    def __init__(self, left: Statement | Any, operator: str, right: Statement | Any) -> None:
        super().__init__()

        self.left = left
        self.operator = operator
        self.right = right

    def __str__(self) -> str:
        left = self.left if isinstance(self.left, Statement) else self.dialect.placeholder
        right = self.right if isinstance(self.right, Statement) else self.dialect.placeholder

        return f"({left!s} {self.operator} {right!s})"

    @property
    def args(self) -> list[Any]:
        out: list[Any] = []

        if isinstance(self.left, Statement):
            out.extend(self.left.args)
        else:
            out.append(self.left)

        if isinstance(self.right, Statement):
            out.extend(self.right.args)
        else:
            out.append(self.right)

        return out


class RawExpression(Expression, Raw):
    """Expression as result of another expression."""


class Column(Expression):
    """
    Column (optionally with table and database) as statement.

    >>> from sqlfactory import Column
    >>> Column("column")
    >>> "`column`"

    >>> from sqlfactory import Column
    >>> Column("table.column")
    >>> "`table`.`column`"

    >>> from sqlfactory import Column
    >>> Column("database.table.column")
    >>> "`database`.`table`.`column`"

    Star-columns are also supported, although they are not recommended to be used. Always try to specify exact columns to select.

    >>> from sqlfactory import Column
    >>> Column("*")
    >>> "*"

    >>> from sqlfactory import Column
    >>> Column("table.*")
    >>> "`table`.*"

    >>> from sqlfactory import Column
    >>> Column("database.table.*")
    >>> "`database`.`table`.*"

    To use column with `Select` statement with alias, you can use `Aliased` or `SelectColumn` classes instead.

    The class also provides shorthand for creating conditional SQL statements and arithmetic SQL statements. You can use Column
    instance to directly create condition using simple operators (`==`, `!=`, `<`, `<=`, `>`, `>=`) or arithmetic operations
    (`+`, `-`, `*`, `/`, `%`).

    >>> from sqlfactory import Column
    >>> Column("table.column") == 5
    >>> # Produces Eq(Column("table.column"), 5)

    >>> from sqlfactory import Column
    >>> Column("table.column") + 5
    >>> # Produces Expression("`table`.`column` + %s", 5)
    """

    def __init__(self, column: str) -> None:
        super().__init__()

        self._column = column.split(".")
        if len(self._column) > 3:
            raise ValueError("Invalid column name (contains more than <database>.<table>.<column>).")

    def __str__(self) -> str:
        return ".".join(
            f"{self.dialect.quote}{x}{self.dialect.quote}" if not x.startswith(self.dialect.quote) and x != "*" else x
            for x in self._column
        )

    @property
    def column(self) -> str:
        """Returns column part of the column name."""
        return self._column[-1]

    @property
    def table(self) -> str | None:
        """Returns table part of the column name, if specified. If column specification does not contain table name,
        returns None."""
        try:
            return self._column[-2]
        except IndexError:
            return None

    @property
    def database(self) -> str | None:
        """Returns database part of the column name, if specified. If column specification does not contain database
        name, returns None."""
        try:
            return self._column[-3]
        except IndexError:
            return None

    def __hash__(self) -> int:
        return hash(str(self))

    @property
    def args(self) -> list[Any]:
        """Column does not have any arguments, so this always returns empty list."""
        return []


class Table(Statement):
    """
    Table (optionally with database) as statement

    >>> from sqlfactory import Table
    >>> Table("table")
    >>> "`table`"

    >>> from sqlfactory import Table
    >>> Table("database.table")
    >>> "`database`.`table`"

    To produce table alias, use `Aliased` class:

    >>> from sqlfactory import Table, Aliased
    >>> Aliased(Table("database.table"), alias="t1")
    >>> "`database`.`table` AS `t1`"

    By accessing Table's undefined attributes, instance of Column is returned. This allows to easily access columns of
    that table, and reference them in SQL statements.

    >>> from sqlfactory import Table, Select
    >>> t = Table("table")
    >>> Select(t.id, t.name, table=t)
    >>> "SELECT `table`.`id`, `table`.`name` FROM `table`"

    This allows creating python-like expressions that are converted to SQL automatically:

    >>> from sqlfactory import Table, Select
    >>> from sqlfactory.func.agg import Count
    >>> t = Table("database.table")
    >>> Select(Count(t.id), table=t, where=t.id > 5)
    >>> "SELECT COUNT(`database`.`table`.`id`) FROM `database`.`table` WHERE `database`.`table`.`id` > %s"
    """

    def __init__(self, table: str) -> None:
        """
        :param table: Table name (optionally with database in form `<database>.<table>`). If database is not specified,
            it is assumed that table is in default database and SQL constructed will not contain any database name.
        """
        super().__init__()
        self._table = table.split(".")

        if len(self._table) > 2:
            raise ValueError("Invalid table name (contains more than <database>.<table>).")

    def __str__(self) -> str:
        return ".".join(
            f"{self.dialect.quote}{x}{self.dialect.quote}" if not x.startswith(self.dialect.quote) else x for x in self._table
        )

    @property
    def table(self) -> str | None:
        """Returns table part of the table name"""
        return self._table[-1]

    @property
    def database(self) -> str | None:
        """Returns database part of the table name, if specified. If table specification does not contain database,
        returns None."""
        try:
            return self._table[-2]
        except IndexError:
            return None

    def __getattr__(self, name: str) -> Column:
        """Returns column of that table."""
        return Column(f"{'.'.join(self._table)}.{name}")

    @property
    def __isabstractmethod__(self) -> bool:
        """
        This is needed to be able to use Table instance in abstract classes as ClassVar.

        class Something(ABC):
            table: ClassVar[Table] = Table("table")

        - ABC checks for __isabstractmethod__ property for all attributes in __dict__, and because Table did not
        contains it, __getattr__ is called, which returns Column, which evaluates to True, which in turn makes
        ABC think that Table is abstract method. So by providing explicit implementation here, we avoid this error.
        """
        return False

    @property
    def args(self) -> list[Any]:
        """Table does not have any arguments, this always returns empty list."""
        return []


# Alias for column that can be passed as instance of column or as string.
ColumnArg = Column | str
