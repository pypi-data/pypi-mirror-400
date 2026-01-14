import math

def evaluate_function(expr, x_values):
    results=[]

    for x in x_values:
        try:
            y = eval(expr, {
                "__builtins__": None,
                "x": x,
                "sin": math.sin,
                "cos": math.cos,
                "tan": math.tan,
                "pi": math.pi,
                "e": math.e
            })
            results.append(y)
        except: results.append(None)
    
    return results
