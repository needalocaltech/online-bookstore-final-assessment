from flask import Blueprint, render_template
from bookstore.services import book_service, cart_service, user_service

store_bp = Blueprint("store", __name__)


@store_bp.route("/")
def index():
    """Homepage showing the book catalogue."""
    current_user = user_service.get_current_user()
    books = book_service.get_all_books()
    cart = cart_service.get_cart()
    return render_template(
        "index.html",
        books=books,
        cart=cart,
        current_user=current_user,
    )
