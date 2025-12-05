"""
services package initialiser.

This file makes it easy to import the main service modules as:

    from services import user_service, book_service, cart_service, order_service
"""

from . import user_service
from . import book_service
from . import cart_service
from . import order_service

__all__ = [
    "user_service",
    "book_service",
    "cart_service",
    "order_service",
]
