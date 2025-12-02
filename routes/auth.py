import logging
from functools import wraps

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    abort,
)

from bookstore.services import user_service, order_service

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


def login_required(view):
    """Decorator to require login for certain routes."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_email" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    """Decorator to enforce admin-only access on routes."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = user_service.get_current_user()
        if not user or not user_service.is_admin(user):
            # Do not reveal whether the user exists or is admin; simply deny.
            abort(403)
        return view(*args, **kwargs)

    return wrapped


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""
        name = (request.form.get("name") or "").strip()
        address = request.form.get("address", "").strip()

        if not email or not password or not name:
            flash("Please fill in all required fields.", "error")
            return render_template("register.html")

        try:
            user_service.register_user(email, password, name, address)
        except ValueError as ex:
            # Could be "email already registered" or password policy failure
            flash(str(ex), "error")
            return render_template("register.html")

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()
        password = request.form.get("password") or ""

        user = user_service.authenticate(email, password)
        if not user:
            # Generic message to avoid leaking lockout or existence details
            logger.warning("Failed login attempt for email=%s", email)
            flash(
                "Invalid email or password, or your account has been temporarily locked.",
                "error",
            )
            return render_template("login.html")

        session["user_email"] = user.email
        logger.info("User %s logged in successfully", email)
        flash("Logged in successfully!", "success")
        return redirect(url_for("store.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    user_email = session.pop("user_email", None)
    if user_email:
        logger.info("User %s logged out", user_email)
    flash("Logged out successfully!", "success")
    return redirect(url_for("store.index"))


@auth_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """
    Account page for viewing and updating basic profile details.
    Uses the service layer so that business logic stays out of the route.
    """
    current_user = user_service.get_current_user()

    if request.method == "POST":
        name = (request.form.get("name") or current_user.name).strip()
        address = (request.form.get("address") or current_user.address).strip()

        user_service.update_profile(current_user, name=name, address=address)
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.account"))

    # GET – render form pre-populated with current details
    return render_template("account.html", current_user=current_user)


@auth_bp.route("/my-orders")
@login_required
def my_orders():
    """
    Show the order history for the currently logged-in user.
    Orders are retrieved via the OrderService, which currently uses
    an in-memory store but can be swapped for a database later.
    """
    current_user = user_service.get_current_user()
    orders = order_service.get_orders_for_user(current_user.email)

    return render_template(
        "my_orders.html",
        current_user=current_user,
        orders=orders,
    )
