"""Base classes to implement SQL conditions."""

from __future__ import annotations

from abc import ABC
from collections.abc import Iterable
from typing import Any, Self, overload

from sqlfactory.statement import ConditionalStatement, Raw, Statement

StatementOrColumn = str | Statement


class ConditionBase(Statement, ConditionalStatement, ABC):
    """
    Generic condition interface, that can be chained with other conditions using `&` or `|` operators. All condition
    classes should inherit from this one, as there are checks through the library for instances of this class.

    For example:

    >>> Gt("id", 1) & Lt("id", 10)
    >>> "(`id` > 1 AND `id` < 10)"

    >>> Lt("id", 1) | Gt("id", 10)
    >>> "(`id` < 1 OR `id` > 10)"

    Conditions can of course be chained:

    >>> Eq("id", 1) & Eq("user_id", 10) & Eq("parent_id", None)
    >>> "(`id` = 1 AND `user_id` = 10 AND `parent_id` IS NULL)"

    >>> Eq("id", 1) | Eq("user_id", 10) | Eq("parent_id", None)
    >>> "(`id` = 1 OR `user_id` = 10 OR `parent_id` IS NULL)"

    or combined together:

    >>> Eq("id", 1) & (Eq("user_id", 10) | Eq("parent_id", None))
    >>> "(`id` = 1 AND (`user_id` = 10 OR `parent_id` IS NULL))"
    """

    def __and__(self, other: ConditionBase) -> And:
        """
        Constructs AND compound condition containing this and the other conditions. It can be chained to produce multiple
        conditions joined by AND operator.

        >>> Eq("id", 1) & Eq("user_id", 10) & Eq("parent_id", None)
        >>> "(`id` = 1 AND `user_id` = 10 AND `parent_id` IS NULL)"

        :param other: Other condition to be concatenated with this one.
        """
        if isinstance(self, And):
            out = self
        else:
            out = And(self)

        if isinstance(other, And):
            out.extend(other.sub_conditions)
        else:
            out.append(other)

        return out

    def __or__(self, other: ConditionBase) -> Or:
        """
        Constructs OR compound condition containing this and the other conditions. It can be chained to produce multiple
        conditions joined by AND operator.

        >>> Eq("id", 1) | Eq("user_id", 10) | Eq("parent_id", None)
        >>> "(`id` = 1 OR `user_id` = 10 OR `parent_id` IS NULL)"

        :param other: Other condition to be concatenated with this one.
        """

        if isinstance(self, Or):
            out = self
        else:
            out = Or(self)

        if isinstance(other, Or):
            out.extend(other.sub_conditions)
        else:
            out.append(other)

        return out


class Condition(ConditionBase):
    """
    Generic RAW condition with optional arguments. You probably don't want to use this class directly, instead, try to
    construct conditions using more specific classes, such as Eq, Gt, In, Between, etc.

    Usage:

    >>> Select("id", table="table", where=Eq("id", 1))
    >>> Update("table").set("name", "hello").where(Eq("id", 1))

    >>> Gt("id", 1) & Lt("id", 10)
    >>> "(`id` > 1 AND `id` < 10)"

    """

    def __init__(self, condition: str, *args: Any):
        """
        :param condition: Condition with placeholders (such as "`column` = %s")
        :param args: Optional arguments used in condition.
        """

        super().__init__()

        self.condition = condition
        """Condition with placeholders."""

        self._args = list(args)

    def __str__(self) -> str:
        return self.condition

    @property
    def args(self) -> list[Any]:
        """Argument values of the condition statement."""
        return self._args

    def __bool__(self) -> bool:
        return bool(self.condition)


class CompoundCondition(ConditionBase):
    """
    Base class for joining multiple conditions together using specified operator. As there are only two operators
    (AND and OR), this class is not meant to be used directly, but rather through And and Or classes.
    """

    def __init__(self, operator: str, *conditions: ConditionBase | Raw | str) -> None:
        """
        :param operator: Which operator to use for joining specific conditions.
        :param conditions: Conditions to join using given operator.
        """
        super().__init__()

        self.operator = operator
        self._sub_conditions: list[ConditionBase | Raw] = [
            Condition(condition) if isinstance(condition, str) else condition for condition in conditions
        ]

    @overload
    def append(self, condition: ConditionBase | Raw) -> Self:
        """Append another condition to the list of conditions."""

    @overload
    def append(self, condition: str, *args: Any) -> Self:
        """Append another condition to the list of conditions."""

    def append(self, condition: ConditionBase | Raw | str, *args: Any) -> Self:
        """
        Append another condition to be joined.
        :param condition: Condition to append
        :param args: Optional arguments for given condition, if condition is passed as string.
        """
        if isinstance(condition, str):
            condition = Condition(condition, *args)
        elif args:
            raise AttributeError("*args can be used only for str conditions.")

        self._sub_conditions.append(condition)
        return self

    def extend(self, conditions: Iterable[ConditionBase | Raw]) -> Self:
        """
        Extend condition with list of conditions.
        :param conditions: Conditions to extend this condition with
        """
        self._sub_conditions.extend(conditions)
        return self

    @property
    def sub_conditions(self) -> list[ConditionBase | Raw]:
        """
        Return filtered list of conditions, which are valid.
        """
        return list(filter(bool, self._sub_conditions))

    def __str__(self) -> str:
        """
        Create SQL statement of joined conditions.
        """
        sub_conditions = list(map(str, self.sub_conditions))
        if sub_conditions:
            return "(" + f" {self.operator} ".join(sub_conditions) + ")" if len(sub_conditions) > 1 else sub_conditions[0]

        return "TRUE"

    @property
    def args(self) -> list[Any]:
        """
        Return arguments from all sub conditions in correct order.
        """
        out = []

        for cond in self.sub_conditions:
            out.extend(cond.args)

        return out

    def __bool__(self) -> bool:
        """
        Is this compound condition non-empty?
        """
        return bool(self.sub_conditions)


class And(CompoundCondition):
    """
    Compound condition joined by AND.

    Usage:

    >>> And(Equals("id", 1), Equals("name", "hello"))
    >>> "(`id` = 1 AND `name` = 'hello')"

    Of course, condition can be another compound condition:

    >>> And(Equals("id", 1), Or(Equals("name", "hello"), Equals("name", "world")))
    >>> "(`id` = 1 AND (`name` = 'hello' OR `name` = 'world'))"
    """

    def __init__(self, *conditions: ConditionBase | str) -> None:
        """
        :param conditions: Conditions that should be joined using AND operator.
        """
        super().__init__("AND", *conditions)


class Or(CompoundCondition):
    """
    Compound condition joined by OR.

    Usage:

    >>> Or(Equals("id", 1), Equals("name", "hello"))
    >>> "(`id` = 1 OR `name` = 'hello')"

    Of course, condition can be another compound condition:

    >>> Or(Equals("id", 1), And(Equals("name", "hello"), Equals("name", "world")))
    >>> "(`id` = 1 OR (`name` = 'hello' AND `name` = 'world'))"
    """

    def __init__(self, *conditions: ConditionBase | str) -> None:
        """
        :param conditions: Conditions that should be joined using OR operator.
        """
        super().__init__("OR", *conditions)

    def __str__(self) -> str:
        """
        Create SQL statement of joined conditions.
        """
        if not self.sub_conditions:
            return "FALSE"

        return super().__str__()
