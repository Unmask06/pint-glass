"""PintGlass Context Module.

Provides context variable management for per-request unit system handling.
Uses Python's contextvars for thread-safe, async-safe context management.
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Literal

# Type alias for unit systems
UnitSystem = Literal["imperial", "si"]

# Context variable holding the current unit system
# Default is "imperial" as per spec
unit_context: ContextVar[str] = ContextVar("unit_context", default="imperial")


def get_unit_system() -> str:
    """Get the current unit system from context.

    Returns:
        The current unit system identifier (e.g., "imperial", "si").

    Example:
        >>> get_unit_system()
        'imperial'
    """
    return unit_context.get()


def set_unit_system(system: str) -> Token[str]:
    """Set the current unit system in context.

    Args:
        system: The unit system identifier to set (e.g., "imperial", "si").

    Returns:
        A token that can be used to reset the context to its previous value.

    Example:
        >>> token = set_unit_system("si")
        >>> get_unit_system()
        'si'
        >>> unit_context.reset(token)
        >>> get_unit_system()
        'imperial'
    """
    return unit_context.set(system)


def reset_unit_system(token: Token[str]) -> None:
    """Reset the unit system context to its previous value.

    Args:
        token: The token returned by a previous set_unit_system call.

    Example:
        >>> token = set_unit_system("si")
        >>> reset_unit_system(token)
        >>> get_unit_system()
        'imperial'
    """
    unit_context.reset(token)
