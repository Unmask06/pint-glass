# PintGlass 🍺

A Pydantic + Pint integration library for seamless unit conversion in Python APIs.

## Installation

```bash
uv add pint-glass
```

## Quick Start

```python
from pydantic import BaseModel
from pint_glass import PintGlass, unit_context, set_unit_system

class EquipmentSettings(BaseModel):
    max_pressure: PintGlass("pressure")
    tubing_length: PintGlass("length")
    max_temperature: PintGlass("temperature")

# Set unit system (default is "imperial")
set_unit_system("imperial")

# Create model - values are interpreted as imperial units
settings = EquipmentSettings(
    max_pressure=50,      # 50 psi → stored as pascals
    tubing_length=100,    # 100 ft → stored as meters
    max_temperature=212   # 212°F → stored as °C
)

# Internal values are always in SI base units
print(f"Pressure in Pa: {settings.max_pressure}")

# Serialization converts back to preferred units
print(settings.model_dump())  # Returns values in imperial units
```

## FastAPI Integration

```python
from fastapi import FastAPI, Request
from pint_glass import unit_context

app = FastAPI()

@app.middleware("http")
async def set_unit_context(request: Request, call_next):
    system = request.headers.get("x-unit-system", "imperial")
    token = unit_context.set(system)
    try:
        response = await call_next(request)
    finally:
        unit_context.reset(token)
    return response
```

## Supported Dimensions

| Dimension   | Imperial Unit | SI Unit  |
| ----------- | ------------- | -------- |
| pressure    | psi           | pascal   |
| length      | foot          | meter    |
| temperature | degF          | degC     |
| mass        | pound         | kilogram |
| time        | second        | second   |

## License

MIT
