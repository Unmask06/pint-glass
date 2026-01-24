"""Tests for pint_glass.core module."""

import pytest

from pint_glass.core import (
    TARGET_DIMENSIONS,
    convert_from_base,
    convert_to_base,
    get_base_unit,
    get_preferred_unit,
    ureg,
)


class TestTargetDimensions:
    """Tests for TARGET_DIMENSIONS configuration."""

    def test_all_dimensions_have_imperial_and_si(self) -> None:
        """All dimensions should have both imperial and si mappings."""
        for dimension, units in TARGET_DIMENSIONS.items():
            assert "imperial" in units, f"{dimension} missing imperial unit"
            assert "si" in units, f"{dimension} missing si unit"

    def test_expected_dimensions_exist(self) -> None:
        """Core dimensions should be defined."""
        expected = ["pressure", "length", "temperature", "mass", "time"]
        for dim in expected:
            assert dim in TARGET_DIMENSIONS, f"Missing dimension: {dim}"


class TestGetPreferredUnit:
    """Tests for get_preferred_unit function."""

    @pytest.mark.parametrize(
        ("dimension", "system", "expected"),
        [
            ("pressure", "imperial", "psi"),
            ("pressure", "si", "pascal"),
            ("length", "imperial", "foot"),
            ("length", "si", "meter"),
            ("temperature", "imperial", "degF"),
            ("temperature", "si", "degC"),
            ("mass", "imperial", "pound"),
            ("mass", "si", "kilogram"),
            ("time", "imperial", "second"),
            ("time", "si", "second"),
        ],
    )
    def test_returns_correct_unit(
        self, dimension: str, system: str, expected: str
    ) -> None:
        """Should return the correct unit for dimension and system."""
        result = get_preferred_unit(dimension, system)
        assert result == expected

    def test_case_insensitive_system(self) -> None:
        """System lookup should be case-insensitive."""
        assert get_preferred_unit("pressure", "IMPERIAL") == "psi"
        assert get_preferred_unit("pressure", "Imperial") == "psi"
        assert get_preferred_unit("pressure", "SI") == "pascal"

    def test_unknown_dimension_raises(self) -> None:
        """Unknown dimension should raise KeyError."""
        with pytest.raises(KeyError, match="Unknown dimension"):
            get_preferred_unit("unknown", "imperial")

    def test_unknown_system_falls_back_to_imperial(self) -> None:
        """Unknown system should fall back to imperial."""
        result = get_preferred_unit("pressure", "unknown_system")
        assert result == "psi"


class TestGetBaseUnit:
    """Tests for get_base_unit function."""

    @pytest.mark.parametrize(
        ("dimension", "expected"),
        [
            ("pressure", "pascal"),
            ("length", "meter"),
            ("temperature", "degC"),
            ("mass", "kilogram"),
            ("time", "second"),
        ],
    )
    def test_returns_si_unit(self, dimension: str, expected: str) -> None:
        """Base unit should always be SI."""
        result = get_base_unit(dimension)
        assert result == expected


class TestConvertToBase:
    """Tests for convert_to_base function."""

    def test_psi_to_pascal(self) -> None:
        """14.7 psi should be approximately 101325 Pa (1 atm)."""
        result = convert_to_base(14.696, "pressure", "imperial")
        assert abs(result - 101325) < 100

    def test_feet_to_meters(self) -> None:
        """1 foot should be 0.3048 meters."""
        result = convert_to_base(1, "length", "imperial")
        assert abs(result - 0.3048) < 0.0001

    def test_fahrenheit_to_celsius(self) -> None:
        """212°F should be 100°C (boiling point)."""
        result = convert_to_base(212, "temperature", "imperial")
        assert abs(result - 100) < 0.1

    def test_32f_to_0c(self) -> None:
        """32°F should be 0°C (freezing point)."""
        result = convert_to_base(32, "temperature", "imperial")
        assert abs(result - 0) < 0.1

    def test_si_to_si_no_change(self) -> None:
        """SI input should remain unchanged."""
        result = convert_to_base(100, "pressure", "si")
        assert result == 100.0


class TestConvertFromBase:
    """Tests for convert_from_base function."""

    def test_pascal_to_psi(self) -> None:
        """101325 Pa should be approximately 14.696 psi."""
        result = convert_from_base(101325, "pressure", "imperial")
        assert abs(result - 14.696) < 0.01

    def test_meters_to_feet(self) -> None:
        """1 meter should be approximately 3.281 feet."""
        result = convert_from_base(1, "length", "imperial")
        assert abs(result - 3.28084) < 0.001

    def test_celsius_to_fahrenheit(self) -> None:
        """100°C should be 212°F."""
        result = convert_from_base(100, "temperature", "imperial")
        assert abs(result - 212) < 0.1

    def test_0c_to_32f(self) -> None:
        """0°C should be 32°F."""
        result = convert_from_base(0, "temperature", "imperial")
        assert abs(result - 32) < 0.1

    def test_si_to_si_no_change(self) -> None:
        """SI output should remain unchanged."""
        result = convert_from_base(100, "pressure", "si")
        assert result == 100.0


class TestRoundTrip:
    """Tests for round-trip conversions."""

    @pytest.mark.parametrize(
        "dimension", ["pressure", "length", "temperature", "mass", "time"]
    )
    def test_imperial_round_trip(self, dimension: str) -> None:
        """Converting to base and back should preserve the value."""
        original = 100.0
        base = convert_to_base(original, dimension, "imperial")
        result = convert_from_base(base, dimension, "imperial")
        assert abs(result - original) < 0.0001

    @pytest.mark.parametrize(
        "dimension", ["pressure", "length", "temperature", "mass", "time"]
    )
    def test_si_round_trip(self, dimension: str) -> None:
        """SI round trips should be exact."""
        original = 100.0
        base = convert_to_base(original, dimension, "si")
        result = convert_from_base(base, dimension, "si")
        assert abs(result - original) < 0.0001


class TestUnitRegistry:
    """Tests for unit registry singleton."""

    def test_ureg_exists(self) -> None:
        """Unit registry should be available."""
        assert ureg is not None

    def test_ureg_can_create_quantity(self) -> None:
        """Should be able to create quantities."""
        q = ureg.Quantity(100, "psi")
        assert q.magnitude == 100
