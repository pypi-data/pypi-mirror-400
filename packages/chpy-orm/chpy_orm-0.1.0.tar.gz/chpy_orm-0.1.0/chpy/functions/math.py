"""
Mathematical functions for ClickHouse.
"""

from typing import Union
from chpy.orm import Column
from chpy.functions.base import Function


def e() -> Function:
    """Returns Euler's number."""
    return Function("e")


def pi() -> Function:
    """Returns pi."""
    return Function("pi")


def exp(x: Union[Column, float]) -> Function:
    """Returns e^x."""
    return Function("exp", x)


def log(x: Union[Column, float]) -> Function:
    """Returns natural logarithm."""
    return Function("log", x)


def log2(x: Union[Column, float]) -> Function:
    """Returns base-2 logarithm."""
    return Function("log2", x)


def log10(x: Union[Column, float]) -> Function:
    """Returns base-10 logarithm."""
    return Function("log10", x)


def sqrt(x: Union[Column, float]) -> Function:
    """Returns square root."""
    return Function("sqrt", x)


def cbrt(x: Union[Column, float]) -> Function:
    """Returns cube root."""
    return Function("cbrt", x)


def pow(x: Union[Column, float], y: Union[Column, float]) -> Function:
    """Returns x^y."""
    return Function("pow", x, y)


def power(x: Union[Column, float], y: Union[Column, float]) -> Function:
    """Returns x^y (alias for pow)."""
    return Function("power", x, y)


def exp2(x: Union[Column, float]) -> Function:
    """Returns 2^x."""
    return Function("exp2", x)


def exp10(x: Union[Column, float]) -> Function:
    """Returns 10^x."""
    return Function("exp10", x)


def log1p(x: Union[Column, float]) -> Function:
    """Returns ln(1+x)."""
    return Function("log1p", x)


def sign(x: Union[Column, float]) -> Function:
    """Returns sign of x."""
    return Function("sign", x)


def sin(x: Union[Column, float]) -> Function:
    """Returns sine."""
    return Function("sin", x)


def cos(x: Union[Column, float]) -> Function:
    """Returns cosine."""
    return Function("cos", x)


def tan(x: Union[Column, float]) -> Function:
    """Returns tangent."""
    return Function("tan", x)


def asin(x: Union[Column, float]) -> Function:
    """Returns arcsine."""
    return Function("asin", x)


def acos(x: Union[Column, float]) -> Function:
    """Returns arccosine."""
    return Function("acos", x)


def atan(x: Union[Column, float]) -> Function:
    """Returns arctangent."""
    return Function("atan", x)


def atan2(y: Union[Column, float], x: Union[Column, float]) -> Function:
    """Returns arctangent of y/x."""
    return Function("atan2", y, x)


def sinh(x: Union[Column, float]) -> Function:
    """Returns hyperbolic sine."""
    return Function("sinh", x)


def cosh(x: Union[Column, float]) -> Function:
    """Returns hyperbolic cosine."""
    return Function("cosh", x)


def tanh(x: Union[Column, float]) -> Function:
    """Returns hyperbolic tangent."""
    return Function("tanh", x)


def asinh(x: Union[Column, float]) -> Function:
    """Returns inverse hyperbolic sine."""
    return Function("asinh", x)


def acosh(x: Union[Column, float]) -> Function:
    """Returns inverse hyperbolic cosine."""
    return Function("acosh", x)


def atanh(x: Union[Column, float]) -> Function:
    """Returns inverse hyperbolic tangent."""
    return Function("atanh", x)


def hypot(x: Union[Column, float], y: Union[Column, float]) -> Function:
    """Returns hypotenuse."""
    return Function("hypot", x, y)


def logGamma(x: Union[Column, float]) -> Function:
    """Returns log of gamma function."""
    return Function("logGamma", x)


def tgamma(x: Union[Column, float]) -> Function:
    """Returns gamma function."""
    return Function("tgamma", x)


def lgamma(x: Union[Column, float]) -> Function:
    """Returns log of absolute value of gamma."""
    return Function("lgamma", x)


def erf(x: Union[Column, float]) -> Function:
    """Returns error function."""
    return Function("erf", x)


def erfc(x: Union[Column, float]) -> Function:
    """Returns complementary error function."""
    return Function("erfc", x)


def erfInv(x: Union[Column, float]) -> Function:
    """Returns inverse error function."""
    return Function("erfInv", x)


def erfcInv(x: Union[Column, float]) -> Function:
    """Returns inverse complementary error function."""
    return Function("erfcInv", x)

