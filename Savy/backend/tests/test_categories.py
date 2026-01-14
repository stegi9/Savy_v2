"""
Test suite for category endpoints.
"""
import pytest

def test_get_categories_defaults(test_client, auth_headers):
    """Test retrieving default categories."""
    response = test_client.get("/api/v1/categories/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # Ensure some defaults exist (Altro, Shopping, etc)
    names = [c["name"] for c in data]
    assert "Altro" in names

def test_create_custom_category(test_client, auth_headers):
    """Test creating a custom category."""
    response = test_client.post(
        "/api/v1/categories/",
        json={
            "name": "My Hobby",
            "icon": "gamepad",
            "color": "#FF5733",
            "category_type": "expense"
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "My Hobby"
    assert data["is_system"] == False

def test_create_category_invalid_color(test_client, auth_headers):
    """Test creating category with invalid hex color."""
    response = test_client.post(
        "/api/v1/categories/",
        json={
            "name": "Invalid Color",
            "color": "not-a-color"
        },
        headers=auth_headers
    )
    assert response.status_code == 422

def test_update_category(test_client, auth_headers):
    """Test updating a category."""
    # Create
    create_res = test_client.post(
        "/api/v1/categories/",
        json={"name": "To Update", "color": "#000000"},
        headers=auth_headers
    )
    cat_id = create_res.json()["id"]
    
    # Update
    response = test_client.put(
        f"/api/v1/categories/{cat_id}",
        json={"name": "Updated Name", "budget_monthly": 500},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert float(data["budget_monthly"]) == 500.0

def test_delete_category(test_client, auth_headers):
    """Test deleting a category."""
    # Create
    create_res = test_client.post(
        "/api/v1/categories/",
        json={"name": "To Delete"},
        headers=auth_headers
    )
    cat_id = create_res.json()["id"]
    
    # Delete
    response = test_client.delete(f"/api/v1/categories/{cat_id}", headers=auth_headers)
    assert response.status_code == 200
    
    # Verify gone
    get_res = test_client.get("/api/v1/categories/", headers=auth_headers)
    ids = [c["id"] for c in get_res.json()]
    assert cat_id not in ids

def test_delete_system_category_fails(test_client, auth_headers):
    """Test that system categories cannot be deleted."""
    # Find a system category
    all_res = test_client.get("/api/v1/categories/", headers=auth_headers)
    sys_cat = next((c for c in all_res.json() if c["is_system"]), None)
    
    if sys_cat:
        response = test_client.delete(f"/api/v1/categories/{sys_cat['id']}", headers=auth_headers)
        # Should be 403 Forbidden or 400 Bad Request depending on implementation
        # Asserting 403 as "Forbidden" is usual for protected resources
        assert response.status_code in [400, 403]

def test_get_categories_income_type(test_client, auth_headers):
    """Test filtering categories by type."""
    # Create income category
    test_client.post(
        "/api/v1/categories/",
        json={"name": "My Salary", "category_type": "income"},
        headers=auth_headers
    )
    
    response = test_client.get("/api/v1/categories/?type=income", headers=auth_headers)
    data = response.json()
    assert all(c["category_type"] == "income" for c in data)
