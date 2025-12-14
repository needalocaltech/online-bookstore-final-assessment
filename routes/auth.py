from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services import user_service

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


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        name = request.form.get("name")
        address = request.form.get("address", "")

        if not email or not password or not name:
            flash("Please fill in all required fields", "error")
            return render_template("register.html")

        try:
            user_service.register_user(email, password, name, address)
        except ValueError:
            flash("An account with this email already exists", "error")
            return render_template("register.html")

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = user_service.authenticate(email, password)
        if not user:
            flash("Invalid email or password", "error")
            return render_template("login.html")

        session["user_email"] = user.email
        flash("Logged in successfully!", "success")
        return redirect(url_for("store.index"))

    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.pop("user_email", None)
    flash("Logged out successfully!", "success")
    return redirect(url_for("store.index"))


@auth_bp.route("/account")
@login_required
def account():
    current_user = user_service.get_current_user()
    return render_template("account.html", current_user=current_user)

@auth_bp.route("/account", methods=["GET", "POST"])
@login_required
def account():
    """
    Account page for viewing and updating basic profile details.

    Uses the service layer so that business logic stays out of the route.
    """
    current_user = user_service.get_current_user()

    if request.method == "POST":
        name = request.form.get("name") or current_user.name
        address = request.form.get("address") or current_user.address

        user_service.update_profile(current_user, name=name, address=address)
        flash("Profile updated successfully.", "success")
        return redirect(url_for("auth.account"))

    # GET – render form pre-populated with current details
    return render_template("account.html", current_user=current_user)
