"""LIMIT statement"""

from __future__ import annotations

from typing import Any, Self, overload

from sqlfactory.statement import ConditionalStatement, Statement


class Limit(ConditionalStatement, Statement):
    """
    `LIMIT` statement

    Examples:

    ```python
    Limit()                   # => No LIMIT statement
    Limit(10)                 # => LIMIT 10
    Limit(5, 10)              # => LIMIT 5, 10
    Limit(offset=3)           # AttributeError, offset cannot be used without limit.
    Limit(offset=3, limit=5)  # => LIMIT 3, 5
    ```
    """

    @overload
    def __init__(self) -> None:
        """No LIMIT statement"""

    @overload
    def __init__(self, limit: int, /) -> None:
        """
        Just a LIMIT statement without offset
        :param limit: Number of returned rows
        """

    @overload
    def __init__(self, /, offset: int | None, limit: int | None) -> None:
        """
        LIMIT statement with both offset and limit
        :param offset: Pagination offset (how many rows to skip before returning result)
        :param limit: Number of returned rows
        """

    def __init__(  # type: ignore[misc]
        self, offset_or_limit: int | None = None, /, limit: int | None = None, *, offset: int | None = None
    ) -> None:
        """
        LIMIT statement
        :param offset_or_limit: Pagination offset, or limit if second argument is None. Only as positional argument.
        :param limit: Number of returned rows.
        :param offset: Optional keyword argument for specifying offset.
        """

        super().__init__()

        if offset_or_limit is not None and offset is not None and limit is not None:
            raise AttributeError("Unable to specify both positional argument offset and keyword argument offset.")

        if offset is not None and offset_or_limit is None and limit is None:
            raise AttributeError("Cannot use only offset without limit.")

        if limit is None:
            limit = offset_or_limit
            offset_or_limit = offset

        if offset is not None:
            offset_or_limit = offset

        self.offset = offset_or_limit
        """Specified pagination offset"""

        self.limit = limit
        """Specified number of returned rows"""

    def __str__(self) -> str:
        if self.offset is not None:
            return f"LIMIT {self.dialect.placeholder}, {self.dialect.placeholder}"

        if self.limit is not None:
            return f"LIMIT {self.dialect.placeholder}"

        return ""

    def __bool__(self) -> bool:
        """Return True if statement should be included in query, False otherwise."""
        return self.offset is not None or self.limit is not None

    @property
    def args(self) -> list[int]:
        """Argument values of the limit statement"""
        if self.offset is not None and self.limit is not None:
            return [self.offset, self.limit]

        if self.limit is not None:
            return [self.limit]

        return []


class WithLimit:
    """
    Mixin to provide LIMIT support for query generator.

    Usage:

    >>> Select().limit(10)  # SELECT ... LIMIT 10
    >>> Select().limit(5, 10)  # SELECT ... LIMIT 5, 10
    >>> Select().limit(limit=10, offset=5)  # SELECT ... LIMIT 5,10
    >>> Select().limit(Limit(...))
    >>> Select(..., limit=Limit(...))

    """

    def __init__(self, *args: Any, limit: Limit | None = None, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._limit = limit

    @overload
    def limit(self, limit: Limit | None, /) -> Self:
        """
        Limit statement
        :param limit: Instance of Limit
        """

    @overload
    def limit(self, limit: int | None, /) -> Self:
        """
        Limit statement
        :param limit: Number of returned rows
        """

    @overload
    def limit(self, offset: int | None, limit: int | None) -> Self:
        """
        Limit statement
        :param offset: Pagination offset (how many rows to skip before returning result)
        :param limit: Number of returned rows
        """

    def limit(  # type: ignore[misc]
        self, offset_or_limit: int | Limit | None = None, /, limit: int | None = None, *, offset: int | None = None
    ) -> Self:
        """
        Limit statement

        Usage:

        >>> Select(...).limit(10)  # SELECT ... LIMIT 10
        >>> Select(...).limit(5, 10)
        >>> Select(...).limit(limit=10, offset=5)
        >>> Select(...).limit(Limit(...))

        :param offset_or_limit: Positional-only argument as first argument to the LIMIT SQL statement. Can also be instance
            of `Limit`.

            If there is no `limit` argument, the first argument will be used as limit. If there is `limit` argument,
            the first argument will be used as offset. This weird behavior is to mimic SQL's LIMIT syntax.

        :param limit: Limit argument, can be passed as kwarg or as second positional argument.
        :param offset: Keyword-only argument to explicitly specify offset.
        """
        if self._limit is not None:
            raise AttributeError("Limit has already been specified.")

        if isinstance(offset_or_limit, Limit):
            self._limit = offset_or_limit

            if limit is not None or offset is not None:
                raise AttributeError("When passing Limit instance as first argument, second argument should not be passed.")

        else:
            if offset_or_limit is not None:
                if offset is not None:
                    raise AttributeError("Unable to specify both positional argument offset and keyword argument offset.")

                self._limit = Limit(offset_or_limit, limit)

            else:
                self._limit = Limit(offset=offset, limit=limit)

        return self

    @overload
    def LIMIT(self, limit: Limit | None, /) -> Self:
        # pylint: disable=invalid-name
        """Alias for `WithLimit.limit()` to be more SQL-like with all capitals."""

    @overload
    def LIMIT(self, limit: int | None, /) -> Self:
        # pylint: disable=invalid-name
        """Alias for `WithLimit.limit()` to be more SQL-like with all capitals."""

    @overload
    def LIMIT(self, offset: int | None, limit: int | None) -> Self:
        # pylint: disable=invalid-name
        """Alias for `WithLimit.limit()` to be more SQL-like with all capitals."""

    def LIMIT(  # type: ignore[misc]
        self, offset_or_limit: int | Limit | None, /, limit: int | None = None, *, offset: int | None = None
    ) -> Self:
        # pylint: disable=invalid-name
        """Alias for `WithLimit.limit()` to be more SQL-like with all capitals."""
        return self.limit(offset_or_limit, limit, offset=offset)  # type: ignore[call-overload]
