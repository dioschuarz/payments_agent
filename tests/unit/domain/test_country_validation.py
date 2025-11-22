"""Phase 1: Domain Logic Unit Tests - Country Validation.

Tests country validation logic in isolation.
"""

import pytest

from src.domain.value_objects.country import Country


class TestCountryValidation:
    """TC-UNIT-04: Test country validation."""

    def test_validate_country_valid(self):
        """
        TC-UNIT-04 (Valid Case): test_validate_country_valid
        
        Given: input "US" or "United States"
        When: Country.from_name() is called
        Then: returns valid Country object
        """
        # Test with code
        country = Country.from_name("US")
        assert country is not None
        assert country.code == "US"
        
        # Test with name
        country = Country.from_name("United States")
        assert country is not None
        assert country.code == "US"
        assert country.name == "United States"

    def test_validate_country_invalid(self):
        """
        TC-UNIT-04 (Invalid Case): test_validate_country_invalid
        
        Given: input "Narnia"
        When: Country.from_name() is called
        Then: returns None (invalid country)
        """
        country = Country.from_name("Narnia")
        assert country is None

    def test_country_case_insensitive(self):
        """Test country name matching is case insensitive."""
        country1 = Country.from_name("brazil")
        country2 = Country.from_name("Brazil")
        country3 = Country.from_name("BRAZIL")
        
        assert country1 is not None
        assert country2 is not None
        assert country3 is not None
        assert country1.code == country2.code == country3.code == "BR"

    def test_country_aliases(self):
        """Test country name variations work."""
        # Test common aliases
        uk1 = Country.from_name("United Kingdom")
        uk2 = Country.from_name("UK")
        uk3 = Country.from_name("Britain")
        
        assert uk1 is not None
        assert uk2 is not None
        assert uk3 is not None
        assert uk1.code == uk2.code == uk3.code == "GB"

