# tests/unit/test_cart_math.py
# from models_0 import compute_cart_totals
from models_not_quite_working import compute_cart_totals

def test_compute_cart_totals_correct_sum():
    cart = [{"price": 10.0, "qty": 2}, {"price": 15.0, "qty": 1}]
    result = compute_cart_totals(cart)
    assert result["subtotal"] == 35.00

def test_compute_cart_totals_with_discount():
    cart = [{"price": 100.0, "qty": 1}]
    result = compute_cart_totals(cart, codes=["SAVE10"])
    assert result["total"] == 90.00
    assert result["discount"] == 10.00

def test_compute_cart_totals_zero_qty():
    cart = [{"price": 15.0, "qty": 0}]
    result = compute_cart_totals(cart)
    assert result["subtotal"] == 0.00
