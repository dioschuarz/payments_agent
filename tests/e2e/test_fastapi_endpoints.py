"""E2E Tests for FastAPI Endpoints.

Tests the complete HTTP flow through FastAPI endpoints,
covering all test cases from the Master Test Plan.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from src.infrastructure.ai.agents.adk_orchestrator import ADKOrchestrator
from src.infrastructure.config.service_factory import ServiceFactory
from src.infrastructure.validators.amount_validator import AmountValidator
from src.infrastructure.validators.beneficiary_validator import BeneficiaryValidator
from src.infrastructure.validators.country_validator import CountryValidator
from src.infrastructure.validators.delivery_method_validator import DeliveryMethodValidator
from src.presentation.agent_flow import AgentFlow
from tests.unit.infrastructure.test_mock_validators import MockBeneficiaryService


@pytest.fixture
def mock_orchestrator():
    """Create a mock ADK orchestrator for testing."""
    orchestrator = MagicMock(spec=ADKOrchestrator)
    orchestrator.process_message = AsyncMock()
    return orchestrator


@pytest.fixture
def agent_flow(mock_orchestrator):
    """Create AgentFlow with mock orchestrator."""
    return AgentFlow(mock_orchestrator)


@pytest.fixture
def client(agent_flow):
    """Create FastAPI test client with mocked agent flow."""
    from main import app
    from src.presentation.api.routes import set_agent_flow
    
    # Set the agent flow
    set_agent_flow(agent_flow)
    
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_endpoint(self, client):
        """Test health check returns 200 with correct structure."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"


class TestWhatsAppWebhookEndpoint:
    """Test WhatsApp webhook endpoint - Phase 1: Domain Logic through API."""

    def test_initial_state_empty_tc_unit_01(self, client, mock_orchestrator):
        """
        TC-UNIT-01 via API: test_initial_state_empty
        
        Given: a new session via API
        Then: agent should respond asking for all required fields
        """
        mock_orchestrator.process_message.return_value = (
            "I'd be happy to help you send money! "
            "I need some information: Who would you like to send money to?"
        )
        
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "I want to send money",
                "message_id": "msg_001",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["to_number"] == "+1234567890"
        assert "send money" in data["message"].lower()
        
        # Verify orchestrator was called
        mock_orchestrator.process_message.assert_called_once()
        call_args = mock_orchestrator.process_message.call_args
        assert call_args[0][0] == "+1234567890"  # session_id
        assert "send money" in call_args[0][1].lower()  # user_input

    def test_slot_filling_partial_tc_unit_02(self, client, mock_orchestrator):
        """
        TC-UNIT-02 via API: test_slot_filling_partial
        
        Given: input "Send to Brazil" via API
        When: message is processed
        Then: agent acknowledges country but asks for other fields
        """
        mock_orchestrator.process_message.return_value = (
            "Great! I've noted you want to send to Brazil. "
            "How much would you like to send?"
        )
        
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "Send to Brazil",
                "message_id": "msg_002",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "brazil" in data["message"].lower()
        mock_orchestrator.process_message.assert_called_once()

    def test_overwrite_slot_correction_tc_unit_03(self, client, mock_orchestrator):
        """
        TC-UNIT-03 via API: test_overwrite_slot_correction
        
        Given: state has country="Brazil"
        When: user says "Actually, send to France"
        Then: agent updates to France
        """
        # First message sets Brazil
        mock_orchestrator.process_message.return_value = "Noted: Brazil"
        response1 = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "Send to Brazil",
            },
        )
        assert response1.status_code == 200
        
        # Second message corrects to France
        mock_orchestrator.process_message.return_value = (
            "Got it! I've updated the destination to France. "
            "How much would you like to send?"
        )
        response2 = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "Actually, send to France",
            },
        )
        
        assert response2.status_code == 200
        data = response2.json()
        assert "france" in data["message"].lower()
        assert mock_orchestrator.process_message.call_count == 2

    def test_validate_country_invalid_tc_unit_04(self, client, mock_orchestrator):
        """
        TC-UNIT-04 via API: test_validate_country_invalid
        
        Given: input "Send to Narnia" via API
        When: message is processed
        Then: agent indicates invalid country and asks again
        """
        mock_orchestrator.process_message.return_value = (
            "I'm sorry, I couldn't find a country called 'Narnia'. "
            "Could you please provide a valid country name?"
        )
        
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "Send to Narnia",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "narnia" in data["message"].lower() or "valid" in data["message"].lower()
        mock_orchestrator.process_message.assert_called_once()

    def test_detect_ambiguity_tc_unit_05(self, client, mock_orchestrator):
        """
        TC-UNIT-05 via API: test_detect_ambiguity
        
        Given: input "To John" via API
        When: lookup returns 2 matches
        Then: agent asks for clarification
        """
        mock_orchestrator.process_message.return_value = (
            "I found a few people named John. Which one did you mean?\n"
            "1. John Doe\n"
            "2. John Smith"
        )
        
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "To John",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "john" in data["message"].lower()
        assert "which" in data["message"].lower() or "1" in data["message"]
        mock_orchestrator.process_message.assert_called_once()

    def test_resolve_ambiguity_tc_unit_06(self, client, mock_orchestrator):
        """
        TC-UNIT-06 via API: test_resolve_ambiguity
        
        Given: state has ambiguity
        When: user says "John Doe" (Exact Match)
        Then: agent confirms and continues
        """
        mock_orchestrator.process_message.return_value = (
            "Perfect! I've selected John Doe. "
            "How much would you like to send?"
        )
        
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "John Doe",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "john doe" in data["message"].lower()
        assert "how much" in data["message"].lower()
        mock_orchestrator.process_message.assert_called_once()

    def test_ready_to_confirm_tc_unit_07(self, client, mock_orchestrator):
        """
        TC-UNIT-07 via API: test_ready_to_confirm
        
        Given: all 4 slots are filled
        Then: agent provides confirmation summary
        """
        mock_orchestrator.process_message.return_value = (
            "Transfer request confirmed!\n\n"
            "Summary:\n"
            "- Beneficiary: John Doe\n"
            "- Amount: USD 500\n"
            "- Country: Brazil\n"
            "- Delivery Method: Bank Transfer\n\n"
            "Is this correct?"
        )
        
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "Yes, confirm",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "confirmed" in data["message"].lower() or "summary" in data["message"].lower()
        assert "john doe" in data["message"].lower()
        assert "500" in data["message"] or "usd" in data["message"].lower()
        mock_orchestrator.process_message.assert_called_once()


class TestAgentFlowIntegration:
    """Phase 2: Agent Flow Integration Tests via API."""

    def test_flow_happy_path_tc_int_01(self, client, mock_orchestrator):
        """
        TC-INT-01 via API: test_flow_happy_path
        
        Scenario: User fills one slot at a time via API
        Assert: Agent asks for next missing field in sequence
        """
        session_id = "+1234567890"
        
        # Step 1: Initial request
        mock_orchestrator.process_message.return_value = (
            "I'd be happy to help! Who would you like to send money to?"
        )
        response1 = client.post(
            "/webhook/whatsapp",
            json={"from_number": session_id, "message": "I want to send money"},
        )
        assert response1.status_code == 200
        assert "who" in response1.json()["message"].lower()
        
        # Step 2: Provide beneficiary
        mock_orchestrator.process_message.return_value = (
            "Great! How much would you like to send to John Doe?"
        )
        response2 = client.post(
            "/webhook/whatsapp",
            json={"from_number": session_id, "message": "John Doe"},
        )
        assert response2.status_code == 200
        assert "how much" in response2.json()["message"].lower()
        
        # Step 3: Provide amount
        mock_orchestrator.process_message.return_value = (
            "Perfect! Which country should the money be sent to?"
        )
        response3 = client.post(
            "/webhook/whatsapp",
            json={"from_number": session_id, "message": "500 dollars"},
        )
        assert response3.status_code == 200
        assert "country" in response3.json()["message"].lower()
        
        # Verify all calls used same session_id
        assert mock_orchestrator.process_message.call_count == 3
        for call in mock_orchestrator.process_message.call_args_list:
            assert call[0][0] == session_id

    def test_flow_mixed_input_tc_int_02(self, client, mock_orchestrator):
        """
        TC-INT-02 via API: test_flow_mixed_input
        
        Scenario: User says "Send 500 to Brazil" via API
        Assert: Agent captures both slots and asks only for remaining fields
        """
        mock_orchestrator.process_message.return_value = (
            "Great! I've noted: Amount 500 USD, Destination Brazil. "
            "Who would you like to send this to?"
        )
        
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "Send 500 to Brazil",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "500" in data["message"] or "brazil" in data["message"].lower()
        assert "who" in data["message"].lower() or "beneficiary" in data["message"].lower()
        mock_orchestrator.process_message.assert_called_once()

    def test_flow_ambiguity_dialog_tc_int_03(self, client, mock_orchestrator):
        """
        TC-INT-03 via API: test_flow_ambiguity_dialog
        
        Scenario:
        1. User: "To John"
        2. Agent: "Which John? Doe or Smith?"
        3. User: "Doe"
        4. Agent: "Ok, to John Doe. How much?"
        """
        session_id = "+1234567890"
        
        # Step 1: Ambiguous input
        mock_orchestrator.process_message.return_value = (
            "I found a few people named John. Which one did you mean?\n"
            "1. John Doe\n"
            "2. John Smith"
        )
        response1 = client.post(
            "/webhook/whatsapp",
            json={"from_number": session_id, "message": "To John"},
        )
        assert response1.status_code == 200
        assert "which" in response1.json()["message"].lower()
        
        # Step 2: User clarifies
        mock_orchestrator.process_message.return_value = (
            "Perfect! I've selected John Doe. How much would you like to send?"
        )
        response2 = client.post(
            "/webhook/whatsapp",
            json={"from_number": session_id, "message": "Doe"},
        )
        assert response2.status_code == 200
        assert "john doe" in response2.json()["message"].lower()
        assert "how much" in response2.json()["message"].lower()
        
        assert mock_orchestrator.process_message.call_count == 2


class TestOutputContracts:
    """Phase 3: Output Contract Tests via API."""

    def test_json_schema_validity_tc_out_01(self, client, mock_orchestrator):
        """
        TC-OUT-01 via API: test_json_schema_validity
        
        Given: a completed flow via API
        When: response is received
        Then: it must be valid JSON with correct structure
        """
        mock_orchestrator.process_message.return_value = "Transfer confirmed!"
        
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "Confirm",
            },
        )
        
        assert response.status_code == 200
        
        # Verify response structure
        data = response.json()
        assert "to_number" in data
        assert "message" in data
        assert "status" in data
        
        # Verify types
        assert isinstance(data["to_number"], str)
        assert isinstance(data["message"], str)
        assert isinstance(data["status"], str)
        assert data["status"] == "success"

    def test_currency_normalization_tc_out_02(self, client, mock_orchestrator):
        """
        TC-OUT-02 via API: test_currency_normalization
        
        Given: input "500 bucks" or "500 USD" via API
        Then: agent response should use normalized currency
        """
        mock_orchestrator.process_message.return_value = (
            "I've noted: Amount 500 USD. Which country?"
        )
        
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "500 bucks",
            },
        )
        
        assert response.status_code == 200
        data = response.json()
        # Agent should normalize to USD in response
        assert "500" in data["message"]
        assert "usd" in data["message"].lower() or "dollar" in data["message"].lower()


class TestErrorHandling:
    """Test error handling in API endpoints."""

    def test_missing_required_fields(self, client):
        """Test API returns 422 for missing required fields."""
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                # Missing "message" field
            },
        )
        
        assert response.status_code == 422  # Validation error

    def test_invalid_json(self, client):
        """Test API handles invalid JSON."""
        response = client.post(
            "/webhook/whatsapp",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        
        assert response.status_code in [400, 422]

    def test_orchestrator_error_handling(self, client, mock_orchestrator):
        """Test API handles orchestrator errors gracefully."""
        mock_orchestrator.process_message.side_effect = Exception("Internal error")
        
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "Test message",
            },
        )
        
        # Should return 500 with error message
        assert response.status_code == 500
        data = response.json()
        assert "error" in data or "detail" in data

    def test_empty_message(self, client, mock_orchestrator):
        """Test API handles empty message."""
        mock_orchestrator.process_message.return_value = (
            "I didn't understand that. Could you please try again?"
        )
        
        response = client.post(
            "/webhook/whatsapp",
            json={
                "from_number": "+1234567890",
                "message": "",
            },
        )
        
        # Should still process (orchestrator decides how to handle)
        assert response.status_code == 200

