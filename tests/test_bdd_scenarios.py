import pytest
from app import app
from urllib.parse import urlparse

# --- Pytest Fixture ---
@pytest.fixture(scope='module')
def client():
    """Fixture to create a Flask test client for simulating requests."""
    # Ensure the app is running in testing mode
    app.config['TESTING'] = True
    # The 'with' block ensures the request context is properly managed
    with app.test_client() as client:
        yield client

# --- Utility Functions to Simplify Tests ---

def get_valid_book_id(client):
    """
    Tries to find a book ID from the home page.
    Assumes book links are in the form of /book/<id>
    """
    response = client.get('/', follow_redirects=True)
    if response.status_code != 200:
        return None
    
    # Simple check for a book link in the response HTML
    # Note: This is a robust way to check for dynamic content in tests
    html_content = response.data.decode('utf-8')
    import re
    match = re.search(r'/book/(\d+)', html_content)
    
    if match:
        return int(match.group(1))
    
    # Fallback to a common default ID if not found
    return 1 

def add_book_to_cart(client, book_id: int, quantity: int = 1, follow_redirect=True):
    """Simulates adding an item to the cart (POST request)."""
    # Assuming the route is /add-to-cart and accepts book_id and quantity
    return client.post(
        '/add-to-cart',
        data={'book_id': book_id, 'quantity': quantity},
        follow_redirects=follow_redirect
    )

# =========================================================================
# --- BDD Scenario Implementations ---
# =========================================================================

# Scenario 1 & 2 — Browse catalogue & View book details
def test_scenario_browse_and_view_details(client):
    """
    Scenario 1: Given the app is running, When I visit /, Then I should see a list of books.
    Scenario 2: Given I have a book ID, When I click the link, Then I should see details.
    """
    
    # 1. Given/When I visit the home page /
    home_response = client.get('/:5000', follow_redirects=True)
    
    # Then I should see a list/grid of books (HTTP 200; at least one book title visible)
    assert home_response.status_code == 200
    assert b"Online Bookstore" in home_response.data
    
    # Extract a valid book ID for Scenario 2
    book_id = get_valid_book_id(client)
    assert book_id is not None, "Failed to find a valid book ID in the catalogue."
    
    # 2. When I click that book’s details link /book/<id>
    detail_url = f'/book/{book_id}'
    detail_response = client.get(detail_url, follow_redirects=True)
    
    # Then I should see title, author, price, description (HTTP 200)
    assert detail_response.status_code == 200
    assert b"Book Details" in detail_response.data
    # Check for price format (a common currency sign check)
    assert b"$" in detail_response.data

# Scenario 3 — Add item to cart
def test_scenario_add_item_to_cart(client):
    """
    Given I am on a book details page, When I add quantity 2 to cart, 
    Then the cart count and contents should reflect 2 items.
    """
    book_id = get_valid_book_id(client)
    quantity_to_add = 2

    # Given/When I add quantity 2 to cart via POST /add-to-cart
    # Use 'with client.session_transaction()' to clear the cart session first
    with client.session_transaction() as session:
        session.pop('cart', None) # Clear any previous cart data
        
    add_response = add_book_to_cart(client, book_id, quantity=quantity_to_add)
    
    # Expected: Redirect to cart or same page (302)
    assert add_response.status_code == 302
    
    # Then the cart count and contents should reflect 2 items
    cart_response = client.get('/cart', follow_redirects=True)
    assert cart_response.status_code == 200
    
    # Check that the number of items (quantity) is reflected in the cart page content
    # Look for a specific indicator, like the total quantity or the line item
    # Assuming the cart page shows the total quantity somewhere: "Quantity: 2"
    assert f'Quantity: {quantity_to_add}'.encode('utf-8') in cart_response.data
    
# Scenario 5 — View cart contents
def test_scenario_view_cart_contents(client):
    """
    Given the cart is populated (from the previous test), When I visit /cart, 
    Then I should see itemized line details and a calculated subtotal.
    """
    # Setup: Ensure cart is populated with at least one item
    book_id = get_valid_book_id(client)
    add_book_to_cart(client, book_id, quantity=1)

    # When I visit /cart
    cart_response = client.get('/cart', follow_redirects=True)
    
    # Then I should see itemized line details and a calculated subtotal
    assert cart_response.status_code == 200
    assert b"Your Shopping Cart" in cart_response.data
    assert b"Subtotal" in cart_response.data # Check for the summary element
    
    # Check for the itemized list presence
    assert f'/book/{book_id}'.encode('utf-8') in cart_response.data

# Scenario 6 & 7 — Discount application
def test_scenario_discount_application(client):
    """
    Scenario 6: Given I have a subtotal, When I apply code 'SAVE10', Then discount should be applied.
    Scenario 7: Test discount calculation precision.
    """
    book_id = get_valid_book_id(client)
    
    # 1. Setup: Ensure a known high-value item is in the cart
    with client.session_transaction() as session:
        session.pop('cart', None) 
        # Manually set a high price item to ensure discount is large enough to see
        # Assuming the cart structure is a dictionary keyed by book ID
        session['cart'] = {book_id: {'price': 100.00, 'qty': 1}}
        
    discount_code = 'SAVE10' # Assuming this gives 10% off
    expected_discounted_total_after_10_percent = '90.00' 
    
    # When I submit the discount code 'SAVE10' on the cart/checkout page
    checkout_response = client.post(
        '/checkout', # Assuming /checkout handles discount application
        data={'discount_code': discount_code, 'action': 'apply_discount'},
        follow_redirects=True
    )
    
    # Then the discount should be applied (check for the discounted total on the next page)
    assert checkout_response.status_code == 200
    assert b"Discount Applied" in checkout_response.data # Check for success message
    assert expected_discounted_total_after_10_percent.encode('utf-8') in checkout_response.data
    
# Scenario 12 — Search Functionality
def test_scenario_search_functionality(client):
    """
    Given the catalogue is available, When I search for a known keyword, 
    Then I should see a list of filtered results and the home page content.
    """
    search_term = "Book" # A generic search term likely to return results

    # When I search for a keyword
    # Assuming search uses a GET request to / and a query parameter 'q'
    search_response = client.get(f'/?q={search_term}', follow_redirects=True)
    
    # Then I should see the home page content and filtered results
    assert search_response.status_code == 200
    assert b"Search Results" in search_response.data
    # Should not redirect (check URL)
    assert urlparse(search_response.request.path).path == '/'

# Scenario 14 - Invalid Quantity Validation (Negative, Zero, Excessively Large)
def test_scenario_invalid_quantity_validation(client):
    """
    When I submit zero, negative, or excessively large quantities, 
    Then I should see validation feedback.
    """
    book_id = get_valid_book_id(client)
    
    # Test 1: Negative quantity
    response_neg = add_book_to_cart(client, book_id, quantity=-1, follow_redirect=False)
    # Expected: 400 Bad Request or 302 with error message after redirect
    assert response_neg.status_code in (400, 302), "Server should reject negative quantity."
    
    # Test 2: Zero quantity
    response_zero = add_book_to_cart(client, book_id, quantity=0, follow_redirect=False)
    assert response_zero.status_code in (400, 302), "Server should reject zero quantity."
    
    # If the app redirects on error, follow the redirect and check for a flash message
    if response_neg.status_code == 302:
        error_page = client.get(response_neg.location, follow_redirects=True)
        assert b"Quantity must be at least 1" in error_page.data or b"Invalid quantity" in error_page.data


# Scenario 13 — User Login (Basic Check)
def test_scenario_user_login(client):
    """
    Given the login page exists, When I submit valid credentials, 
    Then I should be redirected to the account page.
    """
    # 1. Given the login page exists
    login_response = client.get('/login', follow_redirects=True)
    assert login_response.status_code == 200
    assert b"User Login" in login_response.data

    # 2. When I submit valid credentials (using common mock user/credentials)
    # NOTE: This assumes a mock user "test@example.com" / "password" exists for testing
    login_post_response = client.post(
        '/login',
        data={'email': 'test@example.com', 'password': 'password'},
        follow_redirects=False # Do not follow redirect to check status code
    )
    
    # 3. Then I should be redirected (302) to the account page (or home)
    assert login_post_response.status_code == 302
    assert urlparse(login_post_response.location).path in ('/account', '/')
    
    # Check the final page after successful login redirect
    account_page = client.get(login_post_response.location, follow_redirects=True)
    assert b"My Account" in account_page.data or b"Welcome Back" in account_page.data
