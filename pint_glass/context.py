"""PintGlass Context Module.

Provides context variable management for per-request unit system handling.
Uses Python's contextvars for thread-safe, async-safe context management.
"""

from __future__ import annotations

import warnings
from contextvars import ContextVar, Token
from typing import Literal

# Type alias for unit systems
UnitSystem = Literal["imperial", "si"]

# Supported unit systems - used for validation and warnings
SUPPORTED_SYSTEMS: frozenset[str] = frozenset({"imperial", "si"})

# Default unit system (can be configured at app startup)
DEFAULT_SYSTEM: str = "imperial"

# Context variable holding the current unit system
# Default is "imperial" as per spec
unit_context: ContextVar[str] = ContextVar("unit_context", default=DEFAULT_SYSTEM)

# Request-scoped cache for unit conversions (avoids redundant Pint computations)
# Key: (value, dimension, system, direction), Value: converted float
_request_cache: ContextVar[dict[tuple[float, str, str, str], float]] = ContextVar(
    "_request_cache", default={}
)


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

    If the system is not in SUPPORTED_SYSTEMS, a warning is emitted and
    the system falls back to DEFAULT_SYSTEM.

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
    system_lower = system.lower()
    if system_lower not in SUPPORTED_SYSTEMS:
        warnings.warn(
            f"Unknown unit system '{system}' — falling back to '{DEFAULT_SYSTEM}'. "
            f"Supported systems: {sorted(SUPPORTED_SYSTEMS)}. Did you mean 'si'?",
            UserWarning,
            stacklevel=2,
        )
        system_lower = DEFAULT_SYSTEM
    return unit_context.set(system_lower)


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


def get_request_cache() -> dict[tuple[float, str, str, str], float]:
    """Get the current request-scoped conversion cache.

    Returns:
        The cache dictionary for the current request context.
    """
    return _request_cache.get()


def set_request_cache(
    cache: dict[tuple[float, str, str, str], float],
) -> Token[dict[tuple[float, str, str, str], float]]:
    """Set a new request-scoped cache.

    Args:
        cache: The cache dictionary to set.

    Returns:
        A token that can be used to reset the cache to its previous value.
    """
    return _request_cache.set(cache)


def clear_request_cache() -> Token[dict[tuple[float, str, str, str], float]]:
    """Clear the request-scoped cache by setting a fresh empty dict.

    Returns:
        A token that can be used to reset the cache to its previous value.

    Note:
        Call this at the start of each request to ensure isolation.
    """
    return _request_cache.set({})
