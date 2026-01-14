"""
Test configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from main import app
from db.database import Base, get_db
from utils.security import create_access_token

# Create in-memory SQLite database for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def test_client():
    """Create test client with test database for each test function."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Override dependency
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    # Drop tables
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def auth_headers(test_client):
    """Register a user and return auth headers."""
    email = "test_user@example.com"
    password = "password123"
    
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
            "full_name": "Test User"
        }
    )
    
    # If already exists (shouldn't happen with function scope but just in case)
    if response.status_code == 400:
        login_response = test_client.post(
             "/api/v1/auth/login",
             json={"email": email, "password": password}
        )
        token = login_response.json()["access_token"]
    else:
        token = response.json().get("access_token")
        
    return {"Authorization": f"Bearer {token}"}

