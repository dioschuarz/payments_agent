"""Tests for StateManager."""

import pytest

from src.domain.entities.beneficiary import Beneficiary
from src.domain.exceptions import InvalidStateTransitionError
from src.domain.state.state_manager import StateManager
from src.domain.state.transfer_state import TransferState


def test_state_manager_initial_state():
    """Test initial state is IDLE."""
    manager = StateManager()
    assert manager.state == TransferState.IDLE


def test_start_collection_transition():
    """Test transitioning from IDLE to COLLECTING."""
    manager = StateManager()
    manager.start_collection()
    assert manager.state == TransferState.COLLECTING


def test_invalid_transition():
    """Test invalid state transition raises error."""
    manager = StateManager()
    with pytest.raises(InvalidStateTransitionError):
        manager.transition_to(TransferState.CONFIRMED)


def test_resolve_ambiguity_single_match():
    """Test ambiguity resolution with single match."""
    manager = StateManager()
    manager.start_collection()

    beneficiary = Beneficiary(id="1", name="John Doe")
    matches = [beneficiary]

    resolved = manager.resolve_ambiguity("John", matches)
    assert resolved == beneficiary
    assert manager.state == TransferState.COLLECTING


def test_resolve_ambiguity_multiple_matches():
    """Test ambiguity resolution with multiple matches triggers clarification."""
    manager = StateManager()
    manager.start_collection()

    matches = [
        Beneficiary(id="1", name="John Doe"),
        Beneficiary(id="2", name="John Smith"),
    ]

    resolved = manager.resolve_ambiguity("John", matches)
    assert resolved is None
    assert manager.state == TransferState.CLARIFYING


def test_select_beneficiary_after_clarification():
    """Test selecting beneficiary after clarification."""
    manager = StateManager()
    manager.start_collection()

    # Trigger clarification
    matches = [
        Beneficiary(id="1", name="John Doe"),
        Beneficiary(id="2", name="John Smith"),
    ]
    manager.resolve_ambiguity("John", matches)
    assert manager.state == TransferState.CLARIFYING

    # Select beneficiary
    selected = matches[0]
    manager.select_beneficiary(selected)
    assert manager.transfer_request.beneficiary == selected
    assert manager.state == TransferState.COLLECTING

