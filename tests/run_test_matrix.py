"""
run_test_matrix.py

Simple CLI tool to "use" the manual test matrix for the online bookstore.

Features:
- Shows each test case (ID, Scenario, Steps, Expected Result)
- Prompts for Status (Pass / Fail / Skip) and optional Notes
- Writes results to test_results.csv for use in Excel / reports
"""

import csv
from datetime import datetime

# --- Test Matrix Definition (from your appendix) ---

TEST_CASES = [
    {
        "id": "TC-01",
        "scenario": "User registration – success",
        "steps": "Go to Register → enter valid name/email/password → submit",
        "expected": "New user account created; success message shown; optional auto-login or redirect to login page.",
    },
    {
        "id": "TC-02",
        "scenario": "User registration – validation errors",
        "steps": "Go to Register → leave required fields empty / mismatch passwords → submit",
        "expected": "Form re-displays with clear validation messages; no user created.",
    },
    {
        "id": "TC-03",
        "scenario": "Login with valid credentials",
        "steps": "Go to Login → enter registered email + correct password → submit",
        "expected": "User is authenticated; session created; redirected to home or profile page.",
    },
    {
        "id": "TC-04",
        "scenario": "Login with invalid credentials",
        "steps": "Go to Login → enter wrong password or unknown email → submit",
        "expected": "Login fails; generic error “Invalid email or password”; no session created.",
    },
    {
        "id": "TC-05",
        "scenario": "Browse and search catalogue",
        "steps": "Open Books page → enter keyword in search → submit",
        "expected": "List shows only matching books; “no results” message if none match.",
    },
    {
        "id": "TC-06",
        "scenario": "Add item to cart",
        "steps": "From book listing/detail → click “Add to Cart”",
        "expected": "Cart count increments; cart page shows book with correct title, price, quantity = 1.",
    },
    {
        "id": "TC-07",
        "scenario": "Update cart quantity",
        "steps": "Open Cart → change quantity to 3 → update",
        "expected": "Quantity saved as 3; line subtotal and cart total recalculated correctly.",
    },
    {
        "id": "TC-08",
        "scenario": "Apply valid discount code",
        "steps": "Add items to reach known total → enter valid discount code → apply",
        "expected": "Discount applied once; order total reduced by correct amount/percentage; summary reflects discount.",
    },
    {
        "id": "TC-09",
        "scenario": "Apply invalid/expired discount code",
        "steps": "Add items to cart → enter random/expired code → apply",
        "expected": "Error message shown; discount not applied; totals unchanged.",
    },
    {
        "id": "TC-10",
        "scenario": "Checkout with valid details (mock payment)",
        "steps": "With items in cart → go to Checkout → fill valid address/contact → confirm",
        "expected": "Mock payment succeeds; order recorded; user redirected to confirmation page with order reference.",
    },
    {
        "id": "TC-11",
        "scenario": "Prevent checkout with empty cart",
        "steps": "Ensure cart is empty → navigate directly to `/checkout`",
        "expected": "User redirected to cart or home; message indicates cart is empty; no order created.",
    },
    {
        "id": "TC-12",
        "scenario": "View order history",
        "steps": "Log in as existing customer with prior orders → open “My Orders”",
        "expected": "List of past orders displayed with date, total, status; order detail view shows correct line items.",
    },
    {
        "id": "TC-13",
        "scenario": "Admin adds a new book",
        "steps": "Log in as admin → open Admin → “Add Book” → fill form → submit",
        "expected": "New book appears in catalogue/search with all fields (title, author, price, stock) saved correctly.",
    },
    {
        "id": "TC-14",
        "scenario": "Protect admin routes from normal users",
        "steps": "Log in as normal user → attempt to access an admin URL directly",
        "expected": "Access denied or redirected to login/403 page; no admin UI or actions exposed.",
    },
    {
        "id": "TC-15",
        "scenario": "Performance sanity – large catalogue listing",
        "steps": "Seed ~500–1000 books → open Books page multiple times",
        "expected": "Page loads within agreed time budget (e.g. < 500 ms dev); no obvious timeouts or error responses.",
    },
    {
        "id": "TC-16",
        "scenario": "Security sanity – unauthorised access check",
        "steps": "While logged out → attempt to access cart/checkout/order history URLs",
        "expected": "Redirect to login (for protected pages) or error page; no sensitive data exposed.",
    },
]


def prompt_status() -> str:
    """
    Ask the tester to enter a status for a test case.

    Allowed values: P, F, S (Pass, Fail, Skip)
    """
    while True:
        raw = input("Status [P=Pass / F=Fail / S=Skip]: ").strip().upper()
        if raw in {"P", "F", "S"}:
            return raw
        print("Please enter P, F or S.")


def run_matrix():
    print("=" * 80)
    print("ONLINE BOOKSTORE – MANUAL TEST MATRIX RUNNER")
    print("You will be guided through each test case and asked for a status + optional notes.")
    print("=" * 80)
    print()

    results = []
    started_at = datetime.now_
