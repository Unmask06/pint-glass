# PintGlass Usage Guide 🍺

A comprehensive guide for using PintGlass — the seamless Pydantic + Pint integration library for Python APIs.

## Table of Contents

- [Installation](#installation)
- [Core Concepts](#core-concepts)
- [Basic Usage](#basic-usage)
- [FastAPI Integration](#fastapi-integration)
- [Supported Dimensions](#supported-dimensions)
- [Unit Systems](#unit-systems)
- [Advanced Usage](#advanced-usage)
- [Error Handling](#error-handling)
- [API Reference](#api-reference)
- [Best Practices](#best-practices)

---

## Installation

```bash
# Using uv (recommended)
uv add pint-glass

# Using pip
pip install pint-glass
```

---

## Core Concepts

PintGlass simplifies unit conversion in APIs by:

1. **Automatic Conversion**: Input values are converted from user-preferred units to SI base units on validation.
2. **Context-Aware**: Uses `contextvars` for per-request unit system handling (async-safe).
3. **Bidirectional**: Converts user → SI on input, SI → user on serialization.
4. **Zero-Overhead**: Field values are pure `float` at runtime — no complex objects.

### How It Works

```
┌─────────────────┐     PintGlass      ┌─────────────────┐     PintGlass       ┌─────────────────┐
│   User Input    │  ──────────────►   │   Internal SI   │  ───────────────►   │  API Response   │
│  (imperial/si)  │  (validation)      │   (base units)  │  (serialization)    │  (imperial/si)  │
└─────────────────┘                    └─────────────────┘                     └─────────────────┘
```

---

## Basic Usage

### Defining Models with PintGlass Fields

```python
from pydantic import BaseModel
from pint_glass import PintGlass, set_unit_system

# Define a model with unit-aware fields
class TankSpecification(BaseModel):
    pressure: PintGlass("pressure", "Input")       # psi ↔ pascals
    height: PintGlass("length", "Input")           # feet ↔ meters
    capacity: PintGlass("volume", "Input")         # cubic feet ↔ cubic meters
    max_temperature: PintGlass("temperature", "Input")  # °F ↔ °C


# Set the unit system context
set_unit_system("imperial")

# Create a model instance — values are in imperial units
tank = TankSpecification(
    pressure=150,        # 150 psi → stored as ~1,034,213 Pa
    height=10,           # 10 ft → stored as 3.048 m
    capacity=500,        # 500 ft³ → stored as ~14.16 m³
    max_temperature=200  # 200°F → stored as ~93.3°C
)

# Access internal values (always SI)
print(f"Internal pressure: {tank.pressure} Pa")
print(f"Internal height: {tank.height} m")

# Serialize back to user-preferred units
print(tank.model_dump())
# Output: {'pressure': 150.0, 'height': 10.0, 'capacity': 500.0, 'max_temperature': 200.0}
```

### Input vs Output Models

PintGlass supports two model types for different use cases:

```python
from pydantic import BaseModel
from pint_glass import PintGlass

# Input Model: User sends preferred units → stored as SI
class PipeRequest(BaseModel):
    length: PintGlass("length", "Input")    # 10 ft → 3.048 m
    pressure: PintGlass("pressure", "Input")


# Output Model: SI values → serialized to preferred units
class PipeResponse(BaseModel):
    length: PintGlass("length", "Output")    # 3.048 m → 10 ft
    pressure: PintGlass("pressure", "Output")
```

**Key Difference:**

- `"Input"`: Converts during validation (user units → SI)
- `"Output"`: Passes SI through, converts only during serialization (SI → user units)

---

## FastAPI Integration

### Middleware-Based Approach (Recommended)

```python
from fastapi import FastAPI, Request
from pydantic import BaseModel
from pint_glass import PintGlass, set_unit_system, reset_unit_system

app = FastAPI()


# Middleware to set unit system from request header
@app.middleware("http")
async def unit_system_middleware(request: Request, call_next):
    # Read unit system from X-Unit-System header (default: imperial)
    system = request.headers.get("X-Unit-System", "imperial").lower()

    # Set context for this request
    token = set_unit_system(system)
    try:
        response = await call_next(request)
        return response
    finally:
        # Always reset to avoid leaking context
        reset_unit_system(token)


# Request/Response models
class PumpRequest(BaseModel):
    flow_rate: PintGlass("volumetric_flow_rate", "Input")
    head_pressure: PintGlass("pressure", "Input")


class PumpResponse(BaseModel):
    flow_rate: PintGlass("volumetric_flow_rate", "Output")
    head_pressure: PintGlass("pressure", "Output")
    status: str


@app.post("/pumps/calculate", response_model=PumpResponse)
async def calculate_pump(request: PumpRequest):
    # Business logic works with SI units internally
    print(f"Flow rate (m³/s): {request.flow_rate}")
    print(f"Pressure (Pa): {request.head_pressure}")

    # Return response — automatically converted to user's preferred units
    return PumpResponse(
        flow_rate=request.flow_rate,
        head_pressure=request.head_pressure,
        status="calculated"
    )
```

### Making Requests

```bash
# Imperial units (default)
curl -X POST "http://localhost:8000/pumps/calculate" \
  -H "Content-Type: application/json" \
  -H "X-Unit-System: imperial" \
  -d '{"flow_rate": 100, "head_pressure": 50}'

# Response: {"flow_rate": 100.0, "head_pressure": 50.0, "status": "calculated"}


# SI units
curl -X POST "http://localhost:8000/pumps/calculate" \
  -H "Content-Type: application/json" \
  -H "X-Unit-System: si" \
  -d '{"flow_rate": 2.83, "head_pressure": 344737.86}'

# Response: {"flow_rate": 2.83, "head_pressure": 344737.86, "status": "calculated"}
```

### Dependency Injection Alternative

```python
from typing import Annotated
from fastapi import FastAPI, Header, Depends
from pint_glass import set_unit_system, reset_unit_system

app = FastAPI()


async def get_unit_system(x_unit_system: Annotated[str | None, Header()] = None):
    """Dependency to manage unit system context."""
    system = (x_unit_system or "imperial").lower()
    token = set_unit_system(system)
    try:
        yield system
    finally:
        reset_unit_system(token)


@app.post("/items")
async def create_item(
    item: ItemRequest,
    unit_system: str = Depends(get_unit_system)
):
    # unit_system is now set in context
    return {"received_system": unit_system, "data": item.model_dump()}
```

---

## Supported Dimensions

PintGlass supports 21 physical dimensions out of the box:

| Dimension              | Imperial Unit       | SI Unit               | CGS Unit               |
| ---------------------- | ------------------- | --------------------- | ---------------------- |
| `pressure`             | psi                 | pascal                | barye                  |
| `length`               | foot                | meter                 | centimeter             |
| `temperature`          | degF                | degC                  | degC                   |
| `mass`                 | pound               | kilogram              | gram                   |
| `time`                 | second              | second                | second                 |
| `current`              | ampere              | ampere                | ampere                 |
| `luminosity`           | candela             | candela               | candela                |
| `substance`            | mole                | mole                  | mole                   |
| `area`                 | square_foot         | meter²                | centimeter²            |
| `volume`               | cubic_foot          | meter³                | centimeter³            |
| `frequency`            | hertz               | hertz                 | hertz                  |
| `wavenumber`           | 1/foot              | 1/meter               | 1/centimeter           |
| `velocity`             | foot/second         | meter/second          | centimeter/second      |
| `speed`                | foot/second         | meter/second          | centimeter/second      |
| `volumetric_flow_rate` | cubic_foot/second   | meter³/second         | centimeter³/second     |
| `acceleration`         | foot/second²        | meter/second²         | centimeter/second²     |
| `force`                | pound_force         | newton                | dyne                   |
| `energy`               | foot_pound          | joule                 | erg                    |
| `power`                | foot_pound/second   | watt                  | erg/second             |
| `momentum`             | pound·foot/second   | kilogram·meter/second | gram·centimeter/second |
| `density`              | pound/cubic_foot    | kilogram/meter³       | gram/centimeter³       |
| `torque`               | foot_pound          | newton·meter          | dyne·centimeter        |
| `viscosity`            | pound/(foot·second) | pascal·second         | poise                  |
| `kinematic_viscosity`  | square_foot/second  | meter²/second         | stokes                 |

### Accessing Dimension Configuration

```python
from pint_glass import TARGET_DIMENSIONS

# List all supported dimensions
print(list(TARGET_DIMENSIONS.keys()))
# ['pressure', 'length', 'temperature', 'mass', 'time', ...]

# Get units for a specific dimension
print(TARGET_DIMENSIONS["pressure"])
# {'imperial': 'psi', 'si': 'pascal', 'cgs': 'barye', 'us': 'psi'}
```

---

## Unit Systems

### Supported Systems

| System     | Description                                    |
| ---------- | ---------------------------------------------- |
| `imperial` | British Imperial / US Customary (default)      |
| `si`       | International System of Units (metric)         |
| `cgs`      | Centimeter-Gram-Second system                  |
| `us`       | US Customary (same as imperial for most units) |

### Setting Unit System

```python
from pint_glass import set_unit_system, get_unit_system, reset_unit_system

# Set unit system (returns a token for reset)
token = set_unit_system("si")
print(get_unit_system())  # 'si'

# Reset to previous value
reset_unit_system(token)
print(get_unit_system())  # 'imperial' (default)
```

### Invalid System Handling

When an unsupported unit system is provided, PintGlass warns and falls back to `imperial`:

```python
import warnings
from pint_glass import set_unit_system

# This will emit a UserWarning
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    set_unit_system("metric")  # 'metric' is not supported

    print(w[-1].message)
    # "Unknown unit system 'metric' — falling back to 'imperial'.
    #  Supported systems: ['imperial', 'si']. Did you mean 'si'?"
```

---

## Advanced Usage

### Direct Conversion Functions

For cases where you need conversions outside Pydantic models:

```python
from pint_glass import convert_to_base, convert_from_base, get_preferred_unit, get_base_unit

# Convert 100 psi to pascals
pressure_pa = convert_to_base(100, "pressure", "imperial")
print(f"100 psi = {pressure_pa:.2f} Pa")  # ~689475.73 Pa

# Convert 101325 Pa to psi
pressure_psi = convert_from_base(101325, "pressure", "imperial")
print(f"101325 Pa = {pressure_psi:.2f} psi")  # ~14.70 psi

# Get unit strings
print(get_preferred_unit("length", "imperial"))  # 'foot'
print(get_base_unit("length"))                    # 'meter'
```

### Accessing the Pint UnitRegistry

```python
from pint_glass import ureg

# Create Pint quantities directly
length = ureg.Quantity(10, "foot")
print(length.to("meter"))  # 3.048 meter

# Perform calculations
area = length * ureg.Quantity(5, "foot")
print(area)  # 50 foot ** 2
```

### Request-Scoped Caching

PintGlass caches conversions per-request to avoid redundant Pint computations:

```python
from pint_glass import get_request_cache, clear_request_cache

# Access current cache
cache = get_request_cache()
print(f"Cache size: {len(cache)}")

# Clear cache (recommended at request start in middleware)
token = clear_request_cache()
# ... handle request ...
```

### Complete FastAPI Example with Caching

```python
from fastapi import FastAPI, Request
from pint_glass import set_unit_system, reset_unit_system, clear_request_cache

app = FastAPI()


@app.middleware("http")
async def unit_context_middleware(request: Request, call_next):
    """Full middleware with unit system and cache management."""
    system = request.headers.get("X-Unit-System", "imperial").lower()

    # Clear cache for fresh request
    cache_token = clear_request_cache()

    # Set unit system
    system_token = set_unit_system(system)

    try:
        response = await call_next(request)
        return response
    finally:
        reset_unit_system(system_token)
        # Cache automatically cleared on context exit
```

---

## Error Handling

### Exception Types

```python
from pint_glass import PintGlassError, UnsupportedDimensionError, UnitConversionError

# Base exception for all PintGlass errors
try:
    # Some operation
    pass
except PintGlassError as e:
    print(f"PintGlass error: {e}")


# Unsupported dimension
try:
    from pint_glass import get_preferred_unit
    get_preferred_unit("unknown_dimension", "imperial")
except UnsupportedDimensionError as e:
    print(f"Dimension error: {e}")
    # "Unsupported dimension 'unknown_dimension'; supported: 'pressure', 'length', ..."


# Unit conversion failure
try:
    from pint_glass import convert_to_base
    # This would fail with incompatible units
    convert_to_base(100, "pressure", "imperial")  # Normal case works
except UnitConversionError as e:
    print(f"Conversion error: {e}")
```

### Handling Validation Errors in Pydantic

```python
from pydantic import BaseModel, ValidationError
from pint_glass import PintGlass, set_unit_system

class Measurement(BaseModel):
    value: PintGlass("pressure")

set_unit_system("imperial")

# Invalid input type
try:
    m = Measurement(value="not a number")
except ValidationError as e:
    print(e)
    # 1 validation error for Measurement
    # value
    #   Cannot convert 'not a number' to a numeric value
```

---

## API Reference

### Primary API

| Function                           | Description                   |
| ---------------------------------- | ----------------------------- |
| `PintGlass(dimension, model_type)` | Create annotated field type   |
| `set_unit_system(system)`          | Set unit system context       |
| `get_unit_system()`                | Get current unit system       |
| `reset_unit_system(token)`         | Reset to previous unit system |

### Conversion Functions

| Function                                      | Description                |
| --------------------------------------------- | -------------------------- |
| `convert_to_base(value, dimension, system)`   | Convert to SI base units   |
| `convert_from_base(value, dimension, system)` | Convert from SI base units |
| `get_preferred_unit(dimension, system)`       | Get unit string for system |
| `get_base_unit(dimension)`                    | Get SI base unit string    |

### Cache Management

| Function                   | Description               |
| -------------------------- | ------------------------- |
| `get_request_cache()`      | Get current request cache |
| `set_request_cache(cache)` | Set request cache         |
| `clear_request_cache()`    | Clear/reset request cache |

### Constants

| Constant            | Description                                     |
| ------------------- | ----------------------------------------------- |
| `DEFAULT_SYSTEM`    | Default unit system (`"imperial"`)              |
| `SUPPORTED_SYSTEMS` | Set of supported systems (`{"imperial", "si"}`) |
| `TARGET_DIMENSIONS` | Dimension → unit mapping dict                   |
| `ureg`              | Shared Pint UnitRegistry instance               |

---

## Best Practices

### 1. Always Reset Context

```python
token = set_unit_system("si")
try:
    # Your code here
    pass
finally:
    reset_unit_system(token)  # Always in finally block
```

### 2. Use Middleware for Web Apps

Middleware ensures consistent context for the entire request lifecycle:

```python
@app.middleware("http")
async def unit_middleware(request: Request, call_next):
    token = set_unit_system(request.headers.get("X-Unit-System", "imperial"))
    try:
        return await call_next(request)
    finally:
        reset_unit_system(token)
```

### 3. Separate Input and Output Models

```python
# Clear intent and proper conversion direction
class ItemInput(BaseModel):
    value: PintGlass("length", "Input")

class ItemOutput(BaseModel):
    value: PintGlass("length", "Output")
```

### 4. Validate Unit System Header

```python
from pint_glass import SUPPORTED_SYSTEMS

def validate_unit_system(system: str) -> str:
    system = system.lower()
    if system not in SUPPORTED_SYSTEMS:
        raise ValueError(f"Unsupported unit system: {system}")
    return system
```

### 5. Work in SI Internally

All business logic should work with SI units. PintGlass handles conversion at the API boundary:

```python
@app.post("/calculate")
async def calculate(data: InputModel) -> OutputModel:
    # data.pressure is already in pascals
    # data.length is already in meters

    result = complex_calculation(data.pressure, data.length)  # SI units

    # Return OutputModel — converts back to user units automatically
    return OutputModel(result=result)
```

---

## Examples Repository

For complete working examples, see:

- [`fast_api_check.py`](./fast_api_check.py) - Full FastAPI integration example
- [`tests/`](./tests/) - Unit tests demonstrating various use cases

---

## Troubleshooting

### "No conversion found" Error

Ensure the dimension string matches exactly:

```python
# ❌ Wrong
PintGlass("Pressure", "Input")  # Case-sensitive!

# ✅ Correct
PintGlass("pressure", "Input")
```

### Values Not Converting

Check that unit system is set before model creation:

```python
# ❌ Unit system set after model creation
model = MyModel(value=100)
set_unit_system("si")  # Too late!

# ✅ Set unit system first
set_unit_system("si")
model = MyModel(value=100)
```

### Async Context Issues

Ensure you're using the token pattern correctly:

```python
# ❌ Context may not propagate correctly
set_unit_system("si")
await some_async_operation()

# ✅ Use token and reset
token = set_unit_system("si")
try:
    await some_async_operation()
finally:
    reset_unit_system(token)
```

---

## License

MIT License — see [LICENSE](./LICENSE) for details.
