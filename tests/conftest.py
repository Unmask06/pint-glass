"""Pytest configuration and fixtures for PintGlass tests."""

import pytest

from pint_glass import set_unit_system, unit_context


@pytest.fixture
def imperial_context():
    """Fixture that ensures imperial unit system context."""
    token = set_unit_system("imperial")
    yield
    unit_context.reset(token)


@pytest.fixture
def si_context():
    """Fixture that ensures SI unit system context."""
    token = set_unit_system("si")
    yield
    unit_context.reset(token)


@pytest.fixture
def reset_context():
    """Fixture that resets context after each test."""
    original = unit_context.get()
    yield
    set_unit_system(original)
