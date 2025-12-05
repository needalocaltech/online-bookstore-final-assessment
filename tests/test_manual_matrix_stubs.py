"""
Pytest stubs mapped 1:1 to the manual test matrix.

These are placeholders that:
- Document each test case (Scenario, Steps, Expected Result).
- Can later be converted into fully automated tests using the Flask test client.

For now, they are marked as 'manual' and skipped, but the structure
makes it clear how each TC maps into your automated suite.
"""

import pytest


@pytest.mark.manual
def test_tc01_user_registration_success():
    """
    TC-01 – User registration – success

    Steps:
      1. Go to Register.
      2. Enter valid name, email, and strong password.
      3. Submit the form.

    Expected:
      - New user account created.
      - Success message displayed.
      - Optional auto-login or redirect to login page.
    """
    pytest.skip("Manual/placeholder: implement automated registration happy-path test.")


@pytest.mark.manual
def test_tc02_user_registration_validation_errors():
    """
    TC-02 – User registration – validation errors

    Steps:
      1. Go to Register.
      2. Leave required fields empty or use mismatched passwords.
      3. Submit the form.

    Expected:
      - Form re-renders with clear validation messages.
      - No new user account is created.
    """
    pytest.skip("Manual/placeholder: implement registration validation tests.")


@pytest.mark.manual
def test_tc03_login_with_valid_credentials():
    """
    TC-03 – Login with valid credentials

    Steps:
      1. Go to Login.
      2. Enter registered email and correct password.
      3. Submit the form.

    Expected:
      - User is authenticated.
      - Session created.
      - Redirect to home or profile page.
    """
    pytest.skip("Manual/placeholder: implement login success test.")


@pytest.mark.manual
def test_tc04_login_with_invalid_credentials():
    """
    TC-04 – Login with invalid credentials

    Steps:
      1. Go to Login.
      2. Enter wrong password or unknown email.
      3. Submit the form.

    Expected:
      - Login fails.
      - Generic error message ('Invalid email or password').
      - No session created.
    """
    pytest.skip("Manual/placeholder: implement login failure test.")


@pytest.mark.manual
def test_tc05_browse_and_search_catalogue():
    """
    TC-05 – Browse and search catalogue

    Steps:
      1. Open Books page.
      2. Enter keyword into search.
      3. Submit.

    Expected:
      - Result list only shows matching books.
      - 'No results' message if none match.
    """
    pytest.skip("Manual/placeholder: implement catalogue search test.")


@pytest.mark.manual
def test_tc06_add_item_to_cart():
    """
    TC-06 – Add item to cart

    Steps:
      1. From book listing or detail page, click 'Add to Cart'.

    Expected:
      - Cart count increments.
      - Cart page shows book with correct title, price, and quantity = 1.
    """
    pytest.skip("Manual/placeholder: implement add-to-cart test.")


@pytest.mark.manual
def test_tc07_update_cart_quantity():
    """
    TC-07 – Update cart quantity

    Steps:
      1. Open Cart.
      2. Change quantity to 3.
      3. Update cart.

    Expected:
      - Quantity stored as 3.
      - Line subtotal and total recalculated correctly.
    """
    pytest.skip("Manual/placeholder: implement cart quantity update test.")


@pytest.mark.manual
def test_tc08_apply_valid_discount_code():
    """
    TC-08 – Apply valid discount code

    Steps:
      1. Add items to reach known total (e.g. £100).
      2. Enter valid discount code.
      3. Apply.

    Expected:
      - Discount applied once.
      - Total reduced by correct amount or percentage.
      - Summary clearly reflects discount.
    """
    pytest.skip("Manual/placeholder: implement discount application test.")


@pytest.mark.manual
def test_tc09_apply_invalid_discount_code():
    """
    TC-09 – Apply invalid/expired discount code

    Steps:
      1. Add items to cart.
      2. Enter random or expired discount code.
      3. Apply.

    Expected:
      - Clear error message.
      - Discount not applied.
      - Totals unchanged.
    """
    pytest.skip("Manual/placeholder: implement invalid discount test.")


@pytest.mark.manual
def test_tc10_checkout_with_valid_details():
    """
    TC-10 – Checkout with valid details (mock payment)

    Steps:
      1. Ensure cart contains items.
      2. Go to Checkout.
      3. Fill valid address/contact details.
      4. Confirm order.

    Expected:
      - Mock payment succeeds.
      - Order recorded.
      - Redirect to confirmation page with order reference.
    """
    pytest.skip("Manual/placeholder: implement happy-path checkout test.")


@pytest.mark.manual
def test_tc11_prevent_checkout_with_empty_cart():
    """
    TC-11 – Prevent checkout with empty cart

    Steps:
      1. Empty the cart.
      2. Navigate directly to /checkout.

    Expected:
      - User redirected to cart or home.
      - Message indicates cart is empty.
      - No order created.
    """
    pytest.skip("Manual/placeholder: implement empty-cart checkout protection test.")


@pytest.mark.manual
def test_tc12_view_order_history():
    """
    TC-12 – View order history

    Steps:
      1. Log in as customer with previous orders.
      2. Open 'My Orders' page.

    Expected:
      - List of past orders displayed (date, total, status).
      - Order detail view shows correct line items.
    """
    pytest.skip("Manual/placeholder: implement order history test.")


@pytest.mark.manual
def test_tc13_admin_adds_new_book():
    """
    TC-13 – Admin adds a new book

    Steps:
      1. Log in as admin.
      2. Open Admin dashboard.
      3. Click 'Add Book', fill form, submit.

    Expected:
      - New book appears in catalogue/search.
      - Fields (title, genre, price, image) saved correctly.
    """
    pytest.skip("Manual/placeholder: implement admin add-book test.")


@pytest.mark.manual
def test_tc14_protect_admin_routes_from_normal_users():
    """
    TC-14 – Protect admin routes from normal users

    Steps:
      1. Log in as normal (non-admin) user.
      2. Attempt to access an admin URL directly.

    Expected:
      - Access denied or redirect to login/403 page.
      - No admin UI or actions exposed.
    """
    pytest.skip("Manual/placeholder: implement admin access control test.")


@pytest.mark.manual
def test_tc15_performance_sanity_large_catalogue():
    """
    TC-15 – Performance sanity – large catalogue listing

    Steps:
      1. Seed ~500–1000 books.
      2. Open Books page multiple times.

    Expected:
      - Page loads within agreed time (e.g. < 500 ms dev).
      - No obvious timeouts or server errors.
    """
    pytest.skip("Manual/placeholder: implement performance/load test or profiling script.")


@pytest.mark.manual
def test_tc16_security_unauthorised_access_check():
    """
    TC-16 – Security sanity – unauthorised access check

    Steps:
      1. While logged out, attempt to access protected URLs
         (e.g. /checkout, /my-orders, /admin).
    """
    from app import app
    from app import test_client

def test_tc01_user_registration_success(client):
    # client can be a pytest fixture using app.test_client()
    resp = client.post("/register", data={
        "email": "newuser@example.com",
        "password": "StrongPass123!",
        "name": "New User",
    }, follow_redirects=True)

    assert resp.status_code == 200
    assert b"Registration successful" in resp.data

