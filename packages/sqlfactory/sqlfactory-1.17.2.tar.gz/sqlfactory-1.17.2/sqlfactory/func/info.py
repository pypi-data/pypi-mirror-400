"""Information functions (https://mariadb.com/kb/en/information-functions/)."""

from typing import Any

from sqlfactory.entities import Column
from sqlfactory.func.base import Function
from sqlfactory.statement import Statement


class Benchmark(Function):
    """Executes an expression repeatedly."""

    def __init__(self, count: int, expression: Statement) -> None:
        super().__init__("BENCHMARK", count, expression)


class BinlogGtidPos(Function):
    """Returns a string representation of the corresponding GTID position."""

    def __init__(self) -> None:
        super().__init__("BINLOG_GTID_POS")


class Charset(Function):
    """Returns the character set."""

    def __init__(self) -> None:
        super().__init__("CHARSET")


class Coercibility(Function):
    """Returns the collation coercibility value of the string expression."""

    def __init__(self, expression: str) -> None:
        super().__init__("COERCIBILITY", expression)


class Collation(Function):
    """Collation of the string argument"""

    def __init__(self, expression: str) -> None:
        super().__init__("COLLATION", expression)


class Collate(Statement):
    """String with collation"""

    def __init__(self, expression: str | Statement, collation: str) -> None:
        super().__init__()

        self._expression = expression
        self._collation = collation

    def __str__(self) -> str:
        return (
            f"{str(self._expression) if isinstance(self._expression, Statement) else self.dialect.placeholder} "
            f"COLLATE {self._collation}"
        )

    @property
    def args(self) -> list[Any]:
        return self._expression.args if isinstance(self._expression, Statement) else [self._expression]


class ConnectionId(Function):
    """Connection ID"""

    def __init__(self) -> None:
        super().__init__("CONNECTION_ID")


class CurrentRole(Function):
    """Current role name"""

    def __init__(self) -> None:
        super().__init__("CURRENT_ROLE")


class CurrentUser(Function):
    """Username/host that authenticated the current client"""

    def __init__(self) -> None:
        super().__init__("CURRENT_USER")


class Database(Function):
    """Current default database"""

    def __init__(self) -> None:
        super().__init__("DATABASE")


class DecodeHistogram(Function):
    """Returns comma separated numerics corresponding to a probability distribution"""

    def __init__(self, hist_type: Any, histogram: Any) -> None:
        super().__init__("DECODE_HISTOGRAM", hist_type, histogram)


class Default(Function):
    """Returns the default value for a table column"""

    def __init__(self, column: Column) -> None:
        super().__init__("DEFAULT", column)


class FoundRows(Function):
    """Returns the number of (potentially) returned rows if there was no LIMIT involved."""

    def __init__(self) -> None:
        super().__init__("FOUND_ROWS")


class LastInsertId(Function):
    """Returns the value generated for an AUTO_INCREMENT column by the previous INSERT statement."""

    def __init__(self) -> None:
        super().__init__("LAST_INSERT_ID")


class LastValue(Function):
    """Evaluates expression and returns the last."""

    def __init__(self, expr: Statement, *exprs: Statement) -> None:
        super().__init__("LAST_VALUE", expr, *exprs)


class RowNumber(Function):
    """Returns the number of accepted rows so far."""

    def __init__(self) -> None:
        super().__init__("ROW_NUMBER")


class Schema(Function):
    """Current default schema"""

    def __init__(self) -> None:
        super().__init__("SCHEMA")


class SessionUser(Function):
    """Username/host that authenticated the current client"""

    def __init__(self) -> None:
        super().__init__("SESSION_USER")


class SystemUser(Function):
    """Username/host that authenticated the current client"""

    def __init__(self) -> None:
        super().__init__("SYSTEM_USER")


class User(Function):
    """Username/host that authenticated the current client"""

    def __init__(self) -> None:
        super().__init__("USER")


class Version(Function):
    """Database version"""

    def __init__(self) -> None:
        super().__init__("VERSION")
