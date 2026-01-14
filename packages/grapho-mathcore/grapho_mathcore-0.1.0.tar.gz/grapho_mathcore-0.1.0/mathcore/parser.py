import ast
import operator as op
import math
from .constants import CONSTANTS


DEFAULT_VARS = {
    "pi":math.pi,
    "e":math.e,
    "tau": math.tau,
    "phi": (1+5**0.5)/2
}


OPS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.Eq: op.eq,
    ast.NotEq: op.ne,
    ast.Lt: op.lt,
    ast.LtE: op.le,
    ast.Gt: op.gt,
    ast.GtE: op.ge
}

FUNCS = {
    "abs": abs,
    "sin": lambda x: math.sin(math.radians(x)),
    "cos": lambda x: math.cos(math.radians(x)),
    "tan": lambda x: math.tan(math.radians(x))
}

def eval_alg(expr, vars={}):
    if vars is None:
        vars = {}
    vars = {**DEFAULT_VARS, **vars}
    def _eval(n):
        if isinstance(n, ast.Constant):
            return n.value
        if isinstance(n, ast.Name):
            return vars[n.id]
        if isinstance(n, ast.BinOp):
            return OPS[type(n.op)](_eval(n.left),_eval(n.right))
        if isinstance(n, ast.UnaryOp):
            return OPS[type(n.op)](_eval(n.operand))
        if isinstance(n, ast.Call) and n.func.id in FUNCS:
            return FUNCS[n.func.id](_eval(n.args[0]))
        raise TypeError ("Invalid expression")
    expr = expr.replace("^","**")
    return _eval(ast.parse(expr, mode="eval").body)
        