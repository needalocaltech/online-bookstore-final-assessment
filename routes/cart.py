import logging
from typing import Optional

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
)

from services import cart_service, user_service, order_service, book_service

logger = logging.getLogger(__name__)

# IMPORTANT: no url_prefix here so routes are exactly "/cart", "/add-to-cart", etc.
cart_bp = Blueprint("cart", __name__)


@cart_bp.route("/cart")
def view_cart():
    current_user = user_service.get_current_user()
    cart = cart_service.get_cart()
    return render_template("cart.html", cart=cart, current_user=current_user)


@cart_bp.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    """
    Add a book to the cart.

    Form posts:
        title    -> book title
        quantity -> number of copies
    """
    title = (request.form.get("title") or "").strip()
    qty_raw = request.form.get("quantity") or "1"

    try:
        quantity = max(1, int(qty_raw))
    except ValueError:
        quantity = 1

    if not title:
        flash("Invalid book selection.", "error")
        return redirect(url_for("store.index"))

    # Lookup book by title
    books = book_service.get_all_books()
    book: Optional[object] = next((b for b in books if b.title == title), None)

    if not book:
        flash("Book not found.", "error")
        return redirect(url_for("store.index"))

    cart = cart_service.get_cart()
    cart.add_item(title=book.title, price=book.price, quantity=quantity)
    cart_service.save_cart(cart)

    flash(f"Added {quantity} × '{book.title}' to your cart.", "success")
    return redirect(url_for("store.index"))


@cart_bp.route("/clear-cart", methods=["POST"])
def clear_cart_route():
    cart_service.clear_cart()
    flash("Your cart has been cleared.", "success")
    return redirect(url_for("cart.view_cart"))


@cart_bp.route("/checkout")
def checkout():
    cart = cart_service.get_cart()
    if cart.is_empty():
        flash("Your cart is empty!", "error")
        return redirect(url_for("store.index"))

    current_user = user_service.get_current_user()
    return render_template("checkout.html", cart=cart, current_user=current_user)


@cart_bp.route("/process-checkout", methods=["POST"])
def process_checkout():
    cart = cart_service.get_cart()
    if cart.is_empty():
        flash("Your cart is empty!", "error")
        return redirect(url_for("store.index"))

    shipping_info = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "address": request.form.get("address"),
        "city": request.form.get("city"),
        "zip_code": request.form.get("zip_code"),
    }

    payment_info = {
        "card_number": request.form.get("card_number"),
        "expiry_date": request.form.get("expiry_date"),
        "cvv": request.form.get("cvv"),
    }

    current_user = user_service.get_current_user()
    user_email = current_user.email if current_user else shipping_info.get("email")

    order = order_service.create_order(
        shipping_info=shipping_info,
        payment_info=payment_info,
        user_email=user_email,
    )

    cart_service.clear_cart()
    session["last_order_id"] = order.order_id

    flash("Payment successful! Your order has been confirmed.", "success")
    return redirect(url_for("cart.order_confirmation", order_id=order.order_id))


@cart_bp.route("/order-confirmation/<order_id>")
def order_confirmation(order_id: str):
    order = order_service.get_order(order_id)
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("store.index"))

    current_user = user_service.get_current_user()
    return render_template(
        "order_confirmation.html",
        order=order,
        current_user=current_user,
    )
