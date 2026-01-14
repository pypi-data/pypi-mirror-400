from .function_evaluator import evaluate_function

def value_table(expr, x_values):
    y_values = evaluate_function(expr, x_values)

    table=[]
    for x, y in zip(x_values, y_values):
        table.append((x,y))
    
    return table