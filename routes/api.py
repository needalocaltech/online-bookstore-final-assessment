from flask import Blueprint, jsonify

from services import book_service

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/books", methods=["GET"])
def api_list_books():
    """
    Simple JSON API endpoint returning all books.
    """
    books = book_service.get_all_books()
    data = [
        {
            "title": b.title,
            "author": b.author,
            "price": float(b.price),
            "genre": b.genre,
            "isbn": b.isbn,
        }
        for b in books
    ]
    return jsonify(data)
