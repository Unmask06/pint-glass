"""Tests for pint_glass.dimensions module."""

import pytest

from pint_glass.core import ureg
from pint_glass.dimensions import TARGET_DIMENSIONS, UNIT_SYSTEMS


class TestTargetDimensionsStructure:
    """Tests for the structure and validity of TARGET_DIMENSIONS."""

    def test_all_dimensions_have_required_systems(self) -> None:
        """All dimensions should have imperial, si, cgs, and us systems."""
        required_systems = set(UNIT_SYSTEMS)
        for dimension, systems in TARGET_DIMENSIONS.items():
            assert set(systems.keys()) == required_systems, (
                f"Dimension '{dimension}' missing required systems. "
                f"Has: {set(systems.keys())}, Required: {required_systems}"
            )

    def test_all_units_are_valid_pint_units(self) -> None:
        """All unit strings in TARGET_DIMENSIONS should be valid pint units."""
        for dimension, systems in TARGET_DIMENSIONS.items():
            for system, unit_str in systems.items():
                try:
                    ureg.Quantity(1, unit_str)
                except Exception as e:
                    pytest.fail(
                        f"Invalid unit '{unit_str}' for dimension '{dimension}' "
                        f"in system '{system}': {e}"
                    )

    def test_no_empty_unit_strings(self) -> None:
        """No unit strings should be empty."""
        for dimension, systems in TARGET_DIMENSIONS.items():
            for system, unit_str in systems.items():
                assert unit_str.strip(), (
                    f"Empty unit string for dimension '{dimension}' "
                    f"in system '{system}'"
                )

    def test_dimensions_are_strings(self) -> None:
        """All dimension keys should be strings."""
        for dimension in TARGET_DIMENSIONS.keys():
            assert isinstance(
                dimension, str
            ), f"Dimension key '{dimension}' is not a string"

    def test_unit_strings_are_strings(self) -> None:
        """All unit values should be strings."""
        for dimension, systems in TARGET_DIMENSIONS.items():
            for system, unit_str in systems.items():
                assert isinstance(unit_str, str), (
                    f"Unit for dimension '{dimension}' in system '{system}' "
                    f"is not a string: {type(unit_str)}"
                )

    def test_common_dimensions_present(self) -> None:
        """Common physical dimensions should be present."""
        expected_dimensions = {
            "Pressure",
            "Length",
            "Temperature",
            "Mass",
            "Time",
            "Area",
            "Volume",
            "Velocity",
            "Force",
            "Energy",
        }
        actual_dimensions = set(TARGET_DIMENSIONS.keys())
        missing = expected_dimensions - actual_dimensions
        assert not missing, f"Missing expected dimensions: {missing}"

    def test_temperature_handling(self) -> None:
        """Temperature dimensions should use degree units appropriately."""
        temp_units = TARGET_DIMENSIONS["Temperature"]
        # Check that temperature uses degF and degC (pretty versions)
        # Note: ~P formatting: degF -> °F, degC -> °C
        assert temp_units["imperial"] == "°F"
        assert temp_units["us"] == "°F"
        assert temp_units["si"] == "K"
        assert temp_units["cgs"] == "°C"
