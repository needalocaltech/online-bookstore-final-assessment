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

from services import user_service, order_service

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Login form: authenticate user and store email in session.
    """
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        if not email or not password:
            flash("Please enter both email and password.", "error")
            return render_template("login.html")

        user = user_service.authenticate(email, password)
        if not user:
            flash("Invalid email or password.", "error")
            return render_template("login.html")

        session["user_email"] = user.email
        flash("You are now logged in!", "success")
        return redirect(url_for("store.index"))

    # GET
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Log out the current user."""
    session.pop("user_email", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("store.index"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """User registration form."""
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""
        address = (request.form.get("address") or "").strip()

        if not name or not email or not password:
            flash("Name, email and password are required.", "error")
            return render_template("register.html")

        try:
            user_service.register_user(
                email=email,
                raw_password=password,
                name=name,
                address=address,
            )
        except ValueError as exc:
            flash(str(exc), "error")
            return render_template("register.html")

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/my-orders")
def my_orders():
    """Show orders for the currently logged-in user."""
    current_user = user_service.get_current_user()
    if not current_user:
        flash("Please log in to view your orders.", "error")
        return redirect(url_for("auth.login"))

    orders = order_service.get_orders_for_user(current_user.email)
    return render_template(
        "my_orders.html",
        current_user=current_user,
        orders=orders,
    )


# ---------- decorators ----------

def login_required(view):
    """Require login for protected routes."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_email" not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for("auth.login"))
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    """Admin-only routes."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = user_service.get_current_user()
        if not user or not user_service.is_admin(user):
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def reviewer_required(view):
    """Reviewer-only routes."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = user_service.get_current_user()
        if not user or not user_service.is_reviewer(user):
            abort(403)
        return view(*args, **kwargs)
    return wrapped
