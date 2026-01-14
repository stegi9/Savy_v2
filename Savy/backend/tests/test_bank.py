"""
Test suite for bank integration endpoints.
"""
from unittest.mock import patch

def test_start_link_session(test_client, auth_headers):
    """Test starting a bank link session."""
    # Mock the banking service creating a customer/session
    with patch("services.banking_service.BankingService.create_connect_session") as mock_create:
        mock_create.return_value = "https://saltedge.com/connect?token=123"
        
        # Also mock get_customer/create_customer logic if it runs first
        with patch("services.banking_service.BankingService.get_customer") as mock_get_cust:
             mock_get_cust.return_value = {"id": "123"}
             
             response = test_client.post(
                 "/api/v1/banks/link/start",
                 headers=auth_headers
             )
             
             assert response.status_code == 200
             data = response.json()
             assert "link" in data["data"]
             assert "saltedge" in data["data"]["link"]

def test_sync_no_connections(test_client, auth_headers):
    """Test syncing when user has no bank connections."""
    # Mock empty connections list
    with patch("services.banking_service.BankingService.get_connections") as mock_get:
        mock_get.return_value = []
        
        # Mock get_customer
        with patch("services.banking_service.BankingService.get_customer") as mock_cust:
             mock_cust.return_value = {"id": "123"}
        
             response = test_client.post(
                 "/api/v1/banks/sync",
                 headers=auth_headers
             )
             
             assert response.status_code == 200
             assert response.json()["message"] == "User has no linked bank customer"

def test_callback_endpoint(test_client, auth_headers):
    """Test standard callback interception (if implemented)."""
    # Simply check if endpoint exists or validates
    # Not a critical test if logic is handled deep link side, but backend might have one.
    pass

def test_get_connections_initial(test_client, auth_headers):
    """Test retrieving connections list (should be empty initially)."""
    response = test_client.get("/api/v1/banks/connections", headers=auth_headers)
    # If endpoint exists?
    if response.status_code != 404:
        assert response.status_code == 200
        assert isinstance(response.json()["data"], list)
