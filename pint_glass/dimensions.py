"""PintGlass Dimensions Module.

Defines the mapping of dimension keys to their units in different unit systems.
This module contains the configuration for supported physical dimensions and their
corresponding units in Imperial and SI systems.
"""

from __future__ import annotations

from typing import TypedDict, get_type_hints


class UnitMapping(TypedDict):
    """Type definition for unit system mappings.

    Attributes:
        imperial: Unit string for Imperial system.
        si: Unit string for International System of Units.
        cgs: Unit string for Centimeter-Gram-Second system.
        us: Unit string for US Customary system.
        engg_si: Unit string for Engineering SI system.
        engg_field: Unit string for Engineering Field system.
    """

    imperial: str
    si: str
    cgs: str
    us: str
    engg_si: str
    engg_field: str


# Dynamically extract supported unit systems from UnitMapping keys


# This ensures UNIT_SYSTEMS stays in sync with the TypedDict definition


UNIT_SYSTEMS: frozenset[str] = frozenset(get_type_hints(UnitMapping).keys())





# Default unit system to use when none is specified or recognized


DEFAULT_SYSTEM: str = "engg_si"





# Base unit system used for internal storage and conversions (usually SI)


BASE_SYSTEM: str = "si"


# Mapping of dimension keys to their units in each system
# Format: dimension -> {system -> unit_string}
_TARGET_DIMENSIONS_RAW: dict[str, UnitMapping] = {
    "pressure": {
        "imperial": "psi",
        "si": "pascal",
        "cgs": "barye",
        "us": "psi",
        "engg_si": "bar",
        "engg_field": "psi",
    },
    "length": {
        "imperial": "foot",
        "si": "meter",
        "cgs": "centimeter",
        "us": "foot",
        "engg_si": "meter",
        "engg_field": "foot",
    },
    "temperature": {
        "imperial": "degF",
        "si": "kelvin",
        "cgs": "degC",
        "us": "degF",
        "engg_si": "degC",
        "engg_field": "degF",
    },
    "mass": {
        "imperial": "pound",
        "si": "kilogram",
        "cgs": "gram",
        "us": "pound",
        "engg_si": "kilogram",
        "engg_field": "pound",
    },
    "time": {
        "imperial": "second",
        "si": "second",
        "cgs": "second",
        "us": "second",
        "engg_si": "second",
        "engg_field": "second",
    },
    "current": {
        "imperial": "ampere",
        "si": "ampere",
        "cgs": "ampere",
        "us": "ampere",
        "engg_si": "ampere",
        "engg_field": "ampere",
    },
    "luminosity": {
        "imperial": "candela",
        "si": "candela",
        "cgs": "candela",
        "us": "candela",
        "engg_si": "candela",
        "engg_field": "candela",
    },
    "substance": {
        "imperial": "mole",
        "si": "mole",
        "cgs": "mole",
        "us": "mole",
        "engg_si": "mole",
        "engg_field": "mole",
    },
    "area": {
        "imperial": "foot ** 2",
        "si": "meter ** 2",
        "cgs": "centimeter ** 2",
        "us": "foot ** 2",
        "engg_si": "meter ** 2",
        "engg_field": "foot ** 2",
    },
    "volume": {
        "imperial": "foot ** 3",
        "si": "meter ** 3",
        "cgs": "centimeter ** 3",
        "us": "foot ** 3",
        "engg_si": "meter ** 3",
        "engg_field": "foot ** 3",
    },
    "frequency": {
        "imperial": "hertz",
        "si": "hertz",
        "cgs": "hertz",
        "us": "hertz",
        "engg_si": "hertz",
        "engg_field": "hertz",
    },
    "wavenumber": {
        "imperial": "1 / foot",
        "si": "1 / meter",
        "cgs": "1 / centimeter",
        "us": "1 / foot",
        "engg_si": "1 / meter",
        "engg_field": "1 / foot",
    },
    "velocity": {
        "imperial": "foot / second",
        "si": "meter / second",
        "cgs": "centimeter / second",
        "us": "foot / second",
        "engg_si": "meter / second",
        "engg_field": "foot / second",
    },
    "speed": {
        "imperial": "foot / second",
        "si": "meter / second",
        "cgs": "centimeter / second",
        "us": "foot / second",
        "engg_si": "meter / second",
        "engg_field": "foot / second",
    },
    "mass_flow_rate": {
        "imperial": "pound / second",
        "si": "kilogram / second",
        "cgs": "gram / second",
        "us": "pound / second",
        "engg_si": "kilogram / hour",
        "engg_field": "pound / hour",
    },
    "volumetric_flow_rate": {
        "imperial": "foot ** 3 / second",
        "si": "meter ** 3 / second",
        "cgs": "centimeter ** 3 / second",
        "us": "foot ** 3 / second",
        "engg_si": "meter ** 3 / hour",
        "engg_field": "foot ** 3 / hour",
    },
    "acceleration": {
        "imperial": "foot / second ** 2",
        "si": "meter / second ** 2",
        "cgs": "centimeter / second ** 2",
        "us": "foot / second ** 2",
        "engg_si": "meter / second ** 2",
        "engg_field": "foot / second ** 2",
    },
    "force": {
        "imperial": "pound_force",
        "si": "newton",
        "cgs": "dyne",
        "us": "pound_force",
        "engg_si": "newton",
        "engg_field": "pound_force",
    },
    "energy": {
        "imperial": "foot_pound",
        "si": "joule",
        "cgs": "erg",
        "us": "foot_pound",
        "engg_si": "joule",
        "engg_field": "foot_pound",
    },
    "power": {
        "imperial": "foot_pound / second",
        "si": "watt",
        "cgs": "erg / second",
        "us": "foot_pound / second",
        "engg_si": "watt",
        "engg_field": "foot_pound / second",
    },
    "momentum": {
        "imperial": "pound * foot / second",
        "si": "kilogram * meter / second",
        "cgs": "gram * centimeter / second",
        "us": "pound * foot / second",
        "engg_si": "kilogram * meter / second",
        "engg_field": "pound * foot / second",
    },
    "density": {
        "imperial": "pound / foot ** 3",
        "si": "kilogram / meter ** 3",
        "cgs": "gram / centimeter ** 3",
        "us": "pound / foot ** 3",
        "engg_si": "kilogram / meter ** 3",
        "engg_field": "pound / foot ** 3",
    },
    "torque": {
        "imperial": "foot_pound",
        "si": "newton * meter",
        "cgs": "dyne * centimeter",
        "us": "foot_pound",
        "engg_si": "newton * meter",
        "engg_field": "foot_pound",
    },
    "viscosity": {
        "imperial": "pound / (foot * second)",
        "si": "pascal * second",
        "cgs": "poise",
        "us": "pound / (foot * second)",
        "engg_si": "pascal * second",
        "engg_field": "pound / (foot * second)",
    },
    "kinematic_viscosity": {
        "imperial": "square_foot / second",
        "si": "meter ** 2 / second",
        "cgs": "stokes",
        "us": "square_foot / second",
        "engg_si": "meter ** 2 / second",
        "engg_field": "square_foot / second",
    },
}


def get_pretty_dimensions() -> dict[str, dict[str, str]]:
    """Get a pretty-formatted version of TARGET_DIMENSIONS.

    Returns:
        A dictionary with the same structure as TARGET_DIMENSIONS, but with:
        - Keys converted to Title Case (e.g., "mass_flow_rate" -> "Mass Flow Rate")
        - Unit strings formatted to be human-readable (e.g., "m**2" -> "m²")
    """
    import pint

    # Create a local registry to avoid side effects or circular imports
    ureg = pint.UnitRegistry()

    pretty_dims = {}
    for dim_key, unit_map in _TARGET_DIMENSIONS_RAW.items():
        # Convert key: "mass_flow_rate" -> "Mass Flow Rate"
        pretty_key = dim_key.replace("_", " ").title()

        pretty_map = {}
        # Iterate over the UnitMapping (typed dict behaves like dict at runtime)
        for system, unit_str in unit_map.items():
            try:
                # Create a Unit object and format it
                # ~P: Short Pretty format (e.g., km/h, m², etc.)
                unit_obj = ureg.Unit(unit_str)
                pretty_unit = format(unit_obj, "~P")
                pretty_map[system] = pretty_unit
            except Exception:
                # If pint fails to parse or format, keep original string
                pretty_map[system] = unit_str
        
        pretty_dims[pretty_key] = pretty_map

    return pretty_dims


TARGET_DIMENSIONS: dict[str, dict[str, str]] = get_pretty_dimensions()