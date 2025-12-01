from flask import Blueprint, render_template, flash
from bookstore.routes.auth import login_required
from bookstore.services import user_service, book_service

admin_bp = Blueprint("admin", __name__, template_folder="../../templates")


@admin_bp.route("/")
@login_required
def dashboard():
    current_user = user_service.get_current_user()
    # Later you can add checks like: if not current_user.is_admin: abort(403)
    books = book_service.get_all_books()
    return render_template("admin/dashboard.html", current_user=current_user, books=books)
