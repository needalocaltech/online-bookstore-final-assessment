@cart_bp.route("/process-checkout", methods=["POST"])
def process_checkout():
    if cart_service.is_empty():
        flash("Your cart is empty!", "error")
        return redirect(url_for("store.index"))

    # Shipping details from form
    shipping_info = {
        "name": request.form.get("name"),
        "email": request.form.get("email"),
        "address": request.form.get("address"),
        "city": request.form.get("city"),
        "zip_code": request.form.get("zip_code"),
    }

    # Mock payment details (never stored in production)
    payment_info = {
        "card_number": request.form.get("card_number"),
        "expiry_date": request.form.get("expiry_date"),
        "cvv": request.form.get("cvv"),
    }

    # If the user is logged in, tie the order to their account
    current_user = user_service.get_current_user()
    user_email = current_user.email if current_user else shipping_info.get("email")

    order = order_service.create_order(
        shipping_info=shipping_info,
        payment_info=payment_info,
        user_email=user_email,
    )

    # Clear cart after successful order
    cart_service.clear_cart()

    # Keep order ID in session for confirmation page
    session["last_order_id"] = order.order_id

    flash("Payment successful! Your order has been confirmed.", "success")
    return redirect(url_for("cart.order_confirmation", order_id=order.order_id))
