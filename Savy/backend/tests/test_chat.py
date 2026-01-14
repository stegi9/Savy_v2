"""
Tests for the Chat Service and Controller.
"""
from unittest.mock import AsyncMock, patch
import pytest

@pytest.mark.asyncio
async def test_chat_message(test_client, auth_headers):
    """Test sending a chat message/question."""
    mock_agent_response = {
        "decision": "advice",
        "reasoning": "Based on your spending, everything looks fine.",
        "balance": 1000.0,
        "upcoming_bills": []
    }

    # IMPORTANT: mocking 'services.chat_service.invoke_agent' assuming it is imported in chat_service.py
    with patch("services.chat_service.invoke_agent", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = mock_agent_response

        response = test_client.post(
            "/api/v1/chat",
            json={"message": "Can I afford a cocktail?"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["decision"] == "advice"
        assert "fine" in data["reasoning"]

@pytest.mark.asyncio
async def test_chat_json_reasoning_parsing(test_client, auth_headers):
    """Test parsing logic when LLM returns JSON inside markdown."""
    json_content = '{"reasoning": "Parsed reasoning", "decision": "approve"}'
    mock_agent_response = {
        "decision": "approve",
        "reasoning": f"```json\n{json_content}\n```",
        "balance": 500.0,
        "upcoming_bills": []
    }

    with patch("services.chat_service.invoke_agent", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = mock_agent_response

        response = test_client.post(
            "/api/v1/chat",
            json={"message": "Check budget"},
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["decision"] == "approve"
        assert data["reasoning"] == "Parsed reasoning"

@pytest.mark.asyncio
async def test_chat_error_handling(test_client, auth_headers):
    """Test error handling when agent fails."""
    with patch("services.chat_service.invoke_agent", new_callable=AsyncMock) as mock_agent:
        mock_agent.side_effect = Exception("Agent error")

        response = test_client.post(
            "/api/v1/chat",
            json={"message": "Fail please"},
            headers=auth_headers
        )

        # Expect 500
        assert response.status_code == 500
        assert "Errore" in response.json()["detail"]
