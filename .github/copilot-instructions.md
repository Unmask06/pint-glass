# Pint Glass 🍺

A Pydantic + Pint integration library for seamless unit conversion in Python APIs.

## Project Overview

**Pint Glass** bridges the gap between `pint` (unit handling) and `pydantic` (data validation), enabling automatic unit conversion in FastAPI and other Pydantic-based applications. Users can submit values in their preferred unit system (Imperial/SI), and the library handles conversion to base SI units internally.

## Tech Stack

| Category     | Technology              |
| ------------ | ----------------------- |
| Language     | Python 3.10+            |
| Units        | `pint`                  |
| Validation   | `pydantic` v2           |
| Context Mgmt | `contextvars`           |
| Package Mgmt | `uv` (not pip directly) |

## Development Guidelines

### Code Quality

- Be **Pythonic**, modular, and reusable
- Easy to maintain, update, extend, and modify
- Use **type hints** throughout the codebase
- Write comprehensive **docstrings** for public APIs


### Package Management

- Use **`uv`** as the package manager — do NOT use `pip` directly
- Develop package using **`pyproject.toml`**
- Pure Python package (no compiled extensions)

### Testing

- Write unit tests for all conversion functions
- Test with multiple unit systems (Imperial, SI, CGS)
- Validate edge cases (temperature offsets, derived units)
