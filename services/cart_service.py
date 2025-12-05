"""
services/cart_service.py

Cart service layer.

The cart is stored per-session using Flask's secure session cookie.
This module exposes a small Cart object with helpers that are easy to
use from templates (cart.is_empty(), cart.get_total_items(),
cart.get_total_price(), cart.items, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List

from flask import session

CART_SESSION_KEY = "cart"


@dataclass
class CartItem:
    """
    Simple value object representing a line in the cart.
    Jinja can access dict-like fields with dot notation, so this is safe.
    """
    title: str
    price: float
    quantity: int

    def line_total(self) -> float:
        return round(self.price * self.quantity + 1e-9, 2)


class Cart:
    """
    Lightweight cart wrapper used by the templates and services.
    Internally, items are kept in a dict keyed by title.
    """

    def __init__(self, items: Dict[str, CartItem] | None = None) -> None:
        self._items: Dict[str, CartItem] = items or {}

    # ----- Core operations -----

    def add_item(self, title: str, price: float, quantity: int = 1) -> None:
        quantity = max(1, int(quantity))
        if title in self._items:
            existing = self._items[title]
            existing.quantity += quantity
        else:
            self._items[title] = CartItem(
                title=title,
                price=float(price),
                quantity=quantity,
            )

    def clear(self) -> None:
        self._items.clear()

    # ----- Read helpers used in templates / services -----

    def is_empty(self) -> bool:
        return self.get_total_items() == 0

    def get_total_items(self) -> int:
        return sum(item.quantity for item in self._items.values())

    def get_total_price(self) -> float:
        return round(
            sum(item.price * item.quantity for item in self._items.values()) + 1e-9,
            2,
        )

    @property
    def items(self) -> List[CartItem]:
        """
        Returns a list of items for iteration in templates:
            {% for item in cart.items %}
                {{ item.title }} {{ item.quantity }} {{ item.price }}
            {% endfor %}
        """
        return list(self._items.values())

    # ----- Serialisation helpers for storing in the session -----

    def to_dict(self) -> Dict[str, Any]:
        return {
            "items": [
                {
                    "title": item.title,
                    "price": float(item.price),
                    "quantity": int(item.quantity),
                }
                for item in self._items.values()
            ]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any] | None) -> "Cart":
        if not isinstance(data, dict):
            return cls()
        items_data = data.get("items") or []
        items: Dict[str, CartItem] = {}
        for raw in items_data:
            title = raw.get("title")
            if not title:
                continue
            try:
                price = float(raw.get("price", 0.0))
                quantity = int(raw.get("quantity", 1))
            except (TypeError, ValueError):
                continue
            items[title] = CartItem(title=title, price=price, quantity=quantity)
        return cls(items)


# ===== Public service functions =====


def init_cart() -> None:
    """
    Initialisation hook for the cart subsystem.

    Called from create_app() in __init__.py. We deliberately do
    **nothing** here because the Flask `session` is only available
    inside a request context.
    """
    return


def get_cart() -> Cart:
    """
    Get the current user's cart as a Cart object. If no cart is present,
    an empty one is created and stored in the session.
    """
    raw = session.get(CART_SESSION_KEY)
    cart = Cart.from_dict(raw)
    # If there was no cart at all, persist a new one
    if raw is None:
        session[CART_SESSION_KEY] = cart.to_dict()
        session.modified = True
    return cart


def save_cart(cart: Cart) -> None:
    """
    Persist the given cart back into the session.
    """
    session[CART_SESSION_KEY] = cart.to_dict()
    session.modified = True


def clear_cart() -> None:
    """
    Remove the cart from the current session.
    """
    if CART_SESSION_KEY in session:
        session.pop(CART_SESSION_KEY)
        session.modified = True


def is_empty() -> bool:
    """
    Convenience helper mirroring the old API used in some places:
        if cart_service.is_empty(): ...
    """
    return get_cart().is_empty()
