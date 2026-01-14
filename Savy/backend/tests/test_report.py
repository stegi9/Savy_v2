"""
Test suite for report and analytics endpoints.
"""
from datetime import date, timedelta

def test_spending_report_empty(test_client, auth_headers):
    """Test spending report with no data."""
    response = test_client.post(
        "/api/v1/reports/spending",
        json={
            "period": "custom",
            "start_date": str(date.today()),
            "end_date": str(date.today())
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["total_spent"] == 0.0
    assert len(data["categories"]) == 0

def test_spending_report_with_data(test_client, auth_headers):
    """Test spending report with transactions."""
    # Create two expenses in different categories
    # 1. Shopping
    test_client.post(
        "/api/v1/transactions/",
        json={
            "merchant": "Shop A",
            "amount": 50.0,
            "category": "Shopping", # Should map to ID internally or stay string
            "date": str(date.today())
        },
        headers=auth_headers
    )
    # 2. Food
    test_client.post(
        "/api/v1/transactions/",
        json={
            "merchant": "Food B",
            "amount": 30.0,
            "category": "Food",
            "date": str(date.today())
        },
        headers=auth_headers
    )
    
    response = test_client.post(
        "/api/v1/reports/spending",
        json={
            "period": "custom",
            "start_date": str(date.today()),
            "end_date": str(date.today())
        },
        headers=auth_headers
    )
    
    data = response.json()["data"]
    assert data["total_spent"] == 80.0
    assert len(data["categories"]) >= 2

def test_deep_dive_monthly(test_client, auth_headers):
    """Test deep dive analytics for monthly period."""
    response = test_client.post(
        "/api/v1/analytics/deep-dive",
        json={"period": "monthly"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "total_spent" in data
    assert "spending_velocity" in data
    assert "ai_insights" in data

def test_deep_dive_uncategorized_handling(test_client, auth_headers):
    """
    Test deep dive with uncategorized transactions (null category_id).
    This validates the recent regression fix.
    """
    # Create transaction without explicit category (simulating Salt Edge sync)
    test_client.post(
        "/api/v1/transactions/",
        json={
            "merchant": "Mystery Charge",
            "amount": 100.0,
            "date": str(date.today())
        },
        headers=auth_headers
    )
    
    response = test_client.post(
        "/api/v1/analytics/deep-dive",
        json={"period": "monthly"},
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()["data"]
    # Should not be empty
    assert data["total_spent"] >= 100.0
    # Comparison shouldn't crash
    assert isinstance(data["categories_comparison"], list)

def test_deep_dive_invalid_period(test_client, auth_headers):
    """Test deep dive with invalid period."""
    # Using 'monthly' because validation is weak or defaults? 
    # Actually schema might enforce it. Let's try "century"
    # If using Pydantic Enum it fails 422, if string it might 200 but default.
    # Let's check status.
    response = test_client.post(
        "/api/v1/analytics/deep-dive",
        json={"period": "century"},
        headers=auth_headers
    )
    # Depending on implementation, might default to monthly or error.
    # Assuming standard behavior, if not validated it returns 200.
    # But if strict, 422.
    # Let's verify it doesn't crash 500.
    assert response.status_code != 500

def test_report_calculations(test_client, auth_headers):
    """Verify sum of categories equals total spent."""
    # Add expenses
    test_client.post("/api/v1/transactions/", json={"merchant":"A","amount":10,"date":str(date.today())}, headers=auth_headers)
    test_client.post("/api/v1/transactions/", json={"merchant":"B","amount":20,"date":str(date.today())}, headers=auth_headers)
    
    response = test_client.post(
        "/api/v1/reports/spending",
        json={"period": "monthly"},
        headers=auth_headers
    )
    data = response.json()["data"]
    
    cat_sum = sum(c["total_spent"] for c in data["categories"])
    # Floating point issues might occur, use close check
    assert abs(cat_sum - data["total_spent"]) < 0.01
