import pytest
from mathcore.safe_eval import safe_eval
from mathcore.errors import MathError

def test_log_negative():
    with pytest.raises(MathError):
        safe_eval("log(-1)")

def test_log_base_one():
    with pytest.raises(MathError):
        safe_eval("log(10,1)")

def test_division_by_zero():
    with pytest.raises(MathError):
        safe_eval("1/0")