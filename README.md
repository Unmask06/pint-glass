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
    max_pressure: PintGlass("pressure", "Input")
    tubing_length: PintGlass("length", "Input")
    max_temperature: PintGlass("temperature", "Input")
    flow_rate: PintGlass("volumetric_flow_rate", "Input")

# Set unit system (default is "engg_si")
set_unit_system("engg_si")

# Create model - values are interpreted as Engineering SI units
settings = EquipmentSettings(
    max_pressure=1.0,     # 1.0 bar → stored as pascals
    tubing_length=100,    # 100 m → stored as meters
    max_temperature=100,  # 100°C → stored as °C
    flow_rate=10,         # 10 m³/hr → stored as m³/s
)

# Internal values are always in SI base units
print(f"Pressure in Pa: {settings.max_pressure}")

# Serialization converts back to preferred units
print(settings.model_dump())  # Returns values in engg_si units
```

## FastAPI Integration

```python
from fastapi import FastAPI, Request
from pint_glass import unit_context

app = FastAPI()

@app.middleware("http")
async def set_unit_context(request: Request, call_next):
    system = request.headers.get("x-unit-system", "engg_si")
    token = unit_context.set(system)
    try:
        response = await call_next(request)
    finally:
        unit_context.reset(token)
    return response
```

## Supported Dimensions

PintGlass supports multiple unit systems including **Engineering SI** (`engg_si`), **Engineering Field** (`engg_field`), **Imperial** (`imperial`), **SI** (`si`), **CGS** (`cgs`), and **US Customary** (`us`).

| Dimension            | Engg SI (default) | Engg Field | Imperial | SI Unit |
| -------------------- | ----------------- | ---------- | -------- | ------- |
| pressure             | bar               | psi        | psi      | pascal  |
| length               | meter             | foot       | foot     | meter   |
| temperature          | degC              | degF       | degF     | degC    |
| mass_flow_rate       | kg/hr             | lb/hr      | lb/s     | kg/s    |
| volumetric_flow_rate | m³/hr             | ft³/hr     | ft³/s    | m³/s    |

## License

MIT
