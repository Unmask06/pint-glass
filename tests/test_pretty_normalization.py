"""Tests for pretty keys and normalization logic in pint_glass."""

import pytest
from pydantic import BaseModel

from pint_glass import PintGlass
from pint_glass.core import get_preferred_unit
from pint_glass.dimensions import TARGET_DIMENSIONS


class TestPrettyDimensions:
    """Tests for the pretty-formatted TARGET_DIMENSIONS."""

    def test_keys_are_title_case(self) -> None:
        """All keys in TARGET_DIMENSIONS should be Title Case (spaces, no underscores)."""
        for key in TARGET_DIMENSIONS.keys():
            assert "_" not in key, f"Key '{key}' should not contain underscores"
            # Title case check: "Mass Flow Rate"
            # We allow single words like "Pressure"
            assert key[0].isupper(), f"Key '{key}' should start with uppercase"

    def test_units_are_pretty_formatted(self) -> None:
        """Units should be pretty formatted (heuristic check)."""
        # We check a few known ones to ensure the transformation happened
        # Pressure: 'pascal' -> 'Pa' (SI)
        # Area: 'meter ** 2' -> 'm²' (SI)
        
        # Note: We rely on the fact that get_pretty_dimensions() was called.
        
        # Check Pressure SI
        if "Pressure" in TARGET_DIMENSIONS:
            assert TARGET_DIMENSIONS["Pressure"]["si"] == "Pa"
        
        # Check Area SI
        if "Area" in TARGET_DIMENSIONS:
            assert TARGET_DIMENSIONS["Area"]["si"] == "m²"
            
        # Check Volume SI
        if "Volume" in TARGET_DIMENSIONS:
            assert TARGET_DIMENSIONS["Volume"]["si"] == "m³"


class TestDimensionNormalization:
    """Tests for dimension key normalization in PintGlass/core."""

    def test_all_pretty_keys_work_in_pint_glass(self) -> None:
        """PintGlass should accept all keys present in TARGET_DIMENSIONS."""
        for pretty_key in TARGET_DIMENSIONS.keys():
            # Should not raise
            try:
                _ = PintGlass(pretty_key, "Input")
            except Exception as e:
                pytest.fail(f"PintGlass failed for pretty key '{pretty_key}': {e}")

    def test_all_raw_keys_work_in_pint_glass(self) -> None:
        """PintGlass should accept raw keys (lowercase, underscores)."""
        for pretty_key in TARGET_DIMENSIONS.keys():
            # Derive raw key: "Mass Flow Rate" -> "mass_flow_rate"
            raw_key = pretty_key.lower().replace(" ", "_")
            try:
                _ = PintGlass(raw_key, "Input")
            except Exception as e:
                pytest.fail(f"PintGlass failed for raw key '{raw_key}': {e}")

    def test_all_caps_keys_work_in_pint_glass(self) -> None:
        """PintGlass should accept ALL CAPS keys (normalization)."""
        for pretty_key in TARGET_DIMENSIONS.keys():
            # Derive caps key: "Mass Flow Rate" -> "MASS_FLOW_RATE" (or "MASS FLOW RATE"?)
            # The normalization logic in core.py is: dimension.lower().replace(" ", "_")
            # So "MASS FLOW RATE" -> "mass flow rate" -> "mass_flow_rate".
            # "MASS_FLOW_RATE" -> "mass_flow_rate".
            
            # Case 1: Spaces
            caps_space = pretty_key.upper()
            try:
                _ = PintGlass(caps_space, "Input")
            except Exception as e:
                 pytest.fail(f"PintGlass failed for caps space key '{caps_space}': {e}")
                 
            # Case 2: Underscores
            caps_underscore = pretty_key.upper().replace(" ", "_")
            try:
                _ = PintGlass(caps_underscore, "Input")
            except Exception as e:
                 pytest.fail(f"PintGlass failed for caps underscore key '{caps_underscore}': {e}")


class TestNormalizationLogicDetailed:
    """Detailed tests for specific normalization edge cases."""
    
    def test_mixed_case_normalization(self) -> None:
        """Test mixed case inputs."""
        # "tEmPeRaTuRe" -> "temperature"
        assert get_preferred_unit("tEmPeRaTuRe", "si") == "kelvin"
        
        # "Mass Flow Rate" -> "mass_flow_rate"
        assert get_preferred_unit("Mass Flow Rate", "si") == "kilogram / second"

    def test_underscore_handling(self) -> None:
        """Test inputs with underscores vs spaces."""
        # "mass_flow_rate" -> "mass_flow_rate"
        assert get_preferred_unit("mass_flow_rate", "si") == "kilogram / second"
        
        # "mass flow rate" -> "mass_flow_rate"
        assert get_preferred_unit("mass flow rate", "si") == "kilogram / second"
