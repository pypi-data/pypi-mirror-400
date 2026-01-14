class MathCoreError(Exception):
    """Base error for mathcore"""

class SyntaxError(MathCoreError):
    pass

class UndefinedVariableError(MathCoreError):
    pass

class DomainError(MathCoreError):
    pass

class DivisionByZeroError(MathCoreError):
    pass