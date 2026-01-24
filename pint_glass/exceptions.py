"""PintGlass Exceptions Module.

Defines custom exception classes for the pint-glass library.
"""


class PintGlassError(Exception):
    """Base exception for all pint-glass related errors."""


class UnsupportedDimensionError(PintGlassError, KeyError):
    """Raised when a dimension is not found in the supported dimensions mapping."""


class UnitConversionError(PintGlassError, ValueError):
    """Raised when unit conversion fails."""
