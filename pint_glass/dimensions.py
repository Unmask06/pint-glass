"""PintGlass Dimensions Module.

Defines the mapping of dimension keys to their units in different unit systems.
This module contains the configuration for supported physical dimensions and their
corresponding units in Imperial and SI systems.
"""

from __future__ import annotations

from typing import TypedDict


class UnitMapping(TypedDict):
    """Type definition for unit system mappings.

    Attributes:
        imperial: Unit string for Imperial system.
        si: Unit string for International System of Units.
        cgs: Unit string for Centimeter-Gram-Second system.
        us: Unit string for US Customary system.
    """

    imperial: str
    si: str
    cgs: str
    us: str


# Mapping of dimension keys to their units in each system
# Format: dimension -> {system -> unit_string}
TARGET_DIMENSIONS: dict[str, UnitMapping] = {
    "pressure": {
        "imperial": "psi",
        "si": "pascal",
        "cgs": "barye",
        "us": "psi",
    },
    "length": {
        "imperial": "foot",
        "si": "meter",
        "cgs": "centimeter",
        "us": "foot",
    },
    "temperature": {
        "imperial": "degF",
        "si": "degC",
        "cgs": "degC",
        "us": "degF",
    },
    "mass": {
        "imperial": "pound",
        "si": "kilogram",
        "cgs": "gram",
        "us": "pound",
    },
    "time": {
        "imperial": "second",
        "si": "second",
        "cgs": "second",
        "us": "second",
    },
    "current": {
        "imperial": "ampere",
        "si": "ampere",
        "cgs": "ampere",
        "us": "ampere",
    },
    "luminosity": {
        "imperial": "candela",
        "si": "candela",
        "cgs": "candela",
        "us": "candela",
    },
    "substance": {
        "imperial": "mole",
        "si": "mole",
        "cgs": "mole",
        "us": "mole",
    },
    "area": {
        "imperial": "square_foot",
        "si": "meter ** 2",
        "cgs": "centimeter ** 2",
        "us": "square_foot",
    },
    "volume": {
        "imperial": "cubic_foot",
        "si": "meter ** 3",
        "cgs": "centimeter ** 3",
        "us": "cubic_foot",
    },
    "frequency": {
        "imperial": "hertz",
        "si": "hertz",
        "cgs": "hertz",
        "us": "hertz",
    },
    "wavenumber": {
        "imperial": "1 / foot",
        "si": "1 / meter",
        "cgs": "1 / centimeter",
        "us": "1 / foot",
    },
    "velocity": {
        "imperial": "foot / second",
        "si": "meter / second",
        "cgs": "centimeter / second",
        "us": "foot / second",
    },
    "speed": {
        "imperial": "foot / second",
        "si": "meter / second",
        "cgs": "centimeter / second",
        "us": "foot / second",
    },
    "volumetric_flow_rate": {
        "imperial": "cubic_foot / second",
        "si": "meter ** 3 / second",
        "cgs": "centimeter ** 3 / second",
        "us": "cubic_foot / second",
    },
    "acceleration": {
        "imperial": "foot / second ** 2",
        "si": "meter / second ** 2",
        "cgs": "centimeter / second ** 2",
        "us": "foot / second ** 2",
    },
    "force": {
        "imperial": "pound_force",
        "si": "newton",
        "cgs": "dyne",
        "us": "pound_force",
    },
    "energy": {
        "imperial": "foot_pound",
        "si": "joule",
        "cgs": "erg",
        "us": "foot_pound",
    },
    "power": {
        "imperial": "foot_pound / second",
        "si": "watt",
        "cgs": "erg / second",
        "us": "foot_pound / second",
    },
    "momentum": {
        "imperial": "pound * foot / second",
        "si": "kilogram * meter / second",
        "cgs": "gram * centimeter / second",
        "us": "pound * foot / second",
    },
    "density": {
        "imperial": "pound / cubic_foot",
        "si": "kilogram / meter ** 3",
        "cgs": "gram / centimeter ** 3",
        "us": "pound / foot ** 3",
    },
    "torque": {
        "imperial": "foot_pound",
        "si": "newton * meter",
        "cgs": "dyne * centimeter",
        "us": "foot_pound",
    },
    "viscosity": {
        "imperial": "pound / (foot * second)",
        "si": "pascal * second",
        "cgs": "poise",
        "us": "pound / (foot * second)",
    },
    "kinematic_viscosity": {
        "imperial": "square_foot / second",
        "si": "meter ** 2 / second",
        "cgs": "stokes",
        "us": "square_foot / second",
    },
}
