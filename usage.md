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
- [Request-Scoped Caching](#request-scoped-caching)
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
┌──────────────────┐     PintGlass      ┌─────────────────┐     PintGlass       ┌──────────────────┐
│    User Input    │  ──────────────►   │   Internal SI   │  ───────────────►   │   API Response   │
│ (engg_si/field)  │  (validation)      │   (base units)  │  (serialization)    │ (engg_si/field)  │
└──────────────────┘                    └─────────────────┘                     └──────────────────┘
```

---

## Basic Usage

### Defining Models with PintGlass Fields

```python
from pydantic import BaseModel
from pint_glass import PintGlass, set_unit_system

# Define a model with unit-aware fields
class TankSpecification(BaseModel):
    pressure: PintGlass("pressure", "Input")       # bar ↔ pascals
    height: PintGlass("length", "Input")           # meters ↔ meters
    capacity: PintGlass("volume", "Input")         # cubic meters ↔ cubic meters
    max_temperature: PintGlass("temperature", "Input")  # °C ↔ Kelvin


# Set the unit system context (default is engg_si)
set_unit_system("engg_si")

# Create a model instance — values are in engineering SI units
tank = TankSpecification(
    pressure=10,         # 10 bar → stored as 1,000,000 Pa
    height=3,            # 3 m → stored as 3 m
    capacity=14,         # 14 m³ → stored as 14 m³
    max_temperature=100  # 100°C → stored as 373.15 K
)

# Access internal values (always SI)
print(f"Internal pressure: {tank.pressure} Pa")
print(f"Internal height: {tank.height} m")

# Serialize back to user-preferred units
print(tank.model_dump())
# Output: {'pressure': 10.0, 'height': 3.0, 'capacity': 14.0, 'max_temperature': 100.0}
```

### Input vs Output Models

PintGlass supports two model types for different use cases:

```python
from pydantic import BaseModel
from pint_glass import PintGlass

# Input Model: User sends preferred units → stored as SI
class PipeRequest(BaseModel):
    length: PintGlass("length", "Input")    # 10 m → 10 m
    pressure: PintGlass("pressure", "Input") # 10 bar → 1,000,000 Pa


# Output Model: SI values → serialized to preferred units
class PipeResponse(BaseModel):
    length: PintGlass("length", "Output")    # 10 m → 10 m
    pressure: PintGlass("pressure", "Output") # 1,000,000 Pa → 10 bar
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
    # Read unit system from X-Unit-System header (default: engg_si)
    system = request.headers.get("X-Unit-System", "engg_si").lower()

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
    # Flow rate is converted from m³/hr (engg_si) to m³/s (SI base)
    print(f"Flow rate (m³/s): {request.flow_rate}")
    print(f"Pressure (Pa): {request.head_pressure}")

    # Return response — automatically converted back to engg_si (m³/hr, bar)
    return PumpResponse(
        flow_rate=request.flow_rate,
        head_pressure=request.head_pressure,
        status="calculated"
    )
```

### Making Requests

```bash
# Engineering SI units (default)
curl -X POST "http://localhost:8000/pumps/calculate" \
  -H "Content-Type: application/json" \
  -H "X-Unit-System: engg_si" \
  -d '{"flow_rate": 360, "head_pressure": 1.0}'

# Response: {"flow_rate": 360.0, "head_pressure": 1.0, "status": "calculated"}
# (Note: flow_rate 360 m³/hr = 0.1 m³/s internally)


# Engineering Field units
curl -X POST "http://localhost:8000/pumps/calculate" \
  -H "Content-Type: application/json" \
  -H "X-Unit-System: engg_field" \
  -d '{"flow_rate": 100, "head_pressure": 50}'

# Response: {"flow_rate": 100.0, "head_pressure": 50.0, "status": "calculated"}
```

---

## Supported Dimensions

PintGlass supports multiple engineering and standard unit systems.

**Note on Temperature:** The SI base unit for temperature is **Kelvin (K)**. Engineering systems like `engg_si` and `engg_field` use °C and °F respectively, which are converted to/from Kelvin internally.

| Dimension              | Engg SI (default) | Engg Field          | Imperial Unit       | SI Unit (Base)        |
| ---------------------- | ----------------- | ------------------- | ------------------- | --------------------- |
| `pressure`             | bar               | psi                 | psi                 | pascal                |
| `length`               | meter             | foot                | foot                | meter                 |
| `temperature`          | degC              | degF                | degF                | **Kelvin**            |
| `mass_flow_rate`       | kg/hr             | lb/hr               | lb/s                | kg/s                  |
| `volumetric_flow_rate` | m³/hr             | ft³/hr              | ft³/s               | m³/s                  |
| `mass`                 | kilogram          | pound               | pound               | kilogram              |
| `time`                 | second            | second              | second              | second                |
| `area`                 | meter²            | foot²               | foot²               | meter²                |
| `volume`               | meter³            | foot³               | foot³               | meter³                |
| `velocity`             | meter/second      | foot/second         | foot/second         | meter/second          |
| `force`                | newton            | pound_force         | pound_force         | newton                |
| `energy`               | joule             | foot_pound          | foot_pound          | joule                 |
| `power`                | watt              | foot_pound/second   | foot_pound/second   | watt                  |
| `density`              | kg/m³             | lb/ft³              | lb/ft³              | kg/m³                 |
| `viscosity`            | pascal·second     | pound/(foot·second) | pound/(foot·second) | pascal·second         |

---

## Unit Systems

### Supported Systems

| System       | Description                                              |
| ------------ | -------------------------------------------------------- |
| `engg_si`    | Engineering SI: bar, m³/hr, kg/hr, degC (default)        |
| `engg_field` | Engineering Field: psi, ft³/hr, lb/hr, degF              |
| `imperial`   | British Imperial / US Customary (psi, ft³/s, lb/s, degF) |
| `si`         | International System of Units (metric base units)        |
| `cgs`        | Centimeter-Gram-Second system                            |
| `us`         | US Customary                                             |

### Setting Unit System

```python
from pint_glass import set_unit_system, get_unit_system, reset_unit_system

# Set unit system (returns a token for reset)
token = set_unit_system("engg_field")
print(get_unit_system())  # 'engg_field'

# Reset to previous value
reset_unit_system(token)
print(get_unit_system())  # 'engg_si' (default)
```

### Invalid System Handling

When an unsupported unit system is provided, PintGlass warns and falls back to `engg_si`:

```python
import warnings
from pint_glass import set_unit_system

# This will emit a UserWarning
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    set_unit_system("metric")  # 'metric' is not supported

    print(w[-1].message)
    # "Unknown unit system 'metric' — falling back to 'engg_si'.
    #  Supported systems: ['engg_si', 'engg_field', 'imperial', 'si', ...]"
```

---

## Advanced Usage

### Direct Conversion Functions

```python
from pint_glass import convert_to_base, convert_from_base, get_preferred_unit, get_base_unit

# Convert 10 bar to pascals
pressure_pa = convert_to_base(10, "pressure", "engg_si")
print(f"10 bar = {pressure_pa:.2f} Pa")  # 1,000,000.00 Pa

# Convert 3600 m³/hr to m³/s
flow_m3s = convert_to_base(3600, "volumetric_flow_rate", "engg_si")
print(f"3600 m3/hr = {flow_m3s:.2f} m3/s")  # 1.00 m3/s
```

---

## Request-Scoped Caching

PintGlass uses `contextvars` to cache `pint.Quantity` conversions *per request*. This significantly improves performance when converting the same dimension multiple times within a single request context.

### Managing the Cache

Typically, you don't need to manage this manually if you use `set_unit_system()` / `reset_unit_system()`. However, you can inspect or clear it explicitly:

```python
from pint_glass import get_request_cache, clear_request_cache

# Get current cache contents
cache = get_request_cache()
print(len(cache))

# Clear cache manually (e.g., if re-using a context for very long periods)
clear_request_cache()
```

---

## Error Handling

PintGlass uses specific exceptions for conversion failures.

| Exception Class             | Description                                                                 |
| --------------------------- | --------------------------------------------------------------------------- |
| `UnsupportedDimensionError` | Raised when a requested dimension key (e.g., "magic_power") is unknown.     |
| `UnitConversionError`       | Raised when Pint fails to convert units (e.g., incompatible dimensionality).|

### Handling Validation Errors in Pydantic

When using `PintGlass` fields, invalid inputs raise standard Pydantic `ValidationError`s wrapping the underlying PintGlass exception.

```python
try:
    TankSpecification(pressure="invalid_string")
except ValidationError as e:
    print(e)
    # 1 validation error for TankSpecification
    # pressure
    #   Cannot convert 'invalid_string' to a numeric value ...
```

---

## API Reference

### `PintGlass`

```python
def PintGlass(dimension: str, model_type: Literal["Input", "Output"]) -> Any
```
Factory function to create an Annotated type for Pydantic fields.
- **dimension**: Key from `TARGET_DIMENSIONS` (e.g., "pressure").
- **model_type**:
    - `"Input"`: Converts user units → SI base units.
    - `"Output"`: Expects SI base units, serializes to user units.

### Context Management

#### `set_unit_system(system: str) -> Token`
Sets the current unit system context. Returns a token to be used with `reset_unit_system`.

#### `reset_unit_system(token: Token) -> None`
Resets the unit system context to the state before `set_unit_system` was called.

#### `get_unit_system() -> str`
Returns the identifier of the current unit system (e.g., "engg_si"). Defaults to `DEFAULT_SYSTEM` if not set.

### Conversion Utilities

#### `convert_to_base(value: float, dimension: str, system: str) -> float`
Converts a value from the specified system's unit to the SI base unit.

#### `convert_from_base(value: float, dimension: str, system: str) -> float`
Converts a value from the SI base unit to the specified system's unit.

#### `get_preferred_unit(dimension: str, system: str) -> str`
Returns the unit string (e.g., "psi") used for the given dimension in the specified system.

---

## Best Practices

### 1. Always Reset Context
When using `set_unit_system`, always ensure `reset_unit_system` is called, preferably in a `finally` block or context manager logic.

```python
token = set_unit_system("engg_field")
try:
    # Your code here
    pass
finally:
    reset_unit_system(token)  # Always in finally block
```

### 2. Use Middleware for Web Apps
Do not set global state. Use middleware or dependency injection to set the unit system *per request* based on headers or user profile.

### 3. Store SI, Display User Units
Always store physical quantities in SI base units (Kelvin, Pascal, Meter) in your database and business logic. Only convert to/from user units at the API boundary (Input/Output models). This avoids confusion and conversion errors in your core logic.

### 4. Use "Input" vs "Output" Correctly
- Use `PintGlass(..., "Input")` for models receiving data (POST/PUT bodies).
- Use `PintGlass(..., "Output")` for models returning data (Response models).
- Do not use `PintGlass` fields for internal data structures unless you specifically need auto-conversion there.

---

## License

MIT License — see [LICENSE](./LICENSE) for details.