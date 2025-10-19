import pytest
# from models_0 import calculate_discounted_price  # Imports the consolidated pricing function
from models import compute_cart_totals  # Imports the consolidated pricing function

# Mock Inventory Item (Price is $100.00)
@pytest.fixture
def mock_item():
    return {'price': 100.00, 'quantity': 1}

def test_fixed_amount_discount(mock_item):
    """Tests a fixed dollar amount discount (e.g., $10 off)."""
    # Arrange: $100.00 - $10.00 fixed discount
    discount_amount = 10.00
    expected_price = 90.00
    
    # Act
    # We pass the fixed discount amount to the function
    # actual_price = calculate_discounted_price(mock_item['price'], fixed_discount=discount_amount)
    actual_price = compute_cart_totals (mock_item['price'], fixed_discount=discount_amount)

    # Assert
    assert actual_price == expected_price

def test_percentage_discount(mock_item):
    """Tests a percentage discount (e.g., 20% off)."""
    # Arrange: $100.00 * 0.80 = $80.00
    discount_percent = 0.20
    expected_price = 80.00
    
    # Act
    # We pass the percentage discount rate to the function
    actual_price = compute_cart_totals(mock_item['price'], percentage_discount=discount_percent)
    
    # Assert
    assert actual_price == expected_price

def test_no_discount_applied(mock_item):
    """Ensures price remains unchanged if no discount is provided."""
    # Act
    # Call with no discount parameters
    actual_price = compute_cart_totals(mock_item['price'])
    
    # Assert
    assert actual_price == mock_item['price']

def test_discount_with_rounding():
    """Tests correct rounding behavior for discounts."""
    # Arrange: Price $19.99, 10% discount ($1.999 off) -> $17.991, should round down to $17.99
    price = 19.99
    discount_percent = 0.10
    expected_price = 17.99
    
    # Act
    # actual_price = calculate_discounted_price(price, percentage_discount=discount_percent)
    actual_price = compute_cart_totals(price, percentage_discount=discount_percent)


    # Assert
    # We round the assertion result to 2 decimal places to account for floating point math
    assert round(actual_price, 2) == expected_price
