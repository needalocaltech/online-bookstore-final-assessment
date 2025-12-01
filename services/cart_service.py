from models import Cart
from . import book_service

_CART: Cart | None = None


def init_cart() -> None:
    """Create a single Cart instance for this prototype.

    NOTE: For a real system, you'd have one cart *per user/session*
    stored in a DB or cache, rather than a global.
    """
    global __CART
    if __CART is None:
        _CART = Cart()


def get_cart() -> Cart:
    if _CART is None:
        init_cart()
    return _CART


def add_item(title: str, quantity: int = 1):
    cart = get_cart()
    book = book_service.get_book_by_title(title)
    if not book:
        return None
    cart.add_book(book, quantity)
    return book


def remove_item(title: str) -> None:
    cart = get_cart()
    cart.remove_book(title)


def update_item_quantity(title: str, quantity: int) -> None:
    cart = get_cart()
    cart.update_quantity(title, quantity)


def clear_cart() -> None:
    cart = get_cart()
    cart.clear()


def is_empty() -> bool:
    return get_cart().is_empty()


def total_price() -> float:
    return get_cart().get_total_price()
