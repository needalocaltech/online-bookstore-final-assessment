import uuid
from datetime import datetime
from typing import Dict, List, Optional

from models import Order, EmailService
from .cart_service import get_cart

# All orders keyed by order_id (for confirmation page)
_ORDERS: Dict[str, Order] = {}

# Per-user order history (keyed by user email)
_USER_ORDERS: Dict[str, List[Order]] = {}


def init_store() -> None:
    """Initialise in-memory order store."""
    # Kept for symmetry with other services and future DB wiring.
    return


def create_order(shipping_info: dict, payment_info: dict, user_email: str | None = None) -> Order:
    """
    Create an order object from the current cart and store it.

    If a user_email is provided, the order is also added to that user's
    order history. This supports the 'My Orders' page.
    """
    cart = get_cart()
    order_id = str(uuid.uuid4())
    order_date = datetime.utcnow()
    total_amount = cart.get_total_price()

    order = Order(
        order_id=order_id,
        order_date=order_date,
        items=list(cart.get_items()),
        total_amount=total_amount,
        shipping_info=shipping_info,
        payment_info=payment_info,
    )

    _ORDERS[order_id] = order

    # Track order under user history (if we know who they are)
    if user_email:
        history = _USER_ORDERS.setdefault(user_email, [])
        history.append(order)

    # Mock “send email”
    EmailService.send_order_confirmation(shipping_info.get("email"), order)

    return order


def get_order(order_id: str) -> Optional[Order]:
    return _ORDERS.get(order_id)


def get_orders_for_user(user_email: str) -> List[Order]:
    """
    Return all orders associated with the given user email.

    In a real implementation this would become a SELECT query
    against a persistent orders table keyed by user_id/email.
    """
    return list(_USER_ORDERS.get(user_email, []))
