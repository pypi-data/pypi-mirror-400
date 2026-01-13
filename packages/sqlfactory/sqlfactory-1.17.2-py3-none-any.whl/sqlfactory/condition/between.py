"""BETWEEN condition generator"""

from typing import Any, NoReturn

from sqlfactory.condition.base import ConditionBase, StatementOrColumn
from sqlfactory.entities import Column
from sqlfactory.statement import Statement


class Between(ConditionBase):
    # pylint: disable=duplicate-code  # It does not make sense to generalize two-row statement used on two places.
    """
    Provides generation for following syntax:

    - ``` `column` BETWEEN <lower_bound> AND <upper_bound>```
    - ``` `column` NOT BETWEEN <lower_bound> AND <upper_bound>```
    - ```<statement> BETWEEN <lower_bound> AND <upper_bound>```
    - ```<statement> NOT BETWEEN <lower_bound> AND <upper_bound>```

    Usage:

    >>> Between('column', 1, 10)
    >>> "`column` BETWEEN 1 AND 10"

    >>> Between('column', 1, 10, negative=True)
    >>> "`column` NOT BETWEEN 1 AND 10"

    >>> Between(Column('c1') + Column('c2'), 1, 10)
    >>> "(`c1` + `c2`) BETWEEN 1 AND 10"

    >>> Between(Column('c1') + Column('c2'), Column('c3') + Column('c4'), Column('c5') + Column('c6'))
    >>> "(`c1` + `c2`) BETWEEN (`c3` + `c4`) AND (`c5` + `c6`)"

    """

    def __init__(
        self, column: StatementOrColumn, lower_bound: Any | Statement, upper_bound: Any | Statement, *, negative: bool = False
    ) -> None:
        """
        :param column: Column to be compared.
        :param lower_bound: Lower inclusive bound of matching value
        :param upper_bound: Upper inclusive bound of matching value
        :param negative: Whether to negate the condition.
        """
        super().__init__()

        if not isinstance(column, Statement):
            column = Column(column)

        self._column = column
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound
        self._negative = negative

    def __str__(self) -> str:
        lower_bound_s = self.dialect.placeholder
        upper_bound_s = self.dialect.placeholder

        if isinstance(self._lower_bound, Statement):
            lower_bound_s = str(self._lower_bound)

        if isinstance(self._upper_bound, Statement):
            upper_bound_s = str(self._upper_bound)

        return f"{self._column!s} {'NOT ' if self._negative else ''}BETWEEN {lower_bound_s} AND {upper_bound_s}"

    @property
    def args(self) -> list[Any]:
        """
        Return argument values of the condition.
        """

        args = []

        if isinstance(self._column, Statement):
            args.extend(self._column.args)

        if isinstance(self._lower_bound, Statement):
            args.extend(self._lower_bound.args)
        else:
            args.append(self._lower_bound)

        if isinstance(self._upper_bound, Statement):
            args.extend(self._upper_bound.args)
        else:
            args.append(self._upper_bound)

        return args

    def __bool__(self) -> bool:
        return True

    def __invert__(self) -> "Between":
        """
        Allows using the `~` operator to negate the BETWEEN condition, converting it to a NOT BETWEEN condition.
        Note: Cannot use ~ operator on NotBetween conditions.
        """
        return NotBetween(self._column, self._lower_bound, self._upper_bound)


class NotBetween(Between):
    """
    Provides generation for following syntax:

    - ``` `column` NOT BETWEEN <lower_bound> AND <upper_bound>```
    - ```<statement> NOT BETWEEN <lower_bound> AND <upper_bound>```

    This is a dedicated class for NOT BETWEEN conditions, which is equivalent to using Between with negative=True.
    It provides a more intuitive API for NOT BETWEEN conditions.

    Usage:

    >>> NotBetween('column', 1, 10)
    >>> "`column` NOT BETWEEN 1 AND 10"

    >>> NotBetween(Column('c1') + Column('c2'), 1, 10)
    >>> "(`c1` + `c2`) NOT BETWEEN 1 AND 10"

    >>> NotBetween(Column('c1') + Column('c2'), Column('c3') + Column('c4'), Column('c5') + Column('c6'))
    >>> "(`c1` + `c2`) NOT BETWEEN (`c3` + `c4`) AND (`c5` + `c6`)"
    """

    def __init__(self, column: StatementOrColumn, lower_bound: Any | Statement, upper_bound: Any | Statement) -> None:
        """
        :param column: Column to be compared.
        :param lower_bound: Lower inclusive bound of matching value
        :param upper_bound: Upper inclusive bound of matching value
        """
        super().__init__(column, lower_bound, upper_bound, negative=True)

    def __invert__(self) -> NoReturn:
        """
        Allows using the `~` operator to negate the BETWEEN condition, converting it to a NOT BETWEEN condition.
        Note: Cannot use ~ operator on NotBetween conditions.
        """
        raise TypeError("Cannot use ~ operator on NotBetween conditions")
