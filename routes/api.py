from flask import Blueprint, jsonify
from bookstore.services import book_service

api_bp = Blueprint("api", __name__)


@api_bp.get("/books")
def api_list_books():
    """Simple JSON catalogue endpoint (future expansion)."""
    books = book_service.get_all_books()
    return jsonify(
        [
            {
                "title": b.title,
                "category": b.genre,
                "price": b.price,
                "image_url": b.image_url,
            }
            for b in books
        ]
    )
