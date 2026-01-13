"""Numeric SQL functions (https://mariadb.com/kb/en/numeric-functions/)"""

from typing import Any, overload

from sqlfactory.func.base import Function


class Div(Function):
    """
    Integer division.
    """

    def __init__(self, dividend: Any, divisor: Any) -> None:
        super().__init__("DIV", dividend, divisor)


class Abs(Function):
    """
    Absolute value.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("ABS", value)


class ACos(Function):
    """
    Arc cosine.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("ACOS", value)


class ASin(Function):
    """
    Arc sine.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("ASIN", value)


class ATan(Function):
    """
    Arc tangent.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("ATAN", value)


class ATan2(Function):
    """
    Arc tangent of two variables.
    """

    def __init__(self, y: Any, x: Any) -> None:
        super().__init__("ATAN2", y, x)


class Ceil(Function):
    """
    Ceiling value.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("CEIL", value)


class Ceiling(Function):
    """
    Ceiling value.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("CEILING", value)


class Conv(Function):
    """
    Convert number from one base to another.
    """

    def __init__(self, number: Any, from_base: Any, to_base: Any) -> None:
        super().__init__("CONV", number, from_base, to_base)


class Cos(Function):
    """
    Cosine.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("COS", value)


class Cot(Function):
    """
    Cotangent.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("COT", value)


class Crc32(Function):
    """
    Computes a cyclic redundancy check (CRC) value.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("CRC32", value)


class Crc32C(Function):
    """
    Computes a cyclic redundancy check (CRC) value using the Castagnoli polynomial
    """

    def __init__(self, value: Any) -> None:
        super().__init__("CRC32C", value)


class Degrees(Function):
    """
    Converts radians to degrees.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("DEGREES", value)


class Exp(Function):
    """
    e raised to power of the argument
    """

    def __init__(self, value: Any) -> None:
        super().__init__("EXP", value)


class Floor(Function):
    """
    Floor value.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("FLOOR", value)


class Greatest(Function):
    """
    Return the largest argument
    """

    def __init__(self, *args: Any) -> None:
        super().__init__("GREATEST", *args)


class Least(Function):
    """
    Return the smallest argument
    """

    def __init__(self, *args: Any) -> None:
        super().__init__("LEAST", *args)


class Ln(Function):
    """
    Natural logarithm
    """

    def __init__(self, value: Any) -> None:
        super().__init__("LN", value)


class Log(Function):
    """
    Logarithm
    """

    @overload
    def __init__(self, value: Any, /) -> None: ...

    @overload
    def __init__(self, base: Any, value: Any, /) -> None: ...

    def __init__(self, arg1: Any, arg2: Any = None) -> None:
        if arg2 is not None:
            super().__init__("LOG", arg1, arg2)

        else:
            super().__init__("LOG", arg1)


class Log10(Function):
    """
    Base-10 logarithm
    """

    def __init__(self, value: Any) -> None:
        super().__init__("LOG10", value)


class Log2(Function):
    """
    Base-2 logarithm
    """

    def __init__(self, value: Any) -> None:
        super().__init__("LOG2", value)


class Mod(Function):
    """
    Modulo operation
    """

    def __init__(self, dividend: Any, divisor: Any) -> None:
        super().__init__("MOD", dividend, divisor)


class Oct(Function):
    """
    Convert number to octal
    """

    def __init__(self, value: Any) -> None:
        super().__init__("OCT", value)


class Pi(Function):
    """
    Return the value of pi
    """

    def __init__(self) -> None:
        super().__init__("PI")


class Pow(Function):
    """
    Return X raised to power of Y.
    """

    def __init__(self, x: Any, y: Any) -> None:
        super().__init__("POW", x, y)


class Power(Function):
    """
    Return X raised to power of Y.
    """

    def __init__(self, x: Any, y: Any) -> None:
        super().__init__("POWER", x, y)


class Radians(Function):
    """
    Converts degrees to radians.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("RADIANS", value)


class Rand(Function):
    """
    Return a random floating-point value.
    """

    def __init__(self) -> None:
        super().__init__("RAND")


class Round(Function):
    """
    Round the argument to the nearest integer.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("ROUND", value)


class Sign(Function):
    """
    Sign of the argument
    """

    def __init__(self, value: Any) -> None:
        super().__init__("SIGN", value)


class Sin(Function):
    """
    Sine
    """

    def __init__(self, value: Any) -> None:
        super().__init__("SIN", value)


class Sqrt(Function):
    """
    Square root
    """

    def __init__(self, value: Any) -> None:
        super().__init__("SQRT", value)


class Tan(Function):
    """
    Tangent
    """

    def __init__(self, value: Any) -> None:
        super().__init__("TAN", value)


class Truncate(Function):
    """
    Truncate the argument to D decimal places.
    """

    def __init__(self, value: Any, d: Any) -> None:
        super().__init__("TRUNCATE", value, d)


class BitCount(Function):
    """
    Return the number of bits that are set in the argument.
    """

    def __init__(self, value: Any) -> None:
        super().__init__("BIT_COUNT", value)
