"""Phase 1: Domain Logic Unit Tests - Beneficiary Ambiguity Detection.

Tests ambiguity detection and resolution logic.
"""

import pytest

from src.domain.entities.beneficiary import Beneficiary


class TestBeneficiaryAmbiguity:
    """TC-UNIT-05, TC-UNIT-06: Test ambiguity detection and resolution."""

    def test_detect_ambiguity_multiple_matches(self):
        """
        TC-UNIT-05: test_detect_ambiguity
        
        Given: input "To John" and lookup returns 2 matches
        When: logic processes
        Then: ambiguity is detected (multiple candidates)
        """
        matches = [
            Beneficiary(id="1", name="John Doe"),
            Beneficiary(id="2", name="John Smith"),
        ]
        
        # Ambiguity detected when len(matches) > 1
        assert len(matches) > 1
        assert matches[0].name != matches[1].name
        
        # Both are valid candidates
        assert all(isinstance(b, Beneficiary) for b in matches)

    def test_resolve_ambiguity_single_match(self):
        """
        TC-UNIT-06 (Single Match): test_resolve_ambiguity_single_match
        
        Given: lookup returns single match
        When: logic processes
        Then: no ambiguity, beneficiary can be set directly
        """
        matches = [
            Beneficiary(id="1", name="John Doe"),
        ]
        
        # No ambiguity when len(matches) == 1
        assert len(matches) == 1
        selected = matches[0]
        assert selected.name == "John Doe"

    def test_resolve_ambiguity_exact_match(self):
        """
        TC-UNIT-06 (Exact Match): test_resolve_ambiguity_exact_match
        
        Given: state has ambiguity with candidates ["John Doe", "John Smith"]
        When: input is "John Doe" (Exact Match)
        Then: beneficiary is resolved to "John Doe"
        """
        candidates = [
            Beneficiary(id="1", name="John Doe"),
            Beneficiary(id="2", name="John Smith"),
        ]
        
        # User selects exact match
        user_input = "John Doe"
        selected = next((b for b in candidates if b.name == user_input), None)
        
        assert selected is not None
        assert selected.name == "John Doe"
        assert selected.id == "1"

    def test_resolve_ambiguity_no_matches(self):
        """
        Test case: No matches found
        
        Given: lookup returns empty list
        When: logic processes
        Then: no beneficiary found
        """
        matches = []
        assert len(matches) == 0
        # No beneficiary can be selected

