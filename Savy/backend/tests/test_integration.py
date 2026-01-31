"""
Integration tests for critical user flows.
Tests full API endpoints with database interactions.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.database import Base, get_db
from config import settings

# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    """Create test client with fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


# ============================================================================
# USER REGISTRATION & LOGIN FLOW
# ============================================================================

def test_user_registration_and_login_flow(client):
    """
    Test complete user registration and login flow.
    1. Register new user
    2. Login with credentials
    3. Access protected endpoint
    """
    # Step 1: Register
    register_data = {
        "email": "integration@test.com",
        "password": "SecurePass123!",
        "full_name": "Integration Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    access_token = data["access_token"]
    
    # Step 2: Login
    login_data = {
        "email": "integration@test.com",
        "password": "SecurePass123!"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    
    # Step 3: Access protected endpoint
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == "integration@test.com"
    assert user_data["full_name"] == "Integration Test User"


def test_duplicate_email_registration(client):
    """Test that duplicate email registration is rejected."""
    register_data = {
        "email": "duplicate@test.com",
        "password": "SecurePass123!",
        "full_name": "First User"
    }
    
    # First registration
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 201
    
    # Second registration with same email
    response = client.post("/api/v1/auth/register", json=register_data)
    assert response.status_code == 409  # Conflict


# ============================================================================
# CATEGORY MANAGEMENT FLOW
# ============================================================================

def test_category_crud_flow(client):
    """
    Test complete category CRUD flow.
    1. Create user
    2. Create category
    3. List categories
    4. Update category
    5. Delete category
    """
    # Step 1: Create user
    register_data = {
        "email": "category@test.com",
        "password": "SecurePass123!",
        "full_name": "Category Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Step 2: Create category
    category_data = {
        "name": "Test Shopping",
        "icon": "shopping_cart",
        "color": "#FF5733",
        "type": "expense",
        "budget_monthly": 500.00
    }
    
    response = client.post("/api/v1/categories", json=category_data, headers=headers)
    assert response.status_code == 201
    category = response.json()
    category_id = category["id"]
    assert category["name"] == "Test Shopping"
    
    # Step 3: List categories
    response = client.get("/api/v1/categories", headers=headers)
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) > 0  # Default categories + new one
    
    # Step 4: Update category
    update_data = {
        "name": "Updated Shopping",
        "budget_monthly": 600.00
    }
    
    response = client.put(f"/api/v1/categories/{category_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    updated = response.json()
    assert updated["name"] == "Updated Shopping"
    assert float(updated["budget_monthly"]) == 600.00
    
    # Step 5: Delete category
    response = client.delete(f"/api/v1/categories/{category_id}", headers=headers)
    assert response.status_code == 200


# ============================================================================
# TRANSACTION FLOW
# ============================================================================

def test_transaction_creation_and_categorization(client):
    """
    Test transaction creation with automatic categorization.
    """
    # Create user
    register_data = {
        "email": "transaction@test.com",
        "password": "SecurePass123!",
        "full_name": "Transaction Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get user's first category
    response = client.get("/api/v1/categories", headers=headers)
    categories = response.json()
    category_id = categories[0]["id"]
    
    # Create transaction
    transaction_data = {
        "amount": 50.00,
        "description": "Test Grocery Shopping",
        "category_id": category_id,
        "transaction_date": "2026-01-31",
        "type": "expense"
    }
    
    response = client.post("/api/v1/transactions", json=transaction_data, headers=headers)
    assert response.status_code == 201
    transaction = response.json()
    assert transaction["amount"] == 50.00
    assert transaction["description"] == "Test Grocery Shopping"
    
    # List transactions
    response = client.get("/api/v1/transactions", headers=headers)
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) > 0


# ============================================================================
# CHAT AI FLOW
# ============================================================================

def test_chat_with_ai_coach(client):
    """
    Test chat interaction with AI financial coach.
    """
    # Create user
    register_data = {
        "email": "chat@test.com",
        "password": "SecurePass123!",
        "full_name": "Chat Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Send chat message
    chat_data = {
        "message": "Can I afford a €50 purchase?"
    }
    
    response = client.post("/api/v1/chat", json=chat_data, headers=headers)
    assert response.status_code == 200
    chat_response = response.json()
    assert "response" in chat_response
    assert len(chat_response["response"]) > 0


# ============================================================================
# BILL REMINDER FLOW
# ============================================================================

def test_recurring_bill_management(client):
    """
    Test recurring bill creation and management.
    """
    # Create user
    register_data = {
        "email": "bills@test.com",
        "password": "SecurePass123!",
        "full_name": "Bills Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Create recurring bill
    bill_data = {
        "name": "Test Electric Bill",
        "amount": 80.00,
        "frequency": "monthly",
        "next_due_date": "2026-02-15",
        "provider": "Test Energy"
    }
    
    response = client.post("/api/v1/bills", json=bill_data, headers=headers)
    assert response.status_code == 201
    bill = response.json()
    assert bill["name"] == "Test Electric Bill"
    assert bill["amount"] == 80.00
    
    # List bills
    response = client.get("/api/v1/bills", headers=headers)
    assert response.status_code == 200
    bills = response.json()
    assert len(bills) > 0


# ============================================================================
# REPORT GENERATION FLOW
# ============================================================================

def test_spending_report_generation(client):
    """
    Test spending report generation.
    """
    # Create user
    register_data = {
        "email": "report@test.com",
        "password": "SecurePass123!",
        "full_name": "Report Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    access_token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    
    # Get spending report
    response = client.get("/api/v1/reports/spending?period=month", headers=headers)
    assert response.status_code == 200
    report = response.json()
    assert "total_spending" in report
    assert "by_category" in report
