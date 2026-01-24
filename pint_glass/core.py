"""PintGlass Core Module.

Manages the Pint UnitRegistry and provides unit resolution/conversion functions.
Handles mapping between dimensions (e.g., "pressure") and their corresponding
units in different unit systems (Imperial, SI).
"""

from __future__ import annotations

from typing import Literal

import pint

from pint_glass.dimensions import TARGET_DIMENSIONS

# Singleton UnitRegistry instance
ureg: pint.UnitRegistry = pint.UnitRegistry()  # type: ignore[type-arg]


# Type alias for supported unit systems
UnitSystem = Literal["imperial", "si"]


# Base units are always SI
BASE_SYSTEM: UnitSystem = "si"


def get_preferred_unit(dimension: str, system: str) -> str:
    """Get the preferred unit for a dimension in a given unit system.

    Args:
        dimension: The physical dimension key (e.g., "pressure", "length")
        system: The unit system identifier (e.g., "imperial", "si")

    Returns:
        The unit string for the given dimension and system.

    Raises:
        KeyError: If the dimension is not supported.
        KeyError: If the system is not supported for this dimension.
    """
    if dimension not in TARGET_DIMENSIONS:
        raise KeyError(
            f"Unknown dimension '{dimension}'. "
            f"Supported dimensions: {list(TARGET_DIMENSIONS.keys())}"
        )

    system_lower = system.lower()
    dim_units = TARGET_DIMENSIONS[dimension]

    if system_lower not in dim_units:
        # Fallback to imperial if system not recognized
        system_lower = "imperial"

    return dim_units[system_lower]


def get_base_unit(dimension: str) -> str:
    """Get the base (SI) unit for a dimension.

    Args:
        dimension: The physical dimension key (e.g., "pressure", "length")

    Returns:
        The SI base unit string for the given dimension.

    Raises:
        KeyError: If the dimension is not supported.
    """
    return get_preferred_unit(dimension, BASE_SYSTEM)


def convert_to_base(value: float, dimension: str, system: str) -> float:
    """Convert a value from the preferred unit system to the base (SI) unit.

    This is used during input validation to store values in a consistent format.

    Args:
        value: The numeric value in the source unit system.
        dimension: The physical dimension key.
        system: The source unit system.

    Returns:
        The value converted to SI base units.

    Example:
        >>> convert_to_base(14.7, "pressure", "imperial")
        101352.932...  # 14.7 psi in pascals
    """
    source_unit = get_preferred_unit(dimension, system)
    target_unit = get_base_unit(dimension)

    # Create quantity and convert
    quantity = ureg.Quantity(value, source_unit)
    converted = quantity.to(target_unit)

    return float(converted.magnitude)


def convert_from_base(value: float, dimension: str, system: str) -> float:
    """Convert a value from the base (SI) unit to the preferred unit system.

    This is used during serialization to return values in the user's preferred format.

    Args:
        value: The numeric value in SI base units.
        dimension: The physical dimension key.
        system: The target unit system.

    Returns:
        The value converted to the target unit system.

    Example:
        >>> convert_from_base(101325, "pressure", "imperial")
        14.695...  # 101325 pascals in psi
    """
    source_unit = get_base_unit(dimension)
    target_unit = get_preferred_unit(dimension, system)

    # Create quantity and convert
    quantity = ureg.Quantity(value, source_unit)
    converted = quantity.to(target_unit)

    return float(converted.magnitude)
