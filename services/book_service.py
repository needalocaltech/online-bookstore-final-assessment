from typing import List, Optional
from models import Book

# In-memory book catalogue for now (later: move to real DB)
_BOOKS: list[Book] = []


def init_books() -> None:
    """Initialise the in-memory catalogue. Call once from create_app()."""
    global _BOOKS
    if _BOOKS:
        return  # already initialised

    _BOOKS = [
        Book("The Great Gatsby", "Fiction", 10.99, "/images/books/the_great_gatsby.jpg"),
        Book("1984", "Dystopia", 8.99, "/images/books/1984.jpg"),
        Book("I Ching", "Traditional", 18.99, "/images/books/I-Ching.jpg"),
        Book("Moby Dick", "Adventure", 12.49, "/images/books/moby_dick.jpg"),
    ]


def get_all_books() -> List[Book]:
    return list(_BOOKS)


def get_book_by_title(title: str) -> Optional[Book]:
    for book in _BOOKS:
        if book.title == title:
            return book
    return None


def create_book(title: str, genre: str, price: float, image_url: str) -> Book:
    """
    Create a new Book and add it to the in-memory catalogue.

    In a future version this will write to a database instead of a list.
    """
    book = Book(title, genre, price, image_url)
    _BOOKS.append(book)
    return book
