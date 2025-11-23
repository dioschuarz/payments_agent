"""E2E test for ambiguity resolution."""

import pytest

from src.domain.entities.beneficiary import Beneficiary
from src.domain.state.state_manager import StateManager
from src.domain.state.transfer_state import TransferState


@pytest.mark.asyncio
async def test_should_ask_clarification_when_beneficiary_is_ambiguous():
    """
    Test that the agent asks for clarification when beneficiary is ambiguous.

    This is the specific test case mentioned in the PRD.
    """
    # Arrange
    state_manager = StateManager()
    state_manager.start_collection()

    # Simulate ambiguous beneficiary lookup
    matches = [
        Beneficiary(id="1", name="John A"),
        Beneficiary(id="2", name="John B"),
    ]

    # Act
    resolved = state_manager.resolve_ambiguity("John", matches)

    # Assert
    assert resolved is None
    assert state_manager.state == TransferState.CLARIFYING

