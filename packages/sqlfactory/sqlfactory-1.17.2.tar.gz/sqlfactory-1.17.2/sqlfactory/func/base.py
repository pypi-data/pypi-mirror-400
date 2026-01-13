"""Base classes for SQL functions"""

from typing import Any

from sqlfactory.entities import Expression
from sqlfactory.statement import Statement


class Function(Expression):
    """Generic function with name and variable number of arguments."""

    def __init__(self, function: str, *args: Statement | Any) -> None:
        super().__init__()

        self.function = function
        self._args = args

    def _args_placeholders(self) -> list[str]:
        out: list[str] = []

        for arg in self._args:
            if isinstance(arg, Statement):
                out.append(str(arg))
            else:
                out.append(self.dialect.placeholder)

        return out

    def __str__(self) -> str:
        return f"{self.function}({', '.join(self._args_placeholders())})"

    @property
    def args(self) -> list[Any]:
        out = []
        for arg in self._args:
            if isinstance(arg, Statement):
                out.extend(arg.args)
            elif not isinstance(arg, Statement):
                out.append(arg)

        return out
