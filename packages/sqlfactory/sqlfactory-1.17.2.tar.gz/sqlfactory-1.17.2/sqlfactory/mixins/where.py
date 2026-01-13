"""WHERE mixin for query generator."""

from __future__ import annotations

from typing import Any, Self

from sqlfactory.condition.base import And, ConditionBase


class WithWhere:
    """
    Mixin to provide `WHERE` support for query generator.

    Example:

    >>> from sqlfactory import Select, And, Equals
    >>> Select(where=And(Equals("id", 1), Equals("status", "active")))

    >>> from sqlfactory import Update, And, Equals
    >>> Update(where=And(Equals("id", 1), Equals("status", "active")))

    >>> from sqlfactory import Delete, And, Equals
    >>> Delete(where=And(Equals("id", 1), Equals("status", "active")))

    """

    def __init__(self, *args: Any, where: ConditionBase | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._where = where

    def where(self, condition: ConditionBase) -> Self:
        """
        Set `WHERE` condition for query. If you chain multiple where calls together, they are joined by `And` condition.
        You can manually specify joining condition by use one of `sqlfactory.And` or `sqlfactory.Or` compound classes to chain
        multiple conditions.

        Example:

        >>> from sqlfactory import Select, And, Equals
        >>> sel = Select().where(And(Equals("id", 1), Equals("status", "active")))

        **Note:** `Eq()` and all other condition functions are expecting first argument to be column and second argument to be
        value. If you want to have column on the right side or value on the left, you must explicitely use `Column()` function.
        And if you want literal value on the left side, you must explicitely use `Value()` function.

        :param condition: Condition to be used in WHERE clause.
        """
        if self._where is not None:
            if isinstance(self._where, And):
                self._where.append(condition)
            else:
                self._where = And(self._where, condition)
        else:
            self._where = condition

        return self

    def WHERE(self, condition: ConditionBase) -> Self:  # pylint: disable=invalid-name
        """Alias for `WithWhere.where()` to be more SQL-like with all capitals."""
        return self.where(condition)
