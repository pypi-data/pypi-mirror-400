import numpy as np
import matplotlib.pyplot as plt
from tkinter import Toplevel, Label, Entry, Button
from .parser import eval_alg
import math


def run():
    win = Toplevel()
    win.title("Function Graph")
    win.geometry("400x250")

    Label(win, text="Function f(x)").pack()
    func_entry = Entry(win, width=30)
    func_entry.insert(0, "sin(x)")
    func_entry.pack()

    Label(win, text="Interval [a, b]").pack()
    a_entry = Entry(win)
    a_entry.insert(0, "-10")
    a_entry.pack()

    b_entry = Entry(win)
    b_entry.insert(0, "10")
    b_entry.pack()

    def plot_function():
        expr = func_entry.get()
        a = float(a_entry.get())
        b = float(b_entry.get())

        xs = np.linspace(a, b, 400)
        ys = [] 

        for x in xs:
            try:
                y = eval_alg(expr, {"x": x})
                ys.append(y)
            except: 
                ys.append(None)

        plt.figure()
        plt.plot(xs, ys)
        plt.title(f"f(x) = {expr}")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.grid(True)
        plt.show()

    Button(win, text="Draw function", command=plot_function).pack(pady=10)

