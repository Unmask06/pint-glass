# PintGlass Module Specification

## 1. Overview

**PintGlass** is a specialized Python module designed to bridge the gap between physical unit handling (via **Pint**) and data validation (via **Pydantic**). It enables "Context-Aware" unit conversion, allowing API models to accept raw numbers that are automatically interpreted based on a global unit system setting (e.g., Imperial vs. SI) and converted to a standard **Base Unit (SI)** format for internal processing.

Crucially, it also handles **Response Serialization**, converting internal Base Units back to Preferred Units for the API response, ensuring a consistent user experience.

### Key Features

- **Seamless Integration**: Works directly with `pydantic.BaseModel`.
- **Context Awareness**: Uses `contextvars` to handle per-request unit systems (ideal for FastAPI/Async environments).
- **Bidirectional Conversion**:
  - **Requests**: Preferred Unit (Input) → Base Unit (Internal).
  - **Responses**: Base Unit (Internal) → Preferred Unit (Output).
- **Zero-Overhead Models**: The resulting Pydantic fields are pure `float` types at runtime, ensuring compatibility with JSON serialization and OpenAPI/Swagger documentation.
- **Auto-Discovery**: Dynamically builds unit maps by inspecting the Pint registry.

---

## 2. Architecture

The codebase is modularized to separate core registry logic from Pydantic integration.

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│  INPUT (Request)                                                        │
│  User sends value + dimension (e.g., 50, "pressure")                    │
│  Unit System determined by context (Imperial/SI)                        │
└──────────────────────────────┬──────────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  UNIT RESOLUTION                                                        │
│  Get unit from context + dimension → "psi" (Imperial) or "Pa" (SI)     │
└──────────────────────────────┬──────────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  VALIDATION (BeforeValidator)                                           │
│  Converts 50 psi → 344737.86 Pa (Base Unit)                             │
└──────────────────────────────┬──────────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  INTERNAL LOGIC                                                         │
│  Application works entirely with Base Units (Pa, m, K)                  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  OUTPUT (Response)                                                      │
│  PlainSerializer converts 344737.86 Pa → 50 psi (Preferred Unit System) │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Core Components

### 3.1. `unit_context`

A `contextvars.ContextVar[str]` that holds the current unit system identifier.

- **Default**: `"imperial"`

### 3.2. Registry & Configuration (`core.py`)

Manages the `pint.UnitRegistry` and the resolution of units. It distinguishes between:

| Term               | Description                                                           |
| ------------------ | --------------------------------------------------------------------- |
| **Base Unit**      | The internal storage unit (usually SI: `pascal`, `meter`)             |
| **Preferred Unit** | The unit expected by the user based on active context (`psi`, `foot`) |

### 3.3. PintGlass Factory (`fields.py`)

The primary interface for defining model fields.

```python
def PintGlass(value: float, dimension: str) -> Any
```

**Parameters:**

| Parameter   | Type    | Description                                                 |
| ----------- | ------- | ----------------------------------------------------------- |
| `value`     | `float` | The numeric value in the current context's unit system      |
| `dimension` | `str`   | The physical dimension key (e.g., `"pressure"`, `"length"`) |

**Returns:** An `Annotated` type alias containing:

- `BeforeValidator`: Converts Input → Base Unit.
- `PlainSerializer`: Converts Base Unit → Output.

---

## 4. Usage Example

### Defining a Model

The developer defines the model using `PintGlass`. Note that Request and Response models behave symmetrically.

```python
from pydantic import BaseModel
from pint_glass import PintGlass

class EquipmentSettings(BaseModel):
    # Internal storage is always SI (Pa, m)
    # External representation depends on unit_context
    max_pressure: PintGlass(value = 50, dimension = "pressure")
    tubing_length: PintGlass(value = 100, dimension = "length")
    max_temperature: PintGlass(value = 100, dimension = "temperature")
    tag:str
    count:float
```

### FastAPI Integration Pattern

Middleware can be used to set the context based on headers.

```python
from fastapi import Request
from pint_glass import unit_context

@app.middleware("http")
async def set_unit_context(request: Request, call_next):
    # Specific header to determine system
    system = request.headers.get("x-unit-system", "imperial")
    token = unit_context.set(system)
    try:
        response = await call_next(request)
    finally:
        unit_context.reset(token)
    return response
```

---

## 5. Supported Dimensions

By default, the module supports the following dimension keys (extensible via `TARGET_DIMENSIONS`):

| Dimension Key | Default Imperial Unit | Default SI Unit |
| ------------- | --------------------- | --------------- |
| `pressure`    | `psi`                 | `pascal`        |
| `length`      | `foot`                | `meter`         |
| `temperature` | `degF`                | `degC`          |
| `mass`        | `pound`               | `kilogram`      |
| `time`        | `second`              | `second`        |

---

## 6. Error Handling

| Error Type               | Description                                                                                                                  |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------- |
| **Invalid System**       | If the context is set to a non-existent system, it falls back to explicit mappings or `imperial`.                            |
| **Parsing Error**        | If the input value cannot be converted (e.g., string text in a float field), standard Pydantic validation errors are raised. |
| **Dimensionality Error** | Validates that the requested dimension exists in the Pint registry at startup.                                               |
