from mathcore.safe_eval import safe_eval
import math

def test_basic():
    assert safe_eval("2+3") == 5
    assert safe_eval("2**3") == 8

def test_variables():
    assert safe_eval("x**2", {'x': 4}) == 16

def test_constants():
    assert abs(safe_eval("pi")-math.pi) < 1e-6

def test_trigonometry_radians():
    assert abs(safe_eval("sin(pi/6)")-0.5) < 1e-6

def test_trigonometry_degrees():
    assert abs(safe_eval("sin(30)", degrees=True)-0.5) < 1e-6

def test_log():
    assert safe_eval("log(100)") == 2
    assert safe_eval("log(8, 2)") == 3

def test_ln():
    assert abs(safe_eval("ln(e)") - 1) < 1e-6

def test_pow():
    assert safe_eval("pow(2, 3)") == 8
    assert safe_eval("pow(9, 0.5)") == 3