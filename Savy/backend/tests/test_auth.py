"""
Test suite for authentication endpoints.
"""
import pytest



class TestAuthentication:
    """Test authentication endpoints."""
    
    def test_register_success(self, test_client):
        """Test successful user registration."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0
    
    def test_register_duplicate_email(self, test_client):
        """Test registration with duplicate email."""
        # First registration
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
        
        # Second registration with same email
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "different123",
                "full_name": "Another User"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    def test_register_missing_fields(self, test_client):
        """Test registration with missing required fields."""
        # Missing full_name
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpass123"
                # Missing full_name
            }
        )
        
        assert response.status_code == 422
    
    def test_register_short_password(self, test_client):
        """Test registration with short password."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "123",
                "full_name": "Test User"
            }
        )
        
        assert response.status_code == 422
    
    def test_login_success(self, test_client):
        """Test successful login."""
        # Register user first
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
        
        # Login
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_wrong_password(self, test_client):
        """Test login with wrong password."""
        # Register user first
        test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
        
        # Login with wrong password
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    def test_login_nonexistent_user(self, test_client):
        """Test login with non-existent user."""
        response = test_client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "testpass123"
            }
        )
        
        assert response.status_code == 401
    
    def test_get_current_user(self, test_client):
        """Test getting current user profile."""
        # Register user
        register_response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpass123",
                "full_name": "Test User"
            }
        )
        
        token = register_response.json()["access_token"]
        
        # Get profile
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["full_name"] == "Test User"
        assert "id" in data
    
    def test_get_current_user_no_token(self, test_client):
        """Test getting profile without token."""
        response = test_client.get("/api/v1/auth/me")
        
        assert response.status_code == 403  # Forbidden (no token)
    
    def test_get_current_user_invalid_token(self, test_client):
        """Test getting profile with invalid token."""
        response = test_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        
        assert response.status_code == 401

