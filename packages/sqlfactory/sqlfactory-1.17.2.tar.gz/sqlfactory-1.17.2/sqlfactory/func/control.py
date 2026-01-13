"""Control flow functions"""

from typing import Any

from sqlfactory.func.base import Function
from sqlfactory.statement import Statement


class IfNull(Function):
    """If expr1 is not NULL, IFNULL() returns expr1; otherwise it returns expr2."""

    def __init__(self, expr1: Statement | Any, expr2: Statement | Any) -> None:
        super().__init__("IFNULL", expr1, expr2)


class NullIf(Function):
    """Returns NULL if expr1 = expr2 is true, otherwise returns expr1."""

    def __init__(self, expr1: Statement | Any, expr2: Statement | Any) -> None:
        super().__init__("NULLIF", expr1, expr2)


class If(Function):
    """If expr1 is TRUE (expr1 <> 0 and expr1 <> NULL) then IF() returns expr2; otherwise it returns expr3."""

    def __init__(self, expr: Statement | Any, if_true: Statement | Any, if_false: Statement | Any) -> None:
        super().__init__("IF", expr, if_true, if_false)


class Coalesce(Function):
    """Returns first non-NULL parameter."""

    def __init__(self, expr: Statement | Any, *args: Statement | Any) -> None:
        super().__init__("COALESCE", expr, *args)
