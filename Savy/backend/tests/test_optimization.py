"""
Tests for Optimization Service and Controller.
"""
from unittest.mock import MagicMock, patch
import pytest
from datetime import datetime

# Helper to mock a RecurringBill object since it's an SQLAlchemy model
class MockBill:
    def __init__(self, id, amount, category, provider, name="Bill"):
        self.id = id
        self.amount = amount
        self.category = category
        self.provider = provider
        self.name = name

@pytest.mark.asyncio
async def test_optimization_scan_no_bills(test_client, auth_headers):
    """Test scan when no bills are found."""
    with patch("api.routes.optimization_controller.OptimizationRepository") as MockRepo:
        mock_instance = MockRepo.return_value
        mock_instance.get_user_bills.return_value = []

        response = test_client.post(
            "/api/v1/optimizations/scan",
            json={"categories": ["energy"]},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["optimizations"] == []
        assert data["opportunities_found"] == 0

@pytest.mark.asyncio
async def test_optimization_scan_found_opportunity(test_client, auth_headers):
    """Test scan finding an optimization opportunity."""
    
    # Mock bill that can be optimized (e.g., high cost energy)
    mock_bill = MockBill(id="bill_1", amount=100.0, category="energy", provider="OldProvider")
    
    # Mock created lead
    mock_lead = MagicMock()
    mock_lead.id = "lead_1"
    
    with patch("api.routes.optimization_controller.OptimizationRepository") as MockRepo:
        mock_instance = MockRepo.return_value
        mock_instance.get_user_bills.return_value = [mock_bill]
        mock_instance.create_optimization_lead.return_value = mock_lead
        
        # Patch MOCK_PARTNERS to ensure deterministic result
        with patch("services.optimization_service.OptimizationService.MOCK_PARTNERS", 
                   {"energy": [{"name": "NewProvider", "discount": 0.5}]}):
        
            response = test_client.post(
                "/api/v1/optimizations/scan",
                json={"categories": ["energy"]},
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()["data"]
            assert len(data["optimizations"]) == 1
            opt = data["optimizations"][0]
            assert opt["current_cost"] == 100.0
            assert opt["optimized_cost"] == 50.0  # 50% discount
            assert opt["recommended_provider"] == "NewProvider"

@pytest.mark.asyncio
async def test_optimization_scan_ignore_low_savings(test_client, auth_headers):
    """Test that low savings opportunities are ignored."""
    # Bill with very low cost, savings < 5 euro
    mock_bill = MockBill(id="bill_2", amount=10.0, category="energy", provider="OldProvider")
    
    with patch("api.routes.optimization_controller.OptimizationRepository") as MockRepo:
        mock_instance = MockRepo.return_value
        mock_instance.get_user_bills.return_value = [mock_bill]
        
        # Discount 10% of 10 euro = 1 euro savings (Should be ignored as < 5.0)
        with patch("services.optimization_service.OptimizationService.MOCK_PARTNERS", 
                   {"energy": [{"name": "NewProvider", "discount": 0.1}]}):

            response = test_client.post(
                "/api/v1/optimizations/scan",
                json={"categories": ["energy"]},
                headers=auth_headers
            )

            assert response.status_code == 200
            data = response.json()["data"]
            assert len(data["optimizations"]) == 0

def test_get_leads(test_client, auth_headers):
    """Test retrieving existing leads."""
    
    with patch("api.routes.optimization_controller.OptimizationRepository") as MockRepo:
        mock_instance = MockRepo.return_value
        
        mock_lead = MagicMock()
        mock_lead.id = "lead_123"
        mock_lead.bill_category = "energy"
        mock_lead.current_cost = 100.0
        mock_lead.optimized_cost = 80.0
        mock_lead.savings_amount = 20.0
        mock_lead.partner_name = "Enel"
        mock_lead.status = "new"
        mock_lead.created_at = datetime.now()
        
        mock_instance.get_user_optimization_leads.return_value = [mock_lead]

        response = test_client.get(
            "/api/v1/optimizations/leads?user_id=123",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["count"] == 1
        assert data["leads"][0]["partner_name"] == "Enel"
