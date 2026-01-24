"""Tests for pint_glass.context module."""

from pint_glass.context import (
    get_unit_system,
    reset_unit_system,
    set_unit_system,
    unit_context,
)


class TestUnitContext:
    """Tests for unit_context ContextVar."""

    def test_default_value_is_imperial(self) -> None:
        """Default context value should be 'imperial'."""
        assert unit_context.get() == "imperial"

    def test_set_and_get(self) -> None:
        """Setting context should update the value."""
        token = unit_context.set("si")
        try:
            assert unit_context.get() == "si"
        finally:
            unit_context.reset(token)

    def test_reset_restores_previous(self) -> None:
        """Reset should restore previous value."""
        original = unit_context.get()
        token = unit_context.set("si")
        unit_context.reset(token)
        assert unit_context.get() == original


class TestGetUnitSystem:
    """Tests for get_unit_system helper function."""

    def test_returns_current_value(self) -> None:
        """Should return current context value."""
        token = unit_context.set("test_system")
        try:
            assert get_unit_system() == "test_system"
        finally:
            unit_context.reset(token)

    def test_returns_imperial_by_default(self) -> None:
        """Should return imperial when no context set."""
        result = get_unit_system()
        assert result == "imperial"


class TestSetUnitSystem:
    """Tests for set_unit_system helper function."""

    def test_sets_context_value(self) -> None:
        """Should set the context to given value."""
        token = set_unit_system("si")
        try:
            assert unit_context.get() == "si"
        finally:
            unit_context.reset(token)

    def test_returns_token(self) -> None:
        """Should return a token for reset."""
        token = set_unit_system("si")
        assert token is not None
        unit_context.reset(token)

    def test_multiple_sets(self) -> None:
        """Multiple sets should each return valid tokens."""
        token1 = set_unit_system("si")
        token2 = set_unit_system("imperial")

        assert unit_context.get() == "imperial"
        unit_context.reset(token2)
        assert unit_context.get() == "si"
        unit_context.reset(token1)


class TestResetUnitSystem:
    """Tests for reset_unit_system helper function."""

    def test_resets_to_previous_value(self) -> None:
        """Should reset context to previous value."""
        original = unit_context.get()
        token = set_unit_system("si")
        reset_unit_system(token)
        assert unit_context.get() == original

    def test_works_with_set_unit_system(self) -> None:
        """Should work in conjunction with set_unit_system."""
        token = set_unit_system("si")
        assert get_unit_system() == "si"
        reset_unit_system(token)
        assert get_unit_system() == "imperial"
