from .parser import eval_alg
import math

def solve_equation(expr, var="x", interval=(-10, 10), steps=1000, tol=1e-6, constraint=None):
    a, b = interval
    xs = [a + i * (b-a) / steps for i in range(steps + 1)]

    def f(x):
        return eval_alg(expr, {var: x})
    
    def check_constraint(x):
        if constraint is None:
            return True
        return bool(eval_alg(constraint, {var: x}))

    values = []

    for x in xs:
        try: values.append(f(x))
        except: values.append(None)
    
    #case 1: function is always 0
    if all(v is not None and abs(v) < tol for v in values if v is not None):
        return "infinite"
    solutions = []

    #case 2: normal
    for i in range(len(xs) - 1):
        y1, y2 = values[i], values[i+1]
        if y1 is None or y2 is None: continue
        if abs(y1) < tol and check_constraint(xs[i]):
            solutions.append(xs[i])
        elif y1 * y2 < 0:
            left, right = xs[i], xs[i+1]

            #bisection
            while abs(right - left) > tol:
                mid = (left + right) / 2
                if f(left) * f(mid) <= 0:
                    right = mid
                else: left = mid
            
            sol = (left + right) / 2
            if check_constraint(sol):

                solutions.append(sol)
    if not solutions: print ("No solution found")
    else: print(solutions[0])

    return sorted(set(round(s, 5) for s in solutions))