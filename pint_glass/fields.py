"""PintGlass Fields Module.

Provides the PintGlass factory function for creating Pydantic-compatible
annotated types with automatic unit conversion based on context.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, Literal

from pydantic import BeforeValidator, PlainSerializer

from pint_glass.context import get_unit_system
from pint_glass.core import convert_from_base, convert_to_base
from pint_glass.exceptions import UnitConversionError, UnsupportedDimensionError

# Type alias for model type
ModelType = Literal["Input", "Output"]


if TYPE_CHECKING:
    """Type checker sees this: PintGlass returns a type that's compatible with float."""
    def PintGlass(dimension: str, model_type: ModelType) -> type[float]: ...  # noqa: F811
else:

    def PintGlass(dimension: str, model_type: ModelType) -> Any:  # noqa: N802
        """Create an annotated type for a Pydantic field with automatic unit conversion.

    This factory function returns an `Annotated[float, ...]` type that converts
    between the user's preferred unit system and SI base units.

    Conversion direction depends on model_type:
    - "Input": Converts from preferred unit system → SI base units (for request models)
    - "Output": SI base units → preferred unit system (for response models)

    Args:
        dimension: Physical dimension key (e.g., "pressure", "length")
        model_type: The model type - "Input" or "Output".
            - "Input": User sends preferred units, stored as SI
            - "Output": Stored as SI, serialized to preferred units

    Returns:
        An Annotated type suitable for use as a Pydantic field type.

    Example:
        >>> from pydantic import BaseModel
        >>> from pint_glass import PintGlass, set_unit_system
        >>>
        >>> class PipeRequest(BaseModel):  # Input model
        ...     length: PintGlass("length", "Input")
        >>> class PipeResponse(BaseModel):  # Output model
        ...     length: PintGlass("length", "Output")
        >>>
        >>> set_unit_system("imperial")
        >>> req = PipeRequest(length=10)  # 10 ft → stored as 3.048 m
        >>> print(req.length)
        3.048
        >>>
        >>> resp = PipeResponse(length=3.048)  # 3.048 m → serialized as 10 ft
        >>> print(resp.model_dump())
        {'length': 10.0}

    Note:
        The conversion uses the unit system from context at the time of
        validation/serialization, making this suitable for per-request
        unit system handling in async frameworks like FastAPI.
    """
        if model_type == "Input":
            return _create_input_type(dimension)
        else:
            return _create_output_type(dimension)


def _create_input_type(dimension: str) -> Any:
    """Create Input type: preferred → SI (validation), SI → preferred (dump)."""

    def validate_to_base(value: Any) -> float:
        """BeforeValidator: Convert preferred units to base (SI) units."""
        system = get_unit_system()

        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Cannot convert {value!r} to a numeric value") from e

        try:
            return convert_to_base(float(value), dimension, system)
        except (UnsupportedDimensionError, UnitConversionError) as e:
            raise ValueError(str(e)) from e

    def serialize_from_base(value: float) -> float:
        """PlainSerializer: Convert internal base (SI) units back to preferred units."""
        system = get_unit_system()
        try:
            return convert_from_base(value, dimension, system)
        except (UnsupportedDimensionError, UnitConversionError) as e:
            # Serializers shouldn't typically fail if validation passed, but we handle it
            raise ValueError(str(e)) from e

    return Annotated[
        float,
        BeforeValidator(validate_to_base),
        PlainSerializer(serialize_from_base, return_type=float),
    ]


def _create_output_type(dimension: str) -> Any:
    """Create Output type: SI passthrough (valid), SI → preferred (dump)."""

    def validate_passthrough(value: Any) -> float:
        """BeforeValidator: Accept SI value directly (no conversion on input)."""
        if not isinstance(value, (int, float)):
            try:
                value = float(value)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Cannot convert {value!r} to a numeric value") from e

        return float(value)

    def serialize_to_preferred(value: float) -> float:
        """PlainSerializer: Convert SI base units to preferred units for output."""
        system = get_unit_system()
        try:
            return convert_from_base(value, dimension, system)
        except (UnsupportedDimensionError, UnitConversionError) as e:
            raise ValueError(str(e)) from e

    return Annotated[
        float,
        BeforeValidator(validate_passthrough),
        PlainSerializer(serialize_to_preferred, return_type=float),
    ]
