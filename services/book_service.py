"""
book_service.py

Service layer for managing books using the database-backed Book model.
"""

from typing import List, Optional

from models import Book
from db import db   # local SQLAlchemy instance


# --------- Initialisation / seeding --------- #

def init_books() -> None:
    """
    Seed a few default books into the database, but only if the
    books table is currently empty.

    This should be called once at application startup (e.g. from create_app()).
    """
    # If there are already books, do nothing
    if Book.query.count() > 0:
        return

    defaults = [
        {
            "title": "The Great Gatsby",
            "category": "Fiction",
            "price": 10.99,
            "image": "/static/images/books/the_great_gatsby.jpg",
        },
        {
            "title": "1984",
            "category": "Dystopia",
            "price": 8.99,
            "image": "/static/images/books/1984.jpg",
        },
        {
            "title": "I Ching",
            "category": "Traditional",
            "price": 18.99,
            "image": "/static/images/books/I-Ching.jpg",
        },
        {
            "title": "Moby Dick",
            "category": "Adventure",
            "price": 12.49,
            "image": "/static/images/books/moby_dick.jpg",
        },
    ]

    for data in defaults:
        book = Book(
            title=data["title"],
            category=data["category"],
            price=data["price"],
            image=data["image"],
        )
        db.session.add(book)

    db.session.commit()


# --------- Query helpers --------- #

def get_all_books() -> List[Book]:
    """Return all books from the database ordered by title."""
    return Book.query.order_by(Book.title.asc()).all()


def get_book_by_id(book_id: int) -> Optional[Book]:
    """Fetch a single book by its primary key ID."""
    return Book.query.get(book_id)


def get_book_by_title(title: str) -> Optional[Book]:
    """Fetch a single book by its unique title."""
    return Book.query.filter_by(title=title).first()


def search_books(keyword: str) -> List[Book]:
    """Simple case-insensitive search over title and category."""
    if not keyword:
        return get_all_books()

    pattern = f"%{keyword.strip().lower()}%"
    return Book.query.filter(
        (Book.title.ilike(pattern)) | (Book.category.ilike(pattern))
    ).order_by(Book.title.asc()).all()


# --------- Create / update / delete (used by admin) --------- #

def create_book(title: str, category: str, price: float, image: str) -> Book:
    """
    Create a new book and persist it to the database.
    Called from the admin 'Add Book' form.
    """
    book = Book(title=title, category=category, price=price, image=image)
    db.session.add(book)
    db.session.commit()
    return book


def update_book(
    book_id: int,
    title: str,
    category: str,
    price: float,
    image: str,
) -> Optional[Book]:
    """
    Update an existing book identified by its ID.
    Returns the updated book or None if not found.
    """
    book = Book.query.get(book_id)
    if not book:
        return None

    book.title = title
    book.category = category
    book.price = float(price)
    book.image = image

    db.session.commit()
    return book


def delete_book(book_id: int) -> bool:
    """
    Delete a book by ID. Returns True on success, False if not found.
    """
    book = Book.query.get(book_id)
    if not book:
        return False

    db.session.delete(book)
    db.session.commit()
    return True
