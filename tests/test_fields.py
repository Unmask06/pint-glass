"""Tests for pint_glass.fields module and PintGlass factory."""

import pytest
from pydantic import BaseModel, ValidationError

from pint_glass import PintGlass, set_unit_system, unit_context


class TestPintGlassBasic:
    """Basic tests for PintGlass type factory."""

    def test_creates_annotated_type(self) -> None:
        """PintGlass should create a valid type for Pydantic."""
        pressure_type = PintGlass("pressure")
        assert pressure_type is not None

    def test_can_be_used_in_model(self) -> None:
        """PintGlass types should work in Pydantic models."""

        class TestModel(BaseModel):
            value: PintGlass("pressure")

        model = TestModel(value=100)
        assert model.value is not None

    def test_default_model_type_is_input(self) -> None:
        """Default model_type should be 'Input'."""
        token = set_unit_system("imperial")
        try:

            class TestModel(BaseModel):
                pressure: PintGlass("pressure")  # Default is Input

            # 14.696 psi → ~101325 Pa (converted to SI)
            model = TestModel(pressure=14.696)
            assert abs(model.pressure - 101325) < 100
        finally:
            unit_context.reset(token)


class TestPintGlassInputModel:
    """Tests for PintGlass with model_type='Input'."""

    def test_imperial_pressure_converted_to_si(self) -> None:
        """Imperial psi should be converted to pascals on Input."""
        token = set_unit_system("imperial")
        try:

            class TestModel(BaseModel):
                pressure: PintGlass("pressure", "Input")

            model = TestModel(pressure=14.696)
            assert abs(model.pressure - 101325) < 100
        finally:
            unit_context.reset(token)

    def test_si_pressure_unchanged_on_input(self) -> None:
        """SI pascals should remain as pascals on Input."""
        token = set_unit_system("si")
        try:

            class TestModel(BaseModel):
                pressure: PintGlass("pressure", "Input")

            model = TestModel(pressure=101325)
            assert model.pressure == 101325.0
        finally:
            unit_context.reset(token)

    def test_imperial_length_converted(self) -> None:
        """Imperial feet should be converted to meters on Input."""
        token = set_unit_system("imperial")
        try:

            class TestModel(BaseModel):
                length: PintGlass("length", "Input")

            model = TestModel(length=1)
            assert abs(model.length - 0.3048) < 0.0001
        finally:
            unit_context.reset(token)

    def test_temperature_offset_handled_on_input(self) -> None:
        """Temperature conversion should handle offset correctly on Input."""
        token = set_unit_system("imperial")
        try:

            class TestModel(BaseModel):
                temp: PintGlass("temperature", "Input")

            # 32°F = 0°C
            model = TestModel(temp=32)
            assert abs(model.temp - 0) < 0.1

            # 212°F = 100°C
            model2 = TestModel(temp=212)
            assert abs(model2.temp - 100) < 0.1
        finally:
            unit_context.reset(token)

    def test_serializes_back_to_preferred_on_input(self) -> None:
        """Input model should serialize back to preferred units."""
        token = set_unit_system("imperial")
        try:

            class TestModel(BaseModel):
                pressure: PintGlass("pressure", "Input")

            # 14.696 psi stored as ~101325 Pa
            model = TestModel(pressure=14.696)
            dumped = model.model_dump()
            # Should serialize back to ~14.696 psi
            assert abs(dumped["pressure"] - 14.696) < 0.01
        finally:
            unit_context.reset(token)


class TestPintGlassOutputModel:
    """Tests for PintGlass with model_type='Output'."""

    def test_output_accepts_si_directly(self) -> None:
        """Output model should accept SI values directly without conversion."""
        token = set_unit_system("imperial")
        try:

            class ResponseModel(BaseModel):
                pressure: PintGlass("pressure", "Output")

            # Pass SI value directly - should NOT be converted on input
            model = ResponseModel(pressure=101325)
            assert model.pressure == 101325.0
        finally:
            unit_context.reset(token)

    def test_output_serializes_to_preferred(self) -> None:
        """Output model should serialize to preferred units."""
        token = set_unit_system("imperial")
        try:

            class ResponseModel(BaseModel):
                pressure: PintGlass("pressure", "Output")

            # Store 101325 Pa (SI), serialize to ~14.696 psi
            model = ResponseModel(pressure=101325)
            dumped = model.model_dump()
            assert abs(dumped["pressure"] - 14.696) < 0.01
        finally:
            unit_context.reset(token)

    def test_output_length_serialization(self) -> None:
        """Output model length should serialize from meters to feet."""
        token = set_unit_system("imperial")
        try:

            class ResponseModel(BaseModel):
                length: PintGlass("length", "Output")

            # Store 1 meter, serialize to ~3.28 feet
            model = ResponseModel(length=1.0)
            dumped = model.model_dump()
            assert abs(dumped["length"] - 3.28084) < 0.001
        finally:
            unit_context.reset(token)

    def test_output_temperature_serialization(self) -> None:
        """Output model temperature should serialize from °C to °F."""
        token = set_unit_system("imperial")
        try:

            class ResponseModel(BaseModel):
                temp: PintGlass("temperature", "Output")

            # Store 100°C, serialize to 212°F
            model = ResponseModel(temp=100)
            dumped = model.model_dump()
            assert abs(dumped["temp"] - 212) < 0.1
        finally:
            unit_context.reset(token)

    def test_output_si_context_no_conversion(self) -> None:
        """Output model in SI context should not convert."""
        token = set_unit_system("si")
        try:

            class ResponseModel(BaseModel):
                pressure: PintGlass("pressure", "Output")

            model = ResponseModel(pressure=101325)
            dumped = model.model_dump()
            assert dumped["pressure"] == 101325.0
        finally:
            unit_context.reset(token)


class TestInputOutputWorkflow:
    """Tests simulating real Input → Internal → Output workflow."""

    def test_request_response_workflow(self) -> None:
        """Simulate receiving request, processing, and sending response."""
        token = set_unit_system("imperial")
        try:
            # Request model receives user input
            class PipeRequest(BaseModel):
                pressure: PintGlass("pressure", "Input")
                length: PintGlass("length", "Input")

            # Response model outputs results
            class PipeResponse(BaseModel):
                pressure: PintGlass("pressure", "Output")
                length: PintGlass("length", "Output")
                calculated_value: float

            # User sends 100 psi, 10 feet
            request = PipeRequest(pressure=100, length=10)

            # Internal processing uses SI values
            internal_pressure = request.pressure  # pascals
            internal_length = request.length  # meters

            # Verify internal values are SI
            assert internal_pressure > 100  # pascals > psi
            assert abs(internal_length - 3.048) < 0.001  # ~3 meters

            # Create response with SI values
            response = PipeResponse(
                pressure=internal_pressure,
                length=internal_length,
                calculated_value=42.0,
            )

            # Response serializes back to imperial
            dumped = response.model_dump()
            assert abs(dumped["pressure"] - 100) < 0.1
            assert abs(dumped["length"] - 10) < 0.1
            assert dumped["calculated_value"] == 42.0
        finally:
            unit_context.reset(token)

    def test_cross_system_workflow(self) -> None:
        """Test receiving in one system, responding in another."""
        # Receive request in imperial
        token1 = set_unit_system("imperial")
        try:

            class Request(BaseModel):
                pressure: PintGlass("pressure", "Input")

            request = Request(pressure=14.696)  # 1 atm in psi
        finally:
            unit_context.reset(token1)

        # Process internally (value is in SI)
        si_pressure = request.pressure
        assert abs(si_pressure - 101325) < 100

        # Respond in SI context
        token2 = set_unit_system("si")
        try:

            class Response(BaseModel):
                pressure: PintGlass("pressure", "Output")

            response = Response(pressure=si_pressure)
            dumped = response.model_dump()
            # In SI context, should output pascals
            assert abs(dumped["pressure"] - 101325) < 100
        finally:
            unit_context.reset(token2)


class TestMixedFieldTypes:
    """Tests for models with PintGlass and regular Python types."""

    def test_mixed_with_str(self) -> None:
        """PintGlass should work alongside str fields."""
        token = set_unit_system("imperial")
        try:

            class Equipment(BaseModel):
                name: str
                pressure: PintGlass("pressure", "Input")
                description: str

            model = Equipment(
                name="Pump A",
                pressure=100,
                description="Main pump",
            )
            assert model.name == "Pump A"
            assert model.pressure > 100  # Converted
            assert model.description == "Main pump"
        finally:
            unit_context.reset(token)

    def test_mixed_with_int(self) -> None:
        """PintGlass should work alongside int fields."""
        token = set_unit_system("imperial")
        try:

            class Counter(BaseModel):
                count: int
                pressure: PintGlass("pressure", "Input")
                priority: int

            model = Counter(count=5, pressure=100, priority=1)
            assert model.count == 5
            assert model.pressure > 100
            assert model.priority == 1
        finally:
            unit_context.reset(token)

    def test_mixed_with_float(self) -> None:
        """PintGlass should work alongside float fields."""
        token = set_unit_system("imperial")
        try:

            class Measurement(BaseModel):
                raw_value: float
                pressure: PintGlass("pressure", "Input")
                calibration: float

            model = Measurement(
                raw_value=1.5,
                pressure=100,
                calibration=0.99,
            )
            assert model.raw_value == 1.5
            assert model.pressure > 100
            assert model.calibration == 0.99
        finally:
            unit_context.reset(token)

    def test_mixed_with_bool(self) -> None:
        """PintGlass should work alongside bool fields."""
        token = set_unit_system("imperial")
        try:

            class SensorReading(BaseModel):
                is_active: bool
                pressure: PintGlass("pressure", "Input")
                is_calibrated: bool

            model = SensorReading(
                is_active=True,
                pressure=100,
                is_calibrated=False,
            )
            assert model.is_active is True
            assert model.pressure > 100
            assert model.is_calibrated is False
        finally:
            unit_context.reset(token)

    def test_mixed_with_optional(self) -> None:
        """PintGlass should work alongside Optional fields."""
        token = set_unit_system("imperial")
        try:

            class OptionalFields(BaseModel):
                pressure: PintGlass("pressure", "Input")
                notes: str | None = None
                max_value: float | None = None

            model = OptionalFields(pressure=100)
            assert model.pressure > 100
            assert model.notes is None
            assert model.max_value is None

            model2 = OptionalFields(
                pressure=100,
                notes="Test note",
                max_value=150.0,
            )
            assert model2.notes == "Test note"
            assert model2.max_value == 150.0
        finally:
            unit_context.reset(token)

    def test_mixed_with_list(self) -> None:
        """PintGlass should work alongside list fields."""
        token = set_unit_system("imperial")
        try:

            class MultiSensor(BaseModel):
                pressure: PintGlass("pressure", "Input")
                tags: list[str]
                readings: list[float]

            model = MultiSensor(
                pressure=100,
                tags=["sensor1", "main"],
                readings=[1.0, 2.0, 3.0],
            )
            assert model.pressure > 100
            assert model.tags == ["sensor1", "main"]
            assert model.readings == [1.0, 2.0, 3.0]
        finally:
            unit_context.reset(token)


class TestMultiplePintGlassFields:
    """Tests for models with multiple PintGlass fields."""

    def test_multiple_dimensions_input(self) -> None:
        """Model can have multiple Input fields with different dimensions."""
        token = set_unit_system("imperial")
        try:

            class Equipment(BaseModel):
                max_pressure: PintGlass("pressure", "Input")
                pipe_length: PintGlass("length", "Input")
                max_temp: PintGlass("temperature", "Input")

            equip = Equipment(
                max_pressure=100,  # psi
                pipe_length=10,  # feet
                max_temp=212,  # °F
            )

            # Check internal SI values
            assert equip.max_pressure > 100  # pascals > psi value
            assert abs(equip.pipe_length - 3.048) < 0.001  # meters
            assert abs(equip.max_temp - 100) < 0.1  # °C

            # Check serialization returns imperial
            dumped = equip.model_dump()
            assert abs(dumped["max_pressure"] - 100) < 0.01
            assert abs(dumped["pipe_length"] - 10) < 0.01
            assert abs(dumped["max_temp"] - 212) < 0.1
        finally:
            unit_context.reset(token)

    def test_multiple_dimensions_output(self) -> None:
        """Model can have multiple Output fields with different dimensions."""
        token = set_unit_system("imperial")
        try:

            class Results(BaseModel):
                pressure: PintGlass("pressure", "Output")
                length: PintGlass("length", "Output")
                temperature: PintGlass("temperature", "Output")

            results = Results(
                pressure=689476,  # pascals (100 psi)
                length=3.048,  # meters (10 ft)
                temperature=100,  # °C (212°F)
            )

            dumped = results.model_dump()
            assert abs(dumped["pressure"] - 100) < 1
            assert abs(dumped["length"] - 10) < 0.1
            assert abs(dumped["temperature"] - 212) < 1
        finally:
            unit_context.reset(token)


class TestValidation:
    """Tests for input validation."""

    def test_accepts_int_input(self) -> None:
        """Should accept integer input."""
        token = set_unit_system("imperial")
        try:

            class TestModel(BaseModel):
                value: PintGlass("pressure", "Input")

            model = TestModel(value=100)
            assert isinstance(model.value, float)
        finally:
            unit_context.reset(token)

    def test_accepts_string_numeric_input(self) -> None:
        """Should accept string numeric input."""
        token = set_unit_system("imperial")
        try:

            class TestModel(BaseModel):
                value: PintGlass("pressure", "Input")

            model = TestModel(value="100")
            assert isinstance(model.value, float)
        finally:
            unit_context.reset(token)

    def test_rejects_non_numeric_input(self) -> None:
        """Should reject non-numeric input."""
        token = set_unit_system("imperial")
        try:

            class TestModel(BaseModel):
                value: PintGlass("pressure", "Input")

            with pytest.raises(ValidationError):
                TestModel(value="not a number")
        finally:
            unit_context.reset(token)

    def test_output_rejects_non_numeric(self) -> None:
        """Output model should also reject non-numeric input."""
        token = set_unit_system("imperial")
        try:

            class TestModel(BaseModel):
                value: PintGlass("pressure", "Output")

            with pytest.raises(ValidationError):
                TestModel(value="not a number")
        finally:
            unit_context.reset(token)

    def test_unsupported_dimension_error_message(self) -> None:
        """Should provide friendly error message for unsupported dimensions."""
        # Note: This is usually caught at type definition time if dimension is passed to PintGlass()
        # but the validator itself also has the check.
        try:

            class TestModel(BaseModel):
                value: PintGlass("unknown_dim", "Input")

            with pytest.raises(
                ValidationError, match="Unsupported dimension 'unknown_dim'"
            ):
                TestModel(value=100)
        except Exception as e:
            # If it fails at class definition time (which it should if it's a factory)
            assert "Unsupported dimension 'unknown_dim'" in str(e)


class TestJSONSerialization:
    """Tests for JSON serialization."""

    def test_input_json_serialization(self) -> None:
        """Input model should serialize to JSON correctly."""
        token = set_unit_system("imperial")
        try:

            class TestModel(BaseModel):
                pressure: PintGlass("pressure", "Input")

            model = TestModel(pressure=100)
            json_str = model.model_dump_json()
            assert "pressure" in json_str
        finally:
            unit_context.reset(token)

    def test_output_json_serialization(self) -> None:
        """Output model should serialize to JSON correctly."""
        token = set_unit_system("imperial")
        try:

            class TestModel(BaseModel):
                pressure: PintGlass("pressure", "Output")

            model = TestModel(pressure=101325)
            json_str = model.model_dump_json()
            assert "pressure" in json_str
        finally:
            unit_context.reset(token)
