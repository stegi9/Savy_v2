"""
Test suite for transaction endpoints.
"""
from datetime import date, timedelta

def test_create_transaction_expense(test_client, auth_headers):
    """Test creating an expense transaction."""
    response = test_client.post(
        "/api/v1/transactions/",
        json={
            "merchant": "Supermarket",
            "amount": 50.0,
            "transaction_type": "expense",
            "date": str(date.today()),
            "description": "Weekly grocery"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["merchant"] == "Supermarket"
    assert data["amount"] == 50.0
    assert data["transaction_type"] == "expense"


def test_create_transaction_income(test_client, auth_headers):
    """Test creating an income transaction."""
    response = test_client.post(
        "/api/v1/transactions/",
        json={
            "merchant": "Salary",
            "amount": 2000.0,
            "transaction_type": "income",
            "date": str(date.today()),
            "description": "Monthly salary"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["merchant"] == "Salary"
    assert data["transaction_type"] == "income"


def test_create_transaction_updates_balance(test_client, auth_headers):
    """Test that creating a transaction updates user balance."""
    # Get initial balance
    user_res = test_client.get("/api/v1/auth/me", headers=auth_headers)
    initial_balance = float(user_res.json()["current_balance"] or 0)
    
    # Create expense
    test_client.post(
        "/api/v1/transactions/",
        json={
            "merchant": "Test",
            "amount": 100.0,
            "transaction_type": "expense",
            "date": str(date.today())
        },
        headers=auth_headers
    )
    
    # Check new balance
    user_res = test_client.get("/api/v1/auth/me", headers=auth_headers)
    new_balance = float(user_res.json()["current_balance"])
    assert new_balance == initial_balance - 100.0


def test_create_transaction_invalid_date(test_client, auth_headers):
    """Test creating transaction with invalid date."""
    response = test_client.post(
        "/api/v1/transactions/",
        json={
            "merchant": "Test",
            "amount": 10.0,
            "date": "invalid-date"
        },
        headers=auth_headers
    )
    assert response.status_code == 422


def test_get_transactions_empty(test_client, auth_headers):
    """Test getting transactions when none exist."""
    response = test_client.get("/api/v1/transactions/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["transactions"]) == 0
    assert data["count"] == 0


def test_get_transactions_list(test_client, auth_headers):
    """Test retrieving list of transactions."""
    # Create 3 transactions with different dates
    dates = [
        date.today() - timedelta(days=2),  # Store 0 (Oldest)
        date.today() - timedelta(days=1),  # Store 1 (Middle)
        date.today()                       # Store 2 (Newest)
    ]
    
    for i in range(3):
        test_client.post(
            "/api/v1/transactions/",
            json={
                "merchant": f"Store {i}",
                "amount": 10.0 * (i+1),
                "date": str(dates[i])
            },
            headers=auth_headers
        )
    
    response = test_client.get("/api/v1/transactions/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["transactions"]) == 3
    # Should be sorted by date DESC: Store 2, Store 1, Store 0
    assert data["transactions"][0]["merchant"] == "Store 2"
    assert data["transactions"][1]["merchant"] == "Store 1"
    assert data["transactions"][2]["merchant"] == "Store 0"


def test_get_transactions_limit(test_client, auth_headers):
    """Test pagination limit."""
    # Create 5 transactions
    for i in range(5):
        test_client.post(
            "/api/v1/transactions/",
            json={
                "merchant": f"Store {i}",
                "amount": 10.0,
                "date": str(date.today())
            },
            headers=auth_headers
        )
    
    response = test_client.get("/api/v1/transactions/?limit=2", headers=auth_headers)
    data = response.json()["data"]
    assert len(data["transactions"]) == 2


def test_update_category(test_client, auth_headers):
    """Test updating transaction category."""
    # Create transaction
    create_res = test_client.post(
        "/api/v1/transactions/",
        json={
            "merchant": "Unknown Store",
            "amount": 25.0,
            "date": str(date.today())
        },
        headers=auth_headers
    )
    tx_id = create_res.json()["data"]["id"]
    
    # Create category first (or assume one exists, but safet to create)
    # Using 'Shopping' which should be a default or we mock it
    # Ideally should fetch categories or create one.
    # Let's verify we can update with an arbitrary ID for now or create one.
    
    # Create category
    cat_res = test_client.post(
        "/api/v1/categories/",
        json={"name": "Test Category", "color": "#123456", "icon": "test"},
        headers=auth_headers
    )
    cat_id = cat_res.json()["id"]
    
    # Update
    response = test_client.patch(
        f"/api/v1/transactions/{tx_id}/category",
        json={"category_id": cat_id},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert response.json()["data"]["category_id"] == cat_id


def test_update_category_transaction_not_found(test_client, auth_headers):
    """Test updating invalid transaction."""
    response = test_client.patch(
        "/api/v1/transactions/999999/category",
        json={"category_id": "any"},
        headers=auth_headers
    )
    assert response.status_code == 404


def test_delete_transaction(test_client, auth_headers):
    """Test deleting a transaction."""
    # Create
    create_res = test_client.post(
        "/api/v1/transactions/",
        json={
            "merchant": "To Delete",
            "amount": 50.0,
            "date": str(date.today())
        },
        headers=auth_headers
    )
    tx_id = create_res.json()["data"]["id"]
    
    # Delete
    response = test_client.delete(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify gone
    list_res = test_client.get("/api/v1/transactions/", headers=auth_headers)
    assert len(list_res.json()["data"]["transactions"]) == 0


def test_delete_transaction_restores_balance(test_client, auth_headers):
    """Test that deleting an expense restores balance."""
    # Get initial
    user_res = test_client.get("/api/v1/auth/me", headers=auth_headers)
    initial_balance = float(user_res.json()["current_balance"] or 0)
    
    # Create expense (balance - 50)
    create_res = test_client.post(
        "/api/v1/transactions/",
        json={
            "merchant": "To Delete",
            "amount": 50.0,
            "transaction_type": "expense",
            "date": str(date.today())
        },
        headers=auth_headers
    )
    tx_id = create_res.json()["data"]["id"]
    
    # Verify deduction
    user_res = test_client.get("/api/v1/auth/me", headers=auth_headers)
    mid_balance = float(user_res.json()["current_balance"])
    assert mid_balance == initial_balance - 50.0
    
    # Delete (balance + 50)
    test_client.delete(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    
    # Verify restoration
    user_res = test_client.get("/api/v1/auth/me", headers=auth_headers)
    final_balance = float(user_res.json()["current_balance"])
    assert final_balance == initial_balance


def test_delete_income_subtacts_balance(test_client, auth_headers):
    """Test that deleting an income reduces balance."""
    # Get initial
    user_res = test_client.get("/api/v1/auth/me", headers=auth_headers)
    initial_balance = float(user_res.json()["current_balance"] or 0)
    
    # Create income (balance + 100)
    create_res = test_client.post(
        "/api/v1/transactions/",
        json={
            "merchant": "Income",
            "amount": 100.0,
            "transaction_type": "income",
            "date": str(date.today())
        },
        headers=auth_headers
    )
    tx_id = create_res.json()["data"]["id"]
    
    user_res = test_client.get("/api/v1/auth/me", headers=auth_headers)
    assert float(user_res.json()["current_balance"]) == initial_balance + 100
    
    # Delete
    test_client.delete(f"/api/v1/transactions/{tx_id}", headers=auth_headers)
    
    # Verify return
    user_res = test_client.get("/api/v1/auth/me", headers=auth_headers)
    assert float(user_res.json()["current_balance"]) == initial_balance


def test_delete_transaction_not_found(test_client, auth_headers):
    """Test deleting non-existent transaction."""
    response = test_client.delete("/api/v1/transactions/99999", headers=auth_headers)
    assert response.status_code == 404


def test_get_transactions_filtered_by_date(test_client, auth_headers):
    """Test getting transactions filtered by date range."""
    # Create past, present, future transactions
    dates = [
        date.today() - timedelta(days=10),
        date.today(),
        date.today() + timedelta(days=10)
    ]
    
    for d in dates:
        test_client.post(
            "/api/v1/transactions/",
            json={"merchant": "Filter Test", "amount": 10.0, "date": str(d)},
            headers=auth_headers
        )
        
    # Filter for today only
    start_date = str(date.today())
    end_date = str(date.today())
    
    response = test_client.get(
        f"/api/v1/transactions/?start_date={start_date}&end_date={end_date}",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    expected_count = 1
    # Note: Pagination defaults might apply, but we expect at least the one from today
    # Assuming repository handles date filters properly which we see in transaction_repository.py
    data = response.json()["data"]
    
    # We might need to check how the controller implements filtering.
    # If parameters exist in controller. Let's assume they do or repository supports it.
    # Based on report_service modification, we know reports support it. 
    # Transaction controller `get_user_transactions` usually supports filters. 
    # If not, this test might fail or return all.
    # Let's inspect controller later if it fails. 
    # For now, let's just assert we get what we expect or skip if feature is missing.
    # Wait, the controller code was not fully shown.
    
    # Re-reading: The user objective included "reports" date ranges.
    # If transaction controller doesn't support it, I should implement it or test something else.
    # Let's verify transaction_controller.py first.
