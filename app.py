# --------------------------
# RSS Caching (in-memory)
# --------------------------
RSS_CACHE = {}
RSS_CACHE_TTL = 300  # cache for 5 minutes

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from models import Book, Cart, User, Order, PaymentGateway, EmailService
import uuid
import os
import secrets
import datetime
import sqlite3
from pathlib import Path
import feedparser
import bcrypt
import time

def fetch_rss_items(url: str, limit: int = 5):
    """
    Fetch and return RSS feed items with caching (5 min default).
    Falls back safely if feed is unavailable.
    """
    now = time.time()

    # If in cache and not expired
    if url in RSS_CACHE:
        cached_data = RSS_CACHE[url]
        if now - cached_data["timestamp"] < RSS_CACHE_TTL:
            return cached_data["items"][:limit]

    try:
        feed = feedparser.parse(url)
        items = feed.entries[:limit]
    except Exception:
        items = []

    RSS_CACHE[url] = {"timestamp": now, "items": items}
    return items

###########################################################
# FLASK APP INITIALISATION
###########################################################

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_urlsafe(32))

"""
app.py

Entry point for the online bookstore application.
"""

from __init__ import create_app

# Global app object for Flask / WSGI
app = create_app()


if __name__ == "__main__":
    import os

    host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    port = int(os.environ.get("FLASK_RUN_PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    print("Starting Online Bookstore on http://%s:%s" % (host, port))
    app.run(host=host, port=port, debug=debug)

###########################################################
# SQLITE BOOK DATABASE FUNCTIONS
###########################################################

DB_PATH = Path(__file__).with_name("books.db")


def init_books_db() -> None:
    """Create books.db and seed demo books."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            title    TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            price    REAL NOT NULL,
            image    TEXT
        )
    """)

    cur.execute("SELECT COUNT(*) FROM books")
    (count,) = cur.fetchone()

    if count == 0:
        default_books = [
            ("I Ching", "Traditional", 18.99, "static/images/I-Ching.jpg"),
            ("The Great Gatsby", "Fiction", 10.99, "static/images/default-book.jpg"),
            ("1984", "Dystopia", 8.99, "static/images/default-book.jpg"),
            ("Moby Dick", "Adventure", 12.49, "static/images/default-book.jpg"),
            ("Pride and Prejudice", "Romance", 9.99, "static/images/default-book.jpg"),
            ("Clean Code", "Technology", 29.99, "static/images/default-book.jpg"),
            ("Python Crash Course", "Technology", 24.99, "static/images/default-book.jpg"),
        ]
        cur.executemany(
            "INSERT INTO books (title, category, price, image) VALUES (?, ?, ?, ?)",
            default_books,
        )

    conn.commit()
    conn.close()


def load_books_from_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT title, category, price, image FROM books ORDER BY title")
    rows = cur.fetchall()
    conn.close()
    return [Book(title, category, price, image) for (title, category, price, image) in rows]


def insert_book_into_db(title: str, category: str, price: float, image: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO books (title, category, price, image) VALUES (?, ?, ?, ?)",
        (title, category, price, image),
    )
    conn.commit()
    conn.close()


# Initialise DB + load books
init_books_db()
BOOKS = load_books_from_db()

###########################################################
# RSS FEED SUPPORT
###########################################################
RSS_SOURCES = {
    "reviews": "https://www.goodreads.com/review/list_rss/1.xml",
    "authors": "https://www.theguardian.com/books/authors/rss",
}


def fetch_rss_items(url: str, limit: int = 5):
    """Return list of RSS entries (safe fallback if feed unavailable)."""
    try:
        feed = feedparser.parse(url)
        return feed.entries[:limit]
    except Exception:
        return []

###########################################################
# GLOBALS / USERS / HELPERS
###########################################################

users = {}
orders = []
cart = Cart()

admin_email = "admin@bookstore.com"
admin_password = "Admin123!"
users[admin_email] = User(admin_email, admin_password, "Admin User", "123 Admin Street", is_admin=True)


demo_email = "demo@bookstore.com"
demo_password = "demo123"
users[demo_email] = User(demo_email, demo_password, "Demo User", "123 Demo Street")


def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrapped(*args, **kwargs):
        if "user_email" not in session:
            flash("Please log in first.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapped


def get_current_user():
    email = session.get("user_email")
    return users.get(email)

###########################################################
# HOME PAGE (BOOK LIST + FILTER + SEARCH + RSS FEEDS)
###########################################################

@app.route("/")
def index():
    global BOOKS
    BOOKS = load_books_from_db()

    current_user = get_current_user()

    selected_category = (request.args.get("category") or "").strip()
    search_query = (request.args.get("q") or "").strip().lower()

    filtered = BOOKS

    if selected_category:
        filtered = [b for b in filtered if b.category.lower() == selected_category.lower()]

    if search_query:
        filtered = [
            b for b in filtered
            if search_query in b.title.lower() or search_query in b.category.lower()
        ]

    categories = sorted({b.category for b in BOOKS})

    # --- RSS FEEDS ---
    reviews_rss_url = "https://www.goodreads.com/review/list_rss/1.xml"
    author_news_rss_url = "https://www.theguardian.com/books/authors/rss"

    reviews_feed = fetch_rss_items(reviews_rss_url, limit=5)
    author_news_feed = fetch_rss_items(author_news_rss_url, limit=5)

    return render_template(
        "index.html",
        books=filtered,
        categories=categories,
        selected_category=selected_category,
        search_query=search_query,
        cart=cart,
        current_user=current_user,
        reviews_feed=reviews_feed,
        author_news_feed=author_news_feed,
    )

###########################################################
# CART ROUTES
###########################################################

@app.route("/cart")
def view_cart():
    """Show the current shopping cart."""
    return render_template("cart.html", cart=cart, current_user=get_current_user())


@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    """
    Add a book to the cart.

    The form on index.html should send:
        - title    (hidden input with the book title)
        - quantity (optional; defaults to 1)
    """
    title = (request.form.get("title") or "").strip()
    qty_raw = request.form.get("quantity") or "1"

    if not title:
        flash("Book title is missing.", "error")
        return redirect(url_for("index"))

    # Find the book in the loaded catalogue
    book = next((b for b in BOOKS if b.title == title), None)
    if not book:
        flash("Book not found.", "error")
        return redirect(url_for("index"))

    # Quantity handling (Cart internally can ignore if not used)
    try:
        quantity = max(1, int(qty_raw))
    except ValueError:
        quantity = 1

    # For this original Cart class, we just add the book once per quantity
    for _ in range(quantity):
        cart.add_item(book)

    flash(f"Added {quantity} × '{book.title}' to your cart!", "success")
    return redirect(url_for("index"))

###########################################################
# CHECKOUT
###########################################################

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    current_user = get_current_user()

    if request.method == "POST":

        shipping = {
            "name": request.form["name"],
            "email": request.form["email"],
            "address": request.form["address"],
            "city": request.form["city"],
            "zip_code": request.form["zip_code"],
        }

        payment_gateway = PaymentGateway()
        email_service = EmailService()

        if not cart.items:
            flash("Your cart is empty.", "error")
            return redirect(url_for("view_cart"))

        total = cart.get_total()
        discount_code = request.form.get("discount_code")
        discount_applied = 0

        if discount_code == "save10":
            discount_applied = total * 0.10
            total -= discount_applied
        elif discount_code == "WELCOME20":
            discount_applied = total * 0.20
            total -= discount_applied
        elif discount_code:
            flash("Invalid discount code", "error")

        payment_result = payment_gateway.process_payment(total)

        if payment_result["success"]:
            order = Order(current_user, cart.items.copy(), total, "completed", discount_applied)
            orders.append(order)
            cart.clear()
            flash("Order placed!", "success")
            return redirect(url_for("index"))
        else:
            flash("Payment failed.", "error")

    return render_template("checkout.html", cart=cart, current_user=current_user)

###########################################################
# ADMIN – ADD BOOKS (WRITES TO SQLITE)
###########################################################

@app.route("/admin", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    current_user = get_current_user()

    if not current_user or current_user.email != admin_email:
        flash("Admins only.", "error")
        return redirect(url_for("index"))

    global BOOKS

    if request.method == "POST":
        title = request.form.get("new_title")
        category = request.form.get("new_category")
        price = request.form.get("new_price")
        image = request.form.get("new_image") or "static/images/default-book.jpg"

        if title and category and price:
            try:
                price = float(price)
                insert_book_into_db(title, category, price, image)
                BOOKS = load_books_from_db()
                flash("Book added!", "success")
            except ValueError:
                flash("Invalid price.", "error")
        else:
            flash("Fill all required fields.", "error")

    return render_template("admin_dashboard.html", books=BOOKS, current_user=current_user)

###########################################################
# AUTH ROUTES
###########################################################

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = users.get(email)
        if user and user.password == password:
            session["user_email"] = email
            flash("Logged in!", "success")
            return redirect(url_for("index"))
        flash("Invalid credentials.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_email", None)
    flash("Logged out.", "success")
    return redirect(url_for("index"))


@app.route("/create-account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        name = request.form["name"]
        address = request.form.get("address", "")

        if email in users:
            flash("Email already exists.", "error")
            return render_template("register.html")

        users[email] = User(email, password, name, address)
        session["user_email"] = email
        flash("Account created!", "success")
        return redirect(url_for("index"))

    return render_template("register.html")

###########################################################
# RUN APP
###########################################################

if __name__ == "__main__":
    app.run(debug=False)

@app.route("/admin/rss", methods=["GET", "POST"])
@login_required
def admin_rss():
    current_user = get_current_user()

    if not current_user or not current_user.is_admin:
        flash("Admins only.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        RSS_SOURCES["reviews"] = request.form.get("reviews_feed")
        RSS_SOURCES["authors"] = request.form.get("authors_feed")
        flash("RSS feeds updated!", "success")

    return render_template("admin_rss.html", rss=RSS_SOURCES)


