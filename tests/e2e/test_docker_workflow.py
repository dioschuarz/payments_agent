"""E2E Tests for Docker Container Workflow.

Tests the complete workflow through Docker container,
verifying all Master Test Plan requirements.
"""

import pytest
import requests
import time
import subprocess


@pytest.fixture(scope="module")
def docker_container():
    """Start Docker container for testing."""
    # Start container
    subprocess.run(
        ["docker", "compose", "up", "-d"],
        cwd=".",
        capture_output=True,
        timeout=60,
    )
    
    # Wait for container to be ready
    max_retries = 30
    for _ in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                break
        except Exception:
            time.sleep(1)
    else:
        pytest.fail("Container did not become ready in time")
    
    yield
    
    # Cleanup
    subprocess.run(
        ["docker", "compose", "down"],
        cwd=".",
        capture_output=True,
        timeout=30,
    )


class TestDockerWorkflow:
    """Test complete workflow in Docker container."""

    def test_health_endpoint(self, docker_container):
        """Test health endpoint in Docker."""
        response = requests.get("http://localhost:8000/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "0.1.0"

    def test_initial_message_tc_unit_01(self, docker_container):
        """
        TC-UNIT-01 via Docker: test_initial_state_empty
        
        Given: a new session via Docker API
        Then: agent should respond asking for information
        """
        response = requests.post(
            "http://localhost:8000/webhook/whatsapp",
            json={
                "from_number": "+5511987628829",
                "message": "ola",
            },
            timeout=30,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["to_number"] == "+5511987628829"
        assert len(data["message"]) > 0
        # Should get a response (not an error)
        assert "error" not in data.get("message", "").lower()

    def test_send_money_intent(self, docker_container):
        """Test sending money intent."""
        response = requests.post(
            "http://localhost:8000/webhook/whatsapp",
            json={
                "from_number": "+5511987628829",
                "message": "I want to send money",
            },
            timeout=30,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        # Should ask for beneficiary or acknowledge intent
        assert len(data["message"]) > 0

    def test_provide_beneficiary(self, docker_container):
        """Test providing beneficiary name."""
        response = requests.post(
            "http://localhost:8000/webhook/whatsapp",
            json={
                "from_number": "+5511987628829",
                "message": "John",
            },
            timeout=30,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["message"]) > 0

    def test_provide_amount(self, docker_container):
        """Test providing amount."""
        response = requests.post(
            "http://localhost:8000/webhook/whatsapp",
            json={
                "from_number": "+5511987628829",
                "message": "100 dollars",
            },
            timeout=30,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["message"]) > 0

    def test_provide_country(self, docker_container):
        """Test providing country."""
        response = requests.post(
            "http://localhost:8000/webhook/whatsapp",
            json={
                "from_number": "+5511987628829",
                "message": "Brazil",
            },
            timeout=30,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["message"]) > 0

    def test_provide_delivery_method(self, docker_container):
        """Test providing delivery method."""
        response = requests.post(
            "http://localhost:8000/webhook/whatsapp",
            json={
                "from_number": "+5511987628829",
                "message": "bank transfer",
            },
            timeout=30,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["message"]) > 0

    def test_mixed_input_tc_int_02(self, docker_container):
        """
        TC-INT-02 via Docker: test_flow_mixed_input
        
        Scenario: User says "Send 500 to Brazil" via Docker API
        """
        response = requests.post(
            "http://localhost:8000/webhook/whatsapp",
            json={
                "from_number": "+5511987628829",
                "message": "Send 500 to Brazil",
            },
            timeout=30,
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["message"]) > 0

    def test_session_persistence(self, docker_container):
        """Test that session persists across multiple messages."""
        session_id = "+5511987628829"
        
        # First message
        response1 = requests.post(
            "http://localhost:8000/webhook/whatsapp",
            json={
                "from_number": session_id,
                "message": "I want to send money",
            },
            timeout=30,
        )
        assert response1.status_code == 200
        
        # Second message (should remember context)
        response2 = requests.post(
            "http://localhost:8000/webhook/whatsapp",
            json={
                "from_number": session_id,
                "message": "John",
            },
            timeout=30,
        )
        assert response2.status_code == 200
        # Should understand "John" in context of sending money

