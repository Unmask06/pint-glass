"""PintGlass Demo Backend.

FastAPI server demonstrating real-world usage of PintGlass with
Pump and Line engineering models.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pint_glass import (
    TARGET_DIMENSIONS,
    PintGlass,
    reset_unit_system,
    set_unit_system,
)

# =============================================================================
# Models - Real-world engineering examples
# =============================================================================


class PumpInput(BaseModel):
    """Pump specification input from user (preferred units)."""

    flow_rate: PintGlass("volumetric_flow_rate", "Input")
    head_pressure: PintGlass("pressure", "Input")
    power: PintGlass("power", "Input")
    inlet_temperature: PintGlass("temperature", "Input")
    pipe_diameter: PintGlass("length", "Input")


class PumpOutput(BaseModel):
    """Pump specification output (converted back to preferred units)."""

    flow_rate: PintGlass("volumetric_flow_rate", "Output")
    head_pressure: PintGlass("pressure", "Output")
    power: PintGlass("power", "Output")
    inlet_temperature: PintGlass("temperature", "Output")
    pipe_diameter: PintGlass("length", "Output")


class LineInput(BaseModel):
    """Pipeline specification input from user (preferred units)."""

    length: PintGlass("length", "Input")
    velocity: PintGlass("velocity", "Input")
    pressure_drop: PintGlass("pressure", "Input")
    fluid_density: PintGlass("density", "Input")
    viscosity: PintGlass("viscosity", "Input")


class LineOutput(BaseModel):
    """Pipeline specification output (converted back to preferred units)."""

    length: PintGlass("length", "Output")
    velocity: PintGlass("velocity", "Output")
    pressure_drop: PintGlass("pressure", "Output")
    fluid_density: PintGlass("density", "Output")
    viscosity: PintGlass("viscosity", "Output")


# =============================================================================
# Application Setup
# =============================================================================

app = FastAPI(title="PintGlass Demo API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store for console logs (per-request)
console_logs: list[str] = []


def log(message: str) -> None:
    """Log message to console buffer and stdout."""
    console_logs.append(message)
    print(message)


@app.middleware("http")
async def unit_system_middleware(request: Request, call_next):
    """Set unit system context from X-Unit-System header."""
    global console_logs
    console_logs = []  # Clear logs for new request

    system = request.headers.get("X-Unit-System", "imperial").lower()
    log(f"[Middleware] Received X-Unit-System header: '{system}'")

    token = set_unit_system(system)
    log(f"[Middleware] Unit system context set to: '{system}'")

    try:
        response = await call_next(request)
        return response
    finally:
        reset_unit_system(token)
        log("[Middleware] Unit system context reset")


# =============================================================================
# API Endpoints
# =============================================================================


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/dimensions")
async def get_dimensions():
    """Return all supported dimensions with their unit mappings."""
    return {
        "dimensions": list(TARGET_DIMENSIONS.keys()),
        "mappings": TARGET_DIMENSIONS,
    }


@app.post("/pump")
async def process_pump(pump: PumpInput):
    """Process pump data - demonstrates round-trip conversion."""
    log("\n[Endpoint: /pump] Received PumpInput")
    log("  Raw input values (already converted to SI internally):")
    log(f"    flow_rate: {pump.flow_rate} m³/s")
    log(f"    head_pressure: {pump.head_pressure} Pa")
    log(f"    power: {pump.power} W")
    log(f"    inlet_temperature: {pump.inlet_temperature} °C")
    log(f"    pipe_diameter: {pump.pipe_diameter} m")

    # Business logic would go here (always works in SI)
    log("\n[Processing] Business logic executes with SI values...")

    # Create output - will be serialized back to preferred units
    output = PumpOutput(
        flow_rate=pump.flow_rate,
        head_pressure=pump.head_pressure,
        power=pump.power,
        inlet_temperature=pump.inlet_temperature,
        pipe_diameter=pump.pipe_diameter,
    )

    log("\n[Response] PumpOutput created (will serialize to preferred units)")

    return {
        "data": output,
        "console": console_logs.copy(),
    }


@app.post("/line")
async def process_line(line: LineInput):
    """Process line/pipeline data - demonstrates round-trip conversion."""
    log("\n[Endpoint: /line] Received LineInput")
    log("  Raw input values (already converted to SI internally):")
    log(f"    length: {line.length} m")
    log(f"    velocity: {line.velocity} m/s")
    log(f"    pressure_drop: {line.pressure_drop} Pa")
    log(f"    fluid_density: {line.fluid_density} kg/m³")
    log(f"    viscosity: {line.viscosity} Pa·s")

    # Business logic would go here (always works in SI)
    log("\n[Processing] Business logic executes with SI values...")

    # Create output
    output = LineOutput(
        length=line.length,
        velocity=line.velocity,
        pressure_drop=line.pressure_drop,
        fluid_density=line.fluid_density,
        viscosity=line.viscosity,
    )

    log("\n[Response] LineOutput created (will serialize to preferred units)")

    return {
        "data": output,
        "console": console_logs.copy(),
    }


# =============================================================================
# Run Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    print("Starting PintGlass Demo API on http://localhost:8001")
    print("Open index.html in browser to test the frontend")
    uvicorn.run(app, host="0.0.0.0", port=8001)
