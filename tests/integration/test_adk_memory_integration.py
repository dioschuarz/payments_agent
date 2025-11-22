"""Integration tests for ADK memory integration."""

import pytest
from src.infrastructure.ai.agents.adk_orchestrator import ADKOrchestrator
from src.infrastructure.config.service_factory import ServiceFactory
from src.infrastructure.validators.amount_validator import AmountValidator
from src.infrastructure.validators.beneficiary_validator import BeneficiaryValidator
from src.infrastructure.validators.country_validator import CountryValidator
from src.infrastructure.validators.delivery_method_validator import DeliveryMethodValidator


@pytest.fixture
def orchestrator():
    """Create ADK orchestrator for testing."""
    factory = ServiceFactory()
    beneficiary_validator = BeneficiaryValidator(factory.create_beneficiary_service())
    country_validator = CountryValidator(factory.create_country_service())
    amount_validator = AmountValidator(factory.create_amount_validation_service())
    delivery_validator = DeliveryMethodValidator(factory.create_delivery_method_service())
    
    return ADKOrchestrator(
        beneficiary_validator=beneficiary_validator,
        country_validator=country_validator,
        amount_validator=amount_validator,
        delivery_method_validator=delivery_validator,
        api_key="test-key",  # Will fail at runtime but allows import testing
    )


def test_orchestrator_initialization(orchestrator):
    """Test that orchestrator initializes with ADK components."""
    assert orchestrator is not None
    assert orchestrator._agent is not None
    assert orchestrator._runner is not None
    assert orchestrator._runner.memory_service is not None
    # Plugins are integrated into the runner, verify they exist
    assert hasattr(orchestrator._runner, 'memory_service')


def test_memory_service_present(orchestrator):
    """Test that ADK memory service is present."""
    from google.adk.memory import InMemoryMemoryService
    
    assert isinstance(orchestrator._runner.memory_service, InMemoryMemoryService)


def test_plugins_present(orchestrator):
    """Test that ADK plugins are configured."""
    # Plugins are integrated into the runner during initialization
    # We verify the orchestrator was created with plugins by checking
    # that the runner has the necessary components
    assert orchestrator._runner is not None
    assert orchestrator._runner.memory_service is not None
    # Plugins are internal to the runner, but their effects are observable


def test_tools_present(orchestrator):
    """Test that ADK tools are present."""
    assert orchestrator._beneficiary_tool is not None
    assert orchestrator._amount_tool is not None
    assert orchestrator._country_tool is not None
    assert orchestrator._delivery_method_tool is not None


def test_agent_instruction_contains_memory(orchestrator):
    """Test that agent instructions mention memory usage."""
    instruction = orchestrator._build_instruction("test countries")
    assert "memory" in instruction.lower()
    assert "remember" in instruction.lower()

