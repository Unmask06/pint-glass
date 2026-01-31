"""PintGlass Core Module.

Manages the Pint UnitRegistry and provides unit resolution/conversion functions.
Handles mapping between dimensions (e.g., "pressure") and their corresponding
units in different unit systems (Imperial, SI).
"""

from __future__ import annotations

import pint

from pint_glass.context import get_request_cache
from pint_glass.dimensions import (
    BASE_SYSTEM,
    DEFAULT_SYSTEM,
    _TARGET_DIMENSIONS_RAW as TARGET_DIMENSIONS,
)
from pint_glass.exceptions import UnitConversionError, UnsupportedDimensionError

# Singleton UnitRegistry instance
ureg: pint.UnitRegistry = pint.UnitRegistry()  # type: ignore[type-arg]


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
    # Normalize dimension: "Temperature" -> "temperature", "Mass Flow Rate" -> "mass_flow_rate"
    dim_normalized = dimension.lower().replace(" ", "_")

    if dim_normalized not in TARGET_DIMENSIONS:
        supported = ", ".join(f"'{d}'" for d in TARGET_DIMENSIONS.keys())
        raise UnsupportedDimensionError(
            f"Unsupported dimension '{dimension}'; supported: {supported}"
        )

    system_lower = system.lower()
    dim_units = TARGET_DIMENSIONS[dim_normalized]

    if system_lower not in dim_units:
        # Fallback to default if system not recognized
        system_lower = DEFAULT_SYSTEM

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
    Uses request-scoped caching to avoid redundant Pint computations.

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
    cache_key = (value, dimension, system, "to_base")
    cache = get_request_cache()

    if cache_key in cache:
        return cache[cache_key]

    source_unit = get_preferred_unit(dimension, system)
    target_unit = get_base_unit(dimension)

    # Create quantity and convert
    try:
        quantity = ureg.Quantity(value, source_unit)
        converted = quantity.to(target_unit)
    except (pint.UndefinedUnitError, pint.DimensionalityError) as e:
        raise UnitConversionError(
            f"Conversion failed for dimension '{dimension}' from '{source_unit}' to '{target_unit}': {e}"
        ) from e

    result = float(converted.magnitude)
    cache[cache_key] = result
    return result


def convert_from_base(value: float, dimension: str, system: str) -> float:
    """Convert a value from the base (SI) unit to the preferred unit system.

    This is used during serialization to return values in the user's preferred format.
    Uses request-scoped caching to avoid redundant Pint computations.

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
    cache_key = (value, dimension, system, "from_base")
    cache = get_request_cache()

    if cache_key in cache:
        return cache[cache_key]

    source_unit = get_base_unit(dimension)
    target_unit = get_preferred_unit(dimension, system)

    # Create quantity and convert
    try:
        quantity = ureg.Quantity(value, source_unit)
        converted = quantity.to(target_unit)
    except (pint.UndefinedUnitError, pint.DimensionalityError) as e:
        raise UnitConversionError(
            f"Conversion failed for dimension '{dimension}' from '{source_unit}' to '{target_unit}': {e}"
        ) from e

    result = float(converted.magnitude)
    cache[cache_key] = result
    return result
