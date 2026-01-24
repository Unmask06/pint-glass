from typing import Annotated

from fastapi import FastAPI, Header, Request
from pydantic import BaseModel

from pint_glass import PintGlass, reset_unit_system, set_unit_system

# --- Models ---


class PipeRequest(BaseModel):
    """Input model: User provides length in their preferred unit (e.g., feet).
    It is stored internally as SI (meters).
    """

    length: PintGlass("length", "Input")
    pressure: PintGlass("pressure", "Input")
    temperature: PintGlass("temperature", "Input")
    name: str


class PipeResponse(BaseModel):
    """Output model: Internal SI value (meters) is converted back to
    the user's preferred unit for the response.
    """

    length: PintGlass("length", "Output")
    pressure: PintGlass("pressure", "Output")
    temperature: PintGlass("temperature", "Output")
    name: str


# --- Middleware / Dependency ---


async def get_unit_system_header(x_unit_system: Annotated[str | None, Header()] = None):
    """Dependency to capture the unit system from the header.
    In a real app, this might be a middleware, but for simple dependency injection
    this works well to ensure context is set for the request scope.
    """
    # Default to imperial if not specified
    system = x_unit_system.lower() if x_unit_system else "imperial"

    # Valid systems check could go here, but PintGlass handles fallbacks or errors
    token = set_unit_system(system)
    try:
        yield system
    finally:
        reset_unit_system(token)


# --- App ---

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def unit_system_middleware(request: Request, call_next):
    """Middleware to ensure the unit system is set for the entire request lifecycle.
    This is often safer than valid dependency injection for global state
    that needs to be accessed deep in the call stack.
    """
    system = request.headers.get("X-Unit-System", "imperial").lower()
    token = set_unit_system(system)
    try:
        response = await call_next(request)
        return response
    finally:
        reset_unit_system(token)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/items", response_model=PipeResponse)
async def create_item(item: PipeRequest):
    """Receives an item with dimensions.
    The input 'item.length' will already be in SI units (meters) thanks to PintGlass.
    We return it, and it will be converted back to the preferred unit (feet/meters) thanks to PintGlass.
    """
    print(f"Received item: {item}")
    print(f"Internal structure (SI units): {item.length} meters")
    print(f"Internal pressure (SI units): {item.pressure} pascals")
    print(f"Internal temperature (SI units): {item.temperature} degC")

    # Logic residing in domain layer (works in SI)
    # ...

    # Return same item (demonstrates round trip)
    return PipeResponse(
        length=item.length,
        pressure=item.pressure,
        temperature=item.temperature,
        name=item.name,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
