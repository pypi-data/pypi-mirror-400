from .parser import eval_alg
from .functions import sin, cos, tan, log, ln, log10, pow_func
from .errors import DomainError, DivisionByZeroError

def safe_eval(expr, variables=None, *, degrees=False):
    try:
        if variables is None:
            variables = {}
        
        variables = dict(variables)
        variables.update({
            "sin": lambda x: sin(x, degrees),
            "cos": lambda x: cos(x, degrees),
            "tan": lambda x: tan(x, degrees),
            "log": log,
            "ln": ln,
            "log10": log10,
            "pow": pow_func
        })
        
        if degrees:
            variables = variables.copy()
            variables["__DEGREES__"] = True
        
        return eval_alg(expr, variables)
    except DivisionByZeroError:
        raise DomainError("division by zero")