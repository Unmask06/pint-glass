"""Tests for async concurrency and context isolation.

These tests verify that:
1. Multiple simultaneous async requests with different unit systems don't leak
2. Request-scoped cache is properly isolated between requests
3. Unknown unit systems emit warnings and fallback correctly
"""

import asyncio
import warnings

import pytest
from pydantic import BaseModel

from pint_glass import (
    DEFAULT_SYSTEM,
    SUPPORTED_SYSTEMS,
    PintGlass,
    clear_request_cache,
    get_request_cache,
    get_unit_system,
    reset_unit_system,
    set_unit_system,
)


class TestSupportedSystems:
    """Tests for SUPPORTED_SYSTEMS constant."""

    def test_supported_systems_contains_imperial(self) -> None:
        """Imperial should be a supported system."""
        assert "imperial" in SUPPORTED_SYSTEMS

    def test_supported_systems_contains_si(self) -> None:
        """SI should be a supported system."""
        assert "si" in SUPPORTED_SYSTEMS

    def test_supported_systems_is_frozenset(self) -> None:
        """SUPPORTED_SYSTEMS should be immutable."""
        assert isinstance(SUPPORTED_SYSTEMS, frozenset)


class TestUnknownSystemWarning:
    """Tests for warning on unknown unit systems."""

    def test_unknown_system_emits_warning(self) -> None:
        """Unknown system should emit UserWarning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            token = set_unit_system("metric")  # Unknown system
            try:
                assert len(w) == 1
                assert issubclass(w[0].category, UserWarning)
                assert "Unknown unit system 'metric'" in str(w[0].message)
                assert "Did you mean 'si'?" in str(w[0].message)
            finally:
                reset_unit_system(token)

    def test_unknown_system_falls_back_to_default(self) -> None:
        """Unknown system should fallback to DEFAULT_SYSTEM."""
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            token = set_unit_system("bogus")
            try:
                assert get_unit_system() == DEFAULT_SYSTEM
            finally:
                reset_unit_system(token)

    def test_valid_system_no_warning(self) -> None:
        """Valid systems should not emit warnings."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            token = set_unit_system("si")
            try:
                assert len(w) == 0
            finally:
                reset_unit_system(token)

    def test_case_insensitive_system(self) -> None:
        """System names should be case-insensitive."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            token = set_unit_system("SI")
            try:
                assert len(w) == 0
                assert get_unit_system() == "si"
            finally:
                reset_unit_system(token)


class TestRequestScopedCache:
    """Tests for request-scoped conversion cache."""

    def test_cache_starts_empty(self) -> None:
        """Cache should start empty in new context."""
        cache_token = clear_request_cache()
        try:
            cache = get_request_cache()
            assert len(cache) == 0
        finally:
            # Reset not strictly needed but good practice
            pass

    def test_cache_stores_conversions(self) -> None:
        """Conversions should be cached."""
        cache_token = clear_request_cache()
        try:
            token = set_unit_system("imperial")
            try:

                class TestModel(BaseModel):
                    length: PintGlass("length", "Input")

                # First conversion - cache miss
                model = TestModel(length=10)
                cache = get_request_cache()
                # Cache should have entries now
                assert len(cache) > 0
            finally:
                reset_unit_system(token)
        finally:
            pass

    def test_clear_cache_isolates_requests(self) -> None:
        """Clearing cache should provide isolation."""
        # Simulate first request
        cache_token1 = clear_request_cache()
        token1 = set_unit_system("imperial")
        try:

            class Model1(BaseModel):
                pressure: PintGlass("pressure", "Input")

            _ = Model1(pressure=100)
            cache1_size = len(get_request_cache())
            assert cache1_size > 0
        finally:
            reset_unit_system(token1)

        # Simulate second request with fresh cache
        cache_token2 = clear_request_cache()
        cache2 = get_request_cache()
        assert len(cache2) == 0  # Fresh cache


class TestAsyncConcurrency:
    """Tests for async concurrency and isolation."""

    @pytest.mark.asyncio
    async def test_concurrent_requests_different_systems(self) -> None:
        """Multiple concurrent async requests with different systems don't leak."""
        results: dict[str, str] = {}

        async def request_imperial(request_id: str) -> None:
            """Simulate imperial request."""
            token = set_unit_system("imperial")
            cache_token = clear_request_cache()
            try:
                await asyncio.sleep(0.01)  # Simulate some async work
                results[request_id] = get_unit_system()
            finally:
                reset_unit_system(token)

        async def request_si(request_id: str) -> None:
            """Simulate SI request."""
            token = set_unit_system("si")
            cache_token = clear_request_cache()
            try:
                await asyncio.sleep(0.01)  # Simulate some async work
                results[request_id] = get_unit_system()
            finally:
                reset_unit_system(token)

        # Run many concurrent requests
        tasks = []
        for i in range(50):
            if i % 2 == 0:
                tasks.append(request_imperial(f"imperial_{i}"))
            else:
                tasks.append(request_si(f"si_{i}"))

        await asyncio.gather(*tasks)

        # Verify no leakage
        for request_id, system in results.items():
            if request_id.startswith("imperial"):
                assert system == "imperial", (
                    f"Request {request_id} leaked: got {system}"
                )
            else:
                assert system == "si", f"Request {request_id} leaked: got {system}"

    @pytest.mark.asyncio
    async def test_concurrent_model_validation(self) -> None:
        """Concurrent model validation with different systems."""

        class PipeData(BaseModel):
            length: PintGlass("length", "Input")

        async def validate_imperial(value: float) -> float:
            """Validate with imperial."""
            token = set_unit_system("imperial")
            cache_token = clear_request_cache()
            try:
                await asyncio.sleep(0.005)
                model = PipeData(length=value)
                return model.length
            finally:
                reset_unit_system(token)

        async def validate_si(value: float) -> float:
            """Validate with SI."""
            token = set_unit_system("si")
            cache_token = clear_request_cache()
            try:
                await asyncio.sleep(0.005)
                model = PipeData(length=value)
                return model.length
            finally:
                reset_unit_system(token)

        # 10 feet in imperial = 3.048 meters
        # 10 meters in SI = 10 meters
        imperial_tasks = [validate_imperial(10) for _ in range(20)]
        si_tasks = [validate_si(10) for _ in range(20)]

        all_results = await asyncio.gather(*imperial_tasks, *si_tasks)

        imperial_results = all_results[:20]
        si_results = all_results[20:]

        # Imperial: 10 ft -> ~3.048 m
        for result in imperial_results:
            assert abs(result - 3.048) < 0.001, f"Imperial conversion failed: {result}"

        # SI: 10 m -> 10 m
        for result in si_results:
            assert result == 10.0, f"SI conversion failed: {result}"

    @pytest.mark.asyncio
    async def test_nested_async_context(self) -> None:
        """Nested async calls maintain correct context."""
        results: list[str] = []

        async def outer() -> None:
            token = set_unit_system("imperial")
            try:
                results.append(get_unit_system())
                await inner()
                results.append(get_unit_system())  # Should still be imperial
            finally:
                reset_unit_system(token)

        async def inner() -> None:
            # Inner task uses different system
            token = set_unit_system("si")
            try:
                await asyncio.sleep(0.001)
                results.append(get_unit_system())
            finally:
                reset_unit_system(token)

        await outer()

        assert results == ["imperial", "si", "imperial"]

    @pytest.mark.asyncio
    async def test_cache_isolation_between_tasks(self) -> None:
        """Each async task should have isolated cache."""
        cache_sizes: dict[str, int] = {}

        async def task_with_conversions(task_id: str) -> None:
            cache_token = clear_request_cache()
            token = set_unit_system("imperial" if task_id.startswith("a") else "si")
            try:

                class Model(BaseModel):
                    pressure: PintGlass("pressure", "Input")
                    length: PintGlass("length", "Input")

                _ = Model(pressure=100, length=50)
                await asyncio.sleep(0.005)
                cache_sizes[task_id] = len(get_request_cache())
            finally:
                reset_unit_system(token)

        tasks = [task_with_conversions(f"a_{i}") for i in range(10)]
        tasks += [task_with_conversions(f"b_{i}") for i in range(10)]

        await asyncio.gather(*tasks)

        # All tasks should have non-zero cache (conversions happened)
        for task_id, size in cache_sizes.items():
            assert size > 0, f"Task {task_id} had empty cache"
