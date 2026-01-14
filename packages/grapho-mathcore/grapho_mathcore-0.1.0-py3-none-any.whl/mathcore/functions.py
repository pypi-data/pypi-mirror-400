import math
from .errors import DomainError
def sin(x, degrees=False):
    if degrees: x = math.radians(x)
    return math.sin(x)

def cos(x, degrees=False):
    if degrees: x = math.radians(x)
    return math.cos(x)

def tan(x, degrees=False):
    if degrees: x = math.radians(x)
    return math.tan(x)

def log(x, base=10):
    if x <= 0:
        raise DomainError("log undefined for x <= 0")
    if base <= 0 or base == 1:
        raise DomainError("invalid log base")
    return math.log(x, base)

def ln(x):
    if x <= 0:
        raise ValueError("ln undefined for x <= 0")
    return math.log(x)

def log10(x):
    if x <= 0:
        raise ValueError("log10 undefined for x <= 0")
    return math.log10(x)

def pow_func(x, y):
    return x ** y