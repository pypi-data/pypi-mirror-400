from __future__ import annotations

from abc import ABC, abstractmethod
from contextvars import ContextVar, Token
from types import TracebackType
from typing import ClassVar, Optional, Self, Type


class SQLDialect(ABC):
    """
    Base class for representing SQL dialect for building SQL queries.

    This class is used to configure SQL dialect for building SQL queries. It is used to configure placeholders for
    arguments and quote characters for table and column names.

    Usage:

    >>> from sqlfactory import PostgreSQLDialect, SQLiteDialect, Statement, Select, Eq
    >>>
    >>> # Set default dialect for whole library.
    >>> Statement.default_dialect = PostgreSQLDialect()
    >>>
    >>> sel = Select("a", table="table", where=Eq("id", 1))
    >>> str(sel)
    SELECT "a" FROM "table" WHERE "id" = %s
    >>>
    >>> # Overwrite dialect for this particular statement
    >>> sel = Select("a", table="table", where=Eq("id", 1), dialect=SQLiteDialect())
    >>> str(sel)
    SELECT `a` FROM `table` WHERE `id` = ?
    >>>
    >>> # Use dialect for all statements in the context.
    >>> with SQLiteDialect():
    ...   sel = Select("a", table="table", where=Eq("id", 1))
    ...   str(sel)  # SELECT `a` FROM `table` WHERE `id` = ?
    ...
    ...   # Explicit dialect always has precedence over context.
    ...   sel = Select(dialect=PostgreSQLDialect())
    ...   str(sel)  # SELECT "a" FROM "table" WHERE "id" = %s


    Implementing custom dialect:

    >>> from sqlfactory import SQLDialect, In
    >>>
    >>> class CustomDialect(SQLDialect):
    ...     @property
    ...     def placeholder(self) -> str:
    ...         return "$hello"
    ...
    ...     @property
    ...     def quote(self) -> str:
    ...         return '*'
    >>>
    >>> with CustomDialect():
    ...    str(In("column", [1, 2, 3]))
    ...
    '*column* IN ($hello, $hello, $hello)'

    """

    dialect_context: ClassVar[ContextVar[Optional[SQLDialect]]] = ContextVar("SQLDialect", default=None)
    """
    Context variable holding currently set SQL dialect.
    """

    def __init__(self) -> None:
        self._token: list[Token[SQLDialect | None]] = []

    @property
    @abstractmethod
    def placeholder(self) -> str:
        """Placeholder for arguments in SQL query."""

    @property
    @abstractmethod
    def quote(self) -> str:
        """Quote character for table and column names."""

    def __enter__(self) -> Self:
        self._token.append(self.dialect_context.set(self))
        return self

    def __exit__(
        self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException], exc_stack: Optional[TracebackType]
    ) -> None:
        self.dialect_context.reset(self._token.pop())


class MySQLDialect(SQLDialect):
    """
    MySQL dialect for SQLFactory.
    """

    @property
    def placeholder(self) -> str:
        return "%s"

    @property
    def quote(self) -> str:
        return "`"


class SQLiteDialect(SQLDialect):
    """
    SQLite dialect for SQLFactory.
    """

    @property
    def placeholder(self) -> str:
        return "?"

    @property
    def quote(self) -> str:
        return "`"


class PostgreSQLDialect(SQLDialect):
    """
    PostgreSQL dialect for SQLFactory.
    """

    @property
    def placeholder(self) -> str:
        return "%s"

    @property
    def quote(self) -> str:
        return '"'


class OracleSQLDialect(SQLDialect):
    """
    Oracle SQL dialect for SQLFactory. With indexed placeholders.
    """

    def __init__(self, initial_index: int = 1) -> None:
        """
        :param initial_index: Index where to start counting placeholders.
        """
        super().__init__()
        self._index = initial_index
        self._initial_index = initial_index

    @property
    def placeholder(self) -> str:
        index = self._index
        self._index += 1
        return f":{index}"

    @property
    def quote(self) -> str:
        return '"'

    def __enter__(self) -> Self:
        self._index = self._initial_index
        return super().__enter__()
