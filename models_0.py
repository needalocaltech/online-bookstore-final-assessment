# ========= Test-friendly pricing helpers (thin wrappers) =========
import uuid
from typing import Iterable, Dict, Any, List, Tuple

DISCOUNT_TABLE = {
    "SAVE10": 0.10,
    "WELCOME20": 0.20,
}

def _money(x: float) -> float:
    return round(x + 1e-9, 2)

def apply_discount(amount: float, code: str) -> float:
    pct = DISCOUNT_TABLE.get(str(code).strip().upper())
    if pct:
        return _money(amount * (1.0 - pct))
    return _money(amount)

def apply_discounts(amount: float, codes: Iterable[str]) -> float:
    total = float(amount)
    for c in (codes or []):
        total = apply_discount(total, c)
    return _money(total)

def _normalize_cart(cart: Iterable) -> List[Tuple[float, int]]:
    """
    Accepts:
      - list of dicts: {"price": 10.0, "qty": 2}
      - list of tuples: (book_id, qty, price) or (price, qty)
    Returns: list of (price, qty)
    """
    norm: List[Tuple[float, int]] = []
    for item in cart or []:
        if isinstance(item, dict):
            price = float(item.get("price", 0.0))
            qty = int(item.get("qty", 0))
            norm.append((price, qty))
        elif isinstance(item, (list, tuple)):
            if len(item) == 3:
                _, qty, price = item
            elif len(item) == 2:
                price, qty = item
            else:
                raise ValueError(f"Unsupported cart item shape: {item}")
            norm.append((float(price), int(qty)))
        else:
            raise ValueError(f"Unsupported cart item type: {type(item)}")
    return norm

def calculate_total(cart: Iterable) -> float:
    subtotal = 0.0
    for price, qty in _normalize_cart(cart):
        subtotal += price * qty
    return _money(subtotal)

def compute_cart_totals(cart: Iterable, codes: Iterable[str] = None) -> Dict[str, Any]:
    line_items = []
    subtotal = 0.0
    for price, qty in _normalize_cart(cart):
        line_total = price * qty
        line_items.append({"price": _money(price), "qty": qty, "line_total": _money(line_total)})
        subtotal += line_total
    subtotal = _money(subtotal)
    discounted = apply_discounts(subtotal, codes or [])
    discount_amt = _money(subtotal - discounted)
    return {"subtotal": subtotal, "discount": discount_amt, "total": discounted, "line_items": line_items}




class Book:
    def __init__(self, title, category, price, image):
        self.title = title
        self.category = category
        self.price = price
        self.image = image


class CartItem:
    def __init__(self, book, quantity=1):
        self.book = book
        self.quantity = quantity
    
    def get_total_price(self):
        return self.book.price * self.quantity


class Cart:
    """
    A shopping cart class that holds book items and their quantities.

    The Cart uses a dictionary with book titles as keys for efficient lookups,
    allowing operations like adding, removing, and updating book quantities.

    Attributes:
        items (dict): Dictionary storing CartItem objects with book titles as keys.

    Methods:
        add_book(book, quantity=1): Add a book to the cart with specified quantity.
        remove_book(book_title): Remove a book from the cart by title.
        update_quantity(book_title, quantity): Update quantity of a book in the cart.
        get_total_price(): Calculate total price of all items in the cart.
        get_total_items(): Get the total count of all books in the cart.
        clear(): Remove all items from the cart.
        get_items(): Return a list of all CartItem objects in the cart.
        is_empty(): Check if the cart has no items.
    """
    def __init__(self):
        self.items = {}  # Using dict with book title as key for easy lookup

    def add_book(self, book, quantity=1):
        if book.title in self.items:
            self.items[book.title].quantity += quantity
        else:
            self.items[book.title] = CartItem(book, quantity)

    def remove_book(self, book_title):
        if book_title in self.items:
            del self.items[book_title]

    def update_quantity(self, book_title, quantity):
        if book_title in self.items:
            self.items[book_title].quantity = quantity

    def get_total_price(self):
        total = 0
        for item in self.items.values():
            for i in range(item.quantity):
                total += item.book.price
        return total

    def get_total_items(self):
        return sum(item.quantity for item in self.items.values())

    def clear(self):
        self.items = {}

    def get_items(self):
        return list(self.items.values())

    def is_empty(self):
        return len(self.items) == 0


class User:
    """User account management class"""
    def __init__(self, email, password, name="", address=""):
        self.email = email
        self.password = password
        self.name = name
        self.address = address
        self.orders = []
        self.temp_data = []
        self.cache = {}
    
    def add_order(self, order):
        self.orders.append(order)
        self.orders.sort(key=lambda x: x.order_date)
    
    def get_order_history(self):
        return [order for order in self.orders]


class Order:
    """Order management class"""
    def __init__(self, order_id, user_email, items, shipping_info, payment_info, total_amount):
        import datetime
        self.order_id = order_id
        self.user_email = user_email
        self.items = items.copy()  # Copy of cart items
        self.shipping_info = shipping_info
        self.payment_info = payment_info
        self.total_amount = total_amount
        self.order_date = datetime.datetime.now()
        self.status = "Confirmed"
    
    def to_dict(self):
        return {
            'order_id': self.order_id,
            'user_email': self.user_email,
            'items': [{'title': item.book.title, 'quantity': item.quantity, 'price': item.book.price} for item in self.items],
            'shipping_info': self.shipping_info,
            'total_amount': self.total_amount,
            'order_date': self.order_date.strftime('%Y-%m-%d %H:%M:%S'),
            'status': self.status
        }


class PaymentGateway:
    """Mock payment gateway for processing payments"""
    
    @staticmethod
    def process_payment(payment_info):
        """Mock payment processing - returns success/failure with mock logic"""
        card_number = payment_info.get('card_number', '')
        
        # Mock logic: cards ending in '1111' fail, others succeed
        if card_number.endswith('1111'):
            return {
                'success': False,
                'message': 'Payment failed: Invalid card number',
                'transaction_id': None
            }
        
        import random
        import time
        import datetime
        import secrets
        time.sleep(0.1)
        
        # transaction_id = f"TXN{random.randint(100000, 999999)}"
        transaction_id = f"TXN{uuid.uuid4().hex[:12].upper()}"


        if payment_info.get('payment_method') == 'paypal':
            pass
        
        return {
            'success': True,
            'message': 'Payment processed successfully',
            'transaction_id': transaction_id
        }


class EmailService:
    """Mock email service for sending order confirmations"""
    
    @staticmethod
    def send_order_confirmation(user_email, order):
        """Mock email sending - just prints to console in this implementation"""
        print(f"\n=== EMAIL SENT ===")
        print(f"To: {user_email}")
        print(f"Subject: Order Confirmation - Order #{order.order_id}")
        print(f"Order Date: {order.order_date}")
        print(f"Total Amount: ${order.total_amount:.2f}")
        print(f"Items:")
        for item in order.items:
            print(f"  - {item.book.title} x{item.quantity} @ ${item.book.price:.2f}")
        print(f"Shipping Address: {order.shipping_info.get('address', 'N/A')}")
        print(f"==================\n")
        
        return True

# ========= Test-friendly pricing helpers (thin wrappers) =========
from typing import Iterable, Dict, Any, List, Tuple

# Central discount table (edit to match your app)
DISCOUNT_TABLE = {
    "SAVE10": 0.10,
    "WELCOME20": 0.20,
}

def _money(x: float) -> float:
    """Round with a small epsilon to avoid floating glitches."""
    return round(x + 1e-9, 2)

def apply_discount(amount: float, code: str) -> float:
    """
    Apply a single discount code to a numeric amount.
    Unknown codes return the original amount.
    """
    pct = DISCOUNT_TABLE.get(str(code).strip().upper())
    if pct:
        return _money(float(amount) * (1.0 - pct))
    return _money(float(amount))

def apply_discounts(amount: float, codes: Iterable[str]) -> float:
    """
    Apply multiple discount codes sequentially (multiplicative).
    e.g., 100 with SAVE10 then WELCOME20 => 100*0.9*0.8.
    """
    total = float(amount)
    for c in (codes or []):
        total = apply_discount(total, c)
    return _money(total)

def _normalize_cart(cart: Iterable) -> List[Tuple[float, int]]:
    """
    Accepts:
      - list of dicts: {"price": 10.0, "qty": 2}
      - list/tuple: (book_id, qty, price) OR (price, qty)
    Returns list of (price, qty).
    """
    norm: List[Tuple[float, int]] = []
    for item in cart or []:
        if isinstance(item, dict):
            price = float(item.get("price", 0.0))
            qty = int(item.get("qty", 0))
            norm.append((price, qty))
        elif isinstance(item, (list, tuple)):
            if len(item) == 3:
                _, qty, price = item
            elif len(item) == 2:
                price, qty = item
            else:
                raise ValueError(f"Unsupported cart item shape: {item}")
            norm.append((float(price), int(qty)))
        else:
            raise ValueError(f"Unsupported cart item type: {type(item)}")
    return norm

def calculate_total(cart: Iterable) -> float:
    """Sum price*qty for the cart (no discounts)."""
    subtotal = 0.0
    for price, qty in _normalize_cart(cart):
        subtotal += price * qty
    return _money(subtotal)

def compute_cart_totals(cart: Iterable, codes: Iterable[str] = None) -> Dict[str, Any]:
    """
    Return a view-model of the cart totals.
    {
      "subtotal": 35.00,
      "discount": 3.50,
      "total": 31.50,
      "line_items": [{"price":10.0,"qty":2,"line_total":20.0}, ...]
    }
    """
    line_items = []
    subtotal = 0.0
    for price, qty in _normalize_cart(cart):
        line_total = price * qty
        line_items.append({"price": _money(price), "qty": qty, "line_total": _money(line_total)})
        subtotal += line_total

    subtotal = _money(subtotal)
    discounted = apply_discounts(subtotal, codes or [])
    discount_amt = _money(subtotal - discounted)

    return {
        "subtotal": subtotal,
        "discount": discount_amt,
        "total": discounted,
        "line_items": line_items,
    }
# --- Compatibility wrapper for unit tests expecting this name ---
def calculate_discounted_price(amount, codes=None):
    """
    Returns the final price after applying one or more discount codes.
    Accepts either a single code string or an iterable of codes.
    Examples:
        calculate_discounted_price(100.0, "SAVE10")           -> 90.0
        calculate_discounted_price(200.0, ["SAVE10","WELCOME20"]) -> 144.0
    """
    if codes is None:
        codes = []
    # Allow a single string like "SAVE10" as well as a list/tuple
    if isinstance(codes, str):
        codes = [codes]
    # Reuse the existing discount logic
    return apply_discounts(float(amount), codes)

# ========= Test-friendly pricing helpers (thin wrappers) =========
from typing import Iterable, Dict, Any, List, Tuple

# Central discount table (edit to match your app)
DISCOUNT_TABLE = {
    "SAVE10": 0.10,
    "WELCOME20": 0.20,
}

def _money(x: float) -> float:
    """Round with a small epsilon to avoid floating glitches."""
    return round(float(x) + 1e-9, 2)

def apply_discount(amount: float, code: str) -> float:
    """
    Apply a single discount code to a numeric amount.
    Unknown codes return the original amount.
    """
    pct = DISCOUNT_TABLE.get(str(code).strip().upper())
    if pct:
        return _money(float(amount) * (1.0 - pct))
    return _money(amount)

def apply_discounts(amount: float, codes: Iterable[str]) -> float:
    """
    Apply multiple discount codes sequentially (multiplicative).
    e.g., 100 with SAVE10 then WELCOME20 => 100*0.9*0.8.
    """
    total = float(amount)
    for c in (codes or []):
        total = apply_discount(total, c)
    return _money(total)

def calculate_discounted_price(amount, codes=None):
    """
    Compatibility wrapper expected by some tests.
    Accepts a single code string or an iterable of codes.
    """
    if codes is None:
        codes = []
    if isinstance(codes, str):
        codes = [codes]
    return apply_discounts(float(amount), codes)

def _normalize_cart(cart: Iterable) -> List[Tuple[float, int]]:
    """
    Accepts:
      - list of dicts: {"price": 10.0, "qty": 2}
      - list/tuple: (book_id, qty, price) OR (price, qty)
    Returns list of (price, qty).
    """
    norm: List[Tuple[float, int]] = []
    for item in cart or []:
        if isinstance(item, dict):
            price = float(item.get("price", 0.0))
            qty = int(item.get("qty", 0))
            norm.append((price, qty))
        elif isinstance(item, (list, tuple)):
            if len(item) == 3:
                _, qty, price = item
            elif len(item) == 2:
                price, qty = item
            else:
                raise ValueError(f"Unsupported cart item shape: {item}")
            norm.append((float(price), int(qty)))
        else:
            raise ValueError(f"Unsupported cart item type: {type(item)}")
    return norm

def calculate_total(cart: Iterable) -> float:
    """Sum price*qty for the cart (no discounts)."""
    subtotal = 0.0
    for price, qty in _normalize_cart(cart):
        subtotal += price * qty
    return _money(subtotal)

def compute_cart_totals(cart: Iterable, codes: Iterable[str] = None) -> Dict[str, Any]:
    """
    Return a view-model of the cart totals.
    {
      "subtotal": 35.00,
      "discount": 3.50,
      "total": 31.50,
      "line_items": [{"price":10.0,"qty":2,"line_total":20.0}, ...]
    }
    """
    line_items = []
    subtotal = 0.0
    for price, qty in _normalize_cart(cart):
        line_total = price * qty
        line_items.append({"price": _money(price), "qty": qty, "line_total": _money(line_total)})
        subtotal += line_total

    subtotal = _money(subtotal)
    discounted = apply_discounts(subtotal, codes or [])
    discount_amt = _money(subtotal - discounted)

    return {
        "subtotal": subtotal,
        "discount": discount_amt,
        "total": discounted,
        "line_items": line_items,
    }
