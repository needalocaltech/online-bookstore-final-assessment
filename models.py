# ========= Test-friendly pricing helpers (thin wrappers) =========
from typing import Iterable, Dict, Any, List, Tuple

DISCOUNT_TABLE = {
    "SAVE10": 0.10,
    "WELCOME20": 0.20,
}

def _money(x: float) -> float:
    return round(x + 1e-9, 2)

def calculate_discounted_price(
    amount: float, 
    percentage_discount: float = 0.0, 
    fixed_discount: float = 0.0
) -> float:
    """
    Applies either a percentage discount or a fixed amount discount to the given amount.
    Only one type of discount should be applied at a time.
    """
    if fixed_discount > 0.0:
        # Apply fixed discount first
        discounted_amount = amount - fixed_discount
    elif percentage_discount > 0.0:
        # Apply percentage discount
        discounted_amount = amount * (1.0 - percentage_discount)
    else:
        discounted_amount = amount

    # Ensure the price doesn't go below zero
    return _money(max(0.0, discounted_amount))


def apply_discount(amount: float, code: str) -> float:
    pct = DISCOUNT_TABLE.get(str(code).strip().upper())
    if pct:
        # Use the updated helper function with the percentage discount argument
        return calculate_discounted_price(amount, percentage_discount=pct)
    return _money(amount)

def apply_discounts(amount: float, codes: Iterable[str]) -> float:
    total = float(amount)
    for c in (codes or []):
        total = apply_discount(total, c)
    return _money(total)

def _normalize_cart(cart: Iterable) -> List[Tuple[float, int]]:
    """
    Accepts:
      - list of dicts: {"price": 10.0, "qty": 2}
      - list of tuples: (book_id, qty, price) or (price, qty)
    Returns: list of (price, qty)
    """
    norm: List[Tuple[float, int]] = []
    for item in cart or []:
        if isinstance(item, dict):
            price = float(item.get("price", 0.0))
            qty = int(item.get("qty", 0))
            norm.append((price, qty))
        elif isinstance(item, (list, tuple)):
            if len(item) == 3:
                _, qty, price = item
            elif len(item) == 2:
                price, qty = item
            else:
                raise ValueError(f"Unsupported cart item shape: {item}")
            norm.append((float(price), int(qty)))
        else:
            raise ValueError(f"Unsupported cart item type: {type(item)}")
    return norm

def calculate_total(cart: Iterable) -> float:
    """Sum price*qty for the cart (no discounts)."""
    subtotal = 0.0
    for price, qty in _normalize_cart(cart):
        subtotal += price * qty
    return _money(subtotal)

def compute_cart_totals(cart: Iterable, codes: Iterable[str] = None) -> Dict[str, Any]:
    """
    Return a view-model of the cart totals.
    {
      "subtotal": 35.00,
      "discount": 3.50,
      "total": 31.50,
      "line_items": [{"price":10.0,"qty":2,"line_total":20.0}, ...]
    }
    """
    line_items = []
    subtotal = 0.0
    for price, qty in _normalize_cart(cart):
        line_total = price * qty
        line_items.append({"price": _money(price), "qty": qty, "line_total": _money(line_total)})
        subtotal += line_total
        
    discount = _money(subtotal - apply_discounts(subtotal, codes))
    total = _money(subtotal - discount)
    
    return {
        "subtotal": _money(subtotal),
        "discount": discount,
        "total": total,
        "line_items": line_items,
    }
