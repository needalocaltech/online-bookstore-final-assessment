import logging

from flask import Blueprint, render_template, flash, request, redirect, url_for

from bookstore.routes.auth import login_required, admin_required
from bookstore.services import user_service, book_service

logger = logging.getLogger(__name__)

admin_bp = Blueprint("admin", __name__, template_folder="../../templates")


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    """
    Simple admin dashboard showing all books.

    Access here is restricted to users with the admin role.
    """
    current_user = user_service.get_current_user()
    books = book_service.get_all_books()
    return render_template("admin/dashboard.html", current_user=current_user, books=books)


@admin_bp.route("/books/new", methods=["GET", "POST"])
@login_required
@admin_required
def add_book():
    """
    Admin-only form to create a new book in the catalogue.

    This demonstrates how the admin section can manage catalogue data via
    the service layer rather than embedding logic in templates.
    """
    current_user = user_service.get_current_user()

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        genre = (request.form.get("genre") or "").strip()
        price_raw = (request.form.get("price") or "").strip()
        image_url = (request.form.get("image_url") or "").strip()

        # Basic server-side validation
        if not title or not genre or not price_raw:
            flash("Title, genre and price are required.", "error")
            return render_template("admin/add_book.html", current_user=current_user)

        try:
            price = float(price_raw)
        except ValueError:
            flash("Price must be a valid number.", "error")
            return render_template("admin/add_book.html", current_user=current_user)

        # Create the new book via the service layer
        book_service.create_book(title=title, genre=genre, price=price, image_url=image_url)

        logger.info("Admin %s created new book '%s'", current_user.email, title)
        flash(f'Book "{title}" created successfully.', "success")
        return redirect(url_for("admin.dashboard"))

    # GET
    return render_template("admin/add_book.html", current_user=current_user)
