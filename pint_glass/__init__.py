"""PintGlass - A Pydantic + Pint integration library for seamless unit conversion.

This library bridges the gap between physical unit handling (via Pint) and
data validation (via Pydantic), enabling context-aware unit conversion in
FastAPI and other async Python applications.

Key Features:
- Seamless Integration: Works directly with pydantic.BaseModel
- Context Awareness: Uses contextvars for per-request unit systems
- Bidirectional Conversion: Preferred units ↔ Base units
- Model Type Support: Separate Input/Output model handling
- Zero-Overhead Models: Fields are pure float types at runtime
"""

from pint_glass.context import (
    SUPPORTED_SYSTEMS,
    clear_request_cache,
    get_request_cache,
    get_unit_system,
    reset_unit_system,
    set_request_cache,
    set_unit_system,
    unit_context,
)
from pint_glass.core import (
    convert_from_base,
    convert_to_base,
    get_base_unit,
    get_preferred_unit,
    ureg,
)
from pint_glass.dimensions import (
    BASE_SYSTEM,
    DEFAULT_SYSTEM,
    TARGET_DIMENSIONS,
    UNIT_SYSTEMS,
    export_dimensions,
)
from pint_glass.exceptions import (
    PintGlassError,
    UnitConversionError,
    UnsupportedDimensionError,
)
from pint_glass.fields import ModelType, PintGlass

__version__ = "0.1.0"

__all__ = [
    "BASE_SYSTEM",
    "DEFAULT_SYSTEM",
    "SUPPORTED_SYSTEMS",
    "TARGET_DIMENSIONS",
    "UNIT_SYSTEMS",
    "export_dimensions",
    "ModelType",
    # Primary API
    "PintGlass",
    "convert_from_base",
    "convert_to_base",
    "get_base_unit",
    "get_preferred_unit",
    # Context helpers
    "clear_request_cache",
    "get_request_cache",
    "get_unit_system",
    "reset_unit_system",
    "set_request_cache",
    "set_unit_system",
    "unit_context",
    # Core utilities
    "ureg",
    # Exceptions
    "PintGlassError",
    "UnitConversionError",
    "UnsupportedDimensionError",
]
