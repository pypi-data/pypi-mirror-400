"""Simple binary comparison conditions."""

from typing import Any, TypeAlias

from sqlfactory.condition.base import ConditionBase, StatementOrColumn
from sqlfactory.statement import Statement


class SimpleCondition(ConditionBase):
    """
    Simple condition comparing one column with given value, using specified operator.

    **Note:** `SimpleCondition` and all other condition functions are expecting first argument to be column and second argument
    to be value. If you want to have column on the right side or value on the left, you must explicitely use `Column()` function.
    And if you want literal value on the left side, you must explicitely use `Value()` function.
    """

    def __init__(self, column: StatementOrColumn, operator: str, value: Statement | Any) -> None:
        # pylint: disable=duplicate-code   # It does not make sense to generalize two-row statement used on two places.
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param operator: Operator to use for comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        super().__init__()

        if not isinstance(column, Statement):
            # pylint: disable=import-outside-toplevel,cyclic-import
            from sqlfactory.entities import Column

            column = Column(column)

        self._column = column
        self._operator = operator
        self._value = value

    @property
    def args(self) -> list[Any]:
        args = [*self._column.args]

        if isinstance(self._value, Statement):
            args.extend(self._value.args)

        elif not isinstance(self._value, Statement):
            args.append(self._value)

        return args

    def __str__(self) -> str:
        if isinstance(self._value, Statement):
            return f"{self._column!s} {self._operator} {self._value!s}"

        return f"{self._column!s} {self._operator} {self.dialect.placeholder}"

    def __bool__(self) -> bool:
        return True


class Equals(SimpleCondition):
    """
    Equality condition (`==`). You can also use shorthand alias `Eq`.

    **Note:** First argument to `Equals` (or `Eq`) is expected to be column, while second argument is value. So to compare
    two columns, you must use `Column` instances as second argument (`Eq("column1", Column("column2"))` to produce
    ``` `column1` = `column2` ```). Likewise, to provide literal value as the first argument, you must use `Value` instance
    (`Eq(Value(10), "column")` to produce ``` %s = `column` ``` (with args `[10]`)).

    ```Eq("column1", "column2")``` produces ``` `column1` = %s ``` with arguments ```["column2"]```.

    You can also use column's operator overloading:

    ```python
    c = Column("column")
    c == "value"  # == Eq("column", "value")
    c == None     # == Eq("column", None)
    c == Now()    # == Eq("column", Now())
    ```

    Examples:

    - Simple comparison of column to value
        ```python
        # `column` = <value>
        Eq("column", "value")
        "`column` = %s", ["value"]
        ```
    - Comparison column to None
        ```python
        # `column` IS NULL
        Eq("column", None)
        "`column` IS NULL"
        ```
    - Comparison of generic statement to value
        ```python
        # <statement> = <value>
        Eq(Date(), "2021-01-01")
        "DATE() = %s", ["2021-01-01"]
        ```
    - Comparison of generic statement to None
        ```python
        # <statement> IS NULL
        Eq(Date(), None)
        "DATE() IS NULL"
        ```
    - Comparison of statement to statement
        ```python
        # <statement> = <statement>
        Eq(Date(), Now())
        # "DATE() = NOW()"
        ```
    """

    def __init__(self, column: StatementOrColumn, value: Any | None | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        if value is None:
            super().__init__(column, "IS", value)
        else:
            super().__init__(column, "=", value)


class NotEquals(SimpleCondition):
    """
    Not equality condition (`!=`). You can also use shorthand alis `Ne`.

    **Note:** First argument to `NotEquals` (or `Ne`) is expected to be column, while second argument is value. So to compare
    two columns, you must use `Column` instances as second argument (`Ne("column1", Column("column2"))` to produce
    ``` `column1` != `column2` ```). Likewise, to provide literal value as the first argument, you must use `Value` instance
    (`Ne(Value(10), "column")` to produce ``` %s != `column` ``` (with args `[10]`)).

    ```Ne("column1", "column2")``` produces ``` `column1` != %s ``` with arguments ```["column2"]```.

    You can also use column's operator overloading:

    ```python
    c = Column("column")
    c != "value"  # == Ne("column", "value")
    c != None     # == Ne("column", None)
    c != Now()    # == Ne("column", Now())
    ```

    Examples:

    - Column not equals value
        ```python
        # `column` != <value>
        Ne("column", "value")
        "`column` != %s", ["value"]
        ```
    - Statement not equals value
        ```python
        # <statement> != <value>
        Ne(Date(), "2021-01-01")
        "DATE() != %s", ["2021-01-01"]
        ```
    - Column is not None
        ```python
        # `column` IS NOT NULL
        Ne("column", None)
        "`column` IS NOT NULL"
        ```
    - Statement is not None
        ```python
        # <statement> IS NOT NULL
        Ne(Date(), None)
        "DATE() IS NOT NULL"
        ```
    - Statement not equals statement
        ```python
        # <statement> != <statement>
        Ne(Date(), Now())
        "DATE() != NOW()"
        ```
    """

    def __init__(self, column: StatementOrColumn, value: Any | None | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        if value is None:
            super().__init__(column, "IS NOT", value)
        else:
            super().__init__(column, "!=", value)


class GreaterThanOrEquals(SimpleCondition):
    """
    Greater than or equal condition (`>=`). You can also use shorthand alis `Ge`.

    **Note:** First argument to `GreaterThanOrEquals` (or `Ge`) is expected to be column, while second argument is value.
    So to compare two columns, you must use `Column` instances as second argument (`Ge("column1", Column("column2"))` to produce
    ``` `column1` >= `column2` ```). Likewise, to provide literal value as the first argument, you must use `Value` instance
    (`Ge(Value(10), "column")` to produce ``` %s >= `column` ``` (with args `[10]`)).

    ```Ge("column1", "column2")``` produces ``` `column1` >= %s ``` with arguments ```["column2"]```.

    You can also use column's operator overloading:

    ```python
    c = Column("column")
    c >= "value"  # == Ge("column", "value")
    c >= None     # == Ge("column", None)
    c >= Now()    # == Ge("column", Now())
    ```

    Examples:

    - Column is greater or equals to value:
        ```python
        # `column` >= <value>
        Ge("column", 10)
        "`column` >= %s", [10]
        ```
    - Statement is greater or equals to value:
        ```python
        # <statement> >= <value>
        Ge(Date(), "2021-01-01")
        "DATE() >= %s", ["2021-01-01"]
        ```
    - Column is greater or equals to other column
        ```python
        # `column1` >= `column2`
        Ge("column1", Column("column2"))
        "`column1` >= `column2`"
        ```
    - Column is greater or equals to statement
        ```python
        # `column` >= <statement>
        Ge("column", Now())
        "`column` >= NOW()"
        ```
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        super().__init__(column, ">=", value)


class GreaterThan(SimpleCondition):
    """
    Greater than condition (`>`). You can also use shorthand alis `Gt`.

    **Note:** First argument to `GreaterThan` (or `Ge`) is expected to be column, while second argument is value.
    So to compare two columns, you must use `Column` instances as second argument (`Gt("column1", Column("column2"))` to produce
    ``` `column1` > `column2` ```). Likewise, to provide literal value as the first argument, you must use `Value` instance
    (`Gt(Value(10), "column")` to produce ``` %s > `column` ``` (with args `[10]`)).

    ```Gt("column1", "column2")``` produces ``` `column1` > %s ``` with arguments ```["column2"]```.

    You can also use column's operator overloading:

    ```python
    c = Column("column")
    c > "value"  # == Gt("column", "value")
    c > None     # == Gt("column", None)
    c > Now()    # == Gt("column", Now())
    ```

    Examples:

    - Column is greater than value:
        ```python
        # `column` > <value>
        Gt("column", 10)
        "`column` > %s, [10]
        ```
    - Statement is greater than value:
        ```python
        # <statement> > <value>
        Gt(Date(), "2021-01-01")
        "DATE() > %s", ["2021-01-01"]
        ```
    - Column is greater than other column
        ```python
        # `column1` > `column2`
        Gt("column1", Column("column2"))
        "`column1` > `column2`"
        ```
    - Column is greater than statement
        ```python
        # `column` > <statement>
        Gt("column", Now())
        "`column` > NOW()"
        ```
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        super().__init__(column, ">", value)


class LessThanOrEquals(SimpleCondition):
    """
    Less than or equal condition (`<=`). You can also use shorthand alis `Le`.

    **Note:** First argument to `LessThanOrEquals` (or `Le`) is expected to be column, while second argument is value.
    So to compare two columns, you must use `Column` instances as second argument (`Le("column1", Column("column2"))` to produce
    ``` `column1` <= `column2` ```). Likewise, to provide literal value as the first argument, you must use `Value` instance
    (`Le(Value(10), "column")` to produce ``` %s <= `column` ``` (with args `[10]`)).

    ```Le("column1", "column2")``` produces ``` `column1` <= %s ``` with arguments ```["column2"]```.

    You can also use column's operator overloading:

    ```python
    c = Column("column")
    c <= "value"  # == Le("column", "value")
    c <= None     # == Le("column", None)
    c <= Now()    # == Le("column", Now())
    ```

    Examples:

    - Column is lower or equal to value:
        ```python
        # `column` <= <value>
        Le("column", 10)
        "`column` <= %s", [10]
        ```
    - Statement is lower or equal to value
        ```python
        <statement> <= <value>
        Le(Date(), "2021-01-01")
        "DATE() <= %s", ["2021-01-01"]
        ```
    - Column is lower or equal to other column
        ```python
        # `column1` <= `column2`
        Le("column1", Column("column2"))
        "`column1` <= `column2`"
        ```
    - Column is lower or equal to statement
        ```python
        # `column` <= <statement>
        Le("column", Now())
        "`column` <= NOW()"
        ```
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        super().__init__(column, "<=", value)


class LessThan(SimpleCondition):
    """
    Less than condition (`<`). You can also use shorthand alis `Lt`.

    **Note:** First argument to `LessThan` (or `Lt`) is expected to be column, while second argument is value.
    So to compare two columns, you must use `Column` instances as second argument (`Lt("column1", Column("column2"))` to produce
    ``` `column1` < `column2` ```). Likewise, to provide literal value as the first argument, you must use `Value` instance
    (`Lt(Value(10), "column")` to produce ``` %s < `column` ``` (with args `[10]`)).

    ```Lt("column1", "column2")``` produces ``` `column1` < %s ``` with arguments ```["column2"]```.

    You can also use column's operator overloading:

    ```python
    c = Column("column")
    c < "value"  # == Lt("column", "value")
    c < None     # == Lt("column", None)
    c < Now()    # == Lt("column", Now())
    ```

    Examples:

    - Column is lower than value:
        ```python
        # `column` < <value>
        Lt("column", 10)
        "`column` < %s", [10]
        ```
    - Statement is lower than value:
        ```python
        # <statement> < <value>
        Lt(Date(), "2021-01-01")
        "DATE() < %s", ["2021-01-01"]
        ```
    - Column is lower than other column
        ```python
        # `column1` < `column2`
        Lt("column1", Column("column2"))
        "`column1` < `column2`"
        ```
    - Column is lower than statement
        ```python
        # `column` < <statement>
        Lt("column", Now())
        "`column` < NOW()"
        ```
    """

    def __init__(self, column: StatementOrColumn, value: Any | Statement) -> None:
        """
        :param column: Column to compare (string or instance of Column) or Statement to use on left side of comparison.
        :param value: Value to compare column value to (or statement to use on right side of comparison).
        """
        super().__init__(column, "<", value)


# Convenient aliases for shorter code.
Eq: TypeAlias = Equals
Ge: TypeAlias = GreaterThanOrEquals
Gt: TypeAlias = GreaterThan
Le: TypeAlias = LessThanOrEquals
Lt: TypeAlias = LessThan
Ne: TypeAlias = NotEquals
