"""Tests for the StateManager class."""

import pytest
from unittest.mock import Mock, patch
from src.agent.state_manager import StateManager
from src.agent.models.user_data_model import UserData

@pytest.fixture
def state_manager():
    """Fixture for a clean StateManager instance."""
    return StateManager()

class TestStateManager:
    """Test cases for StateManager."""

    def test_initialization(self, state_manager):
        """Test that StateManager initializes with empty UserData."""
        assert isinstance(state_manager.user_data, UserData)
        assert state_manager.user_data.first_name is None
        assert state_manager.user_data.age is None
        assert state_manager.user_data.preferred_schedule is None

    class TestValidateAndStoreInfo:
        """Test cases for validate_and_store_info method."""

        def test_empty_info(self, state_manager):
            """Test handling of empty extracted info."""
            assert state_manager.validate_and_store_info({}) is None
            assert state_manager.user_data.first_name is None
            assert state_manager.user_data.age is None
            assert state_manager.user_data.preferred_schedule is None

        def test_invalid_field(self, state_manager):
            """Test handling of invalid field names."""
            result = state_manager.validate_and_store_info({"invalid_field": "value"})
            assert result is None
            assert state_manager.user_data.first_name is None
            assert state_manager.user_data.age is None
            assert state_manager.user_data.preferred_schedule is None

        @pytest.mark.parametrize("field,value,validator_method", [
            ("first_name", "Juan", "validate_name"),
            ("age", 25, "validate_age"),
            ("preferred_schedule", "mañana", "validate_schedule")
        ])
        def test_valid_single_field(self, state_manager, field, value, validator_method):
            """Test validation and storage of valid single fields."""
            with patch.object(state_manager.validator, validator_method, return_value=None):
                result = state_manager.validate_and_store_info({field: value})
                assert result is None
                assert getattr(state_manager.user_data, field) == value

        @pytest.mark.parametrize("field,value,validator_method,error_msg", [
            ("first_name", "J", "validate_name", "El nombre debe tener al menos 2 caracteres."),
            ("age", 17, "validate_age", "La edad debe estar entre 18 y 80 años."),
            ("preferred_schedule", "noche", "validate_schedule", "El horario debe ser 'mañana' o 'tarde'.")
        ])
        def test_invalid_single_field(self, state_manager, field, value, validator_method, error_msg):
            """Test validation and storage of invalid single fields."""

            with patch.object(state_manager.validator, validator_method, return_value=error_msg):
                result = state_manager.validate_and_store_info({field: value})
                assert result == error_msg
                assert getattr(state_manager.user_data, field) is None

        def test_multiple_fields(self, state_manager):
            """Test validation and storage of multiple fields at once."""
            test_data = {
                "first_name": "Juan",
                "age": 25,
                "preferred_schedule": "mañana"
            }

            with patch.multiple(state_manager.validator,
                             validate_name=Mock(return_value=None),
                             validate_age=Mock(return_value=None),
                             validate_schedule=Mock(return_value=None)):
                result = state_manager.validate_and_store_info(test_data)
                assert result is None
                assert state_manager.user_data.first_name == "Juan"
                assert state_manager.user_data.age == 25
                assert state_manager.user_data.preferred_schedule == "mañana"

    class TestGetCurrentState:
        """Test cases for get_current_state method."""

        def test_empty_state(self, state_manager):
            """Test current state formatting with no data."""
            expected = "Información recopilada:\n\nInformación pendiente:\n- nombre\n- edad\n- horario preferido"
            assert state_manager.get_current_state() == expected

        def test_partial_state(self, state_manager):
            """Test current state formatting with partial data."""
            state_manager.user_data.first_name = "Juan"
            state_manager.user_data.age = 25
            expected = (
                "Información recopilada:\n"
                "- Nombre: Juan\n"
                "- Edad: 25\n"
                "\nInformación pendiente:\n"
                "- horario preferido"
            )
            assert state_manager.get_current_state() == expected

        def test_complete_state(self, state_manager):
            """Test current state formatting with complete data."""
            state_manager.user_data.first_name = "Juan"
            state_manager.user_data.age = 25
            state_manager.user_data.preferred_schedule = "mañana"
            expected = (
                "Información recopilada:\n"
                "- Nombre: Juan\n"
                "- Edad: 25\n"
                "- Horario preferido: mañana"
            )
            assert state_manager.get_current_state() == expected

    class TestPrepareContext:
        """Test cases for prepare_context method."""

        def test_no_error_incomplete(self, state_manager):
            """Test context preparation with no error and incomplete data."""
            assert state_manager.prepare_context() == "SIGUIENTE DATO REQUERIDO: nombre"

        def test_no_error_complete(self, state_manager):
            """Test context preparation with no error and complete data."""
            state_manager.user_data.first_name = "Juan"
            state_manager.user_data.age = 25
            state_manager.user_data.preferred_schedule = "mañana"
            assert state_manager.prepare_context() == "INFORMACIÓN COMPLETA: Despídete amablemente."

        @pytest.mark.parametrize("field,error_msg,expected_reminder", [
            ("first_name", "Error en nombre", "Recuerda: El nombre debe contener solo letras y tener al menos 2 caracteres."),
            ("age", "Error en edad", "Recuerda: La edad debe estar entre 18 y 80 años."),
            ("preferred_schedule", "Error en horario", "Recuerda: El horario debe ser 'mañana' o 'tarde'.")
        ])
        def test_with_validation_error(self, state_manager, field, error_msg, expected_reminder):
            """Test context preparation with validation errors."""

            if field != "first_name":
                state_manager.user_data.first_name = "Juan"
            if field != "age" and field != "first_name":
                state_manager.user_data.age = 25

            expected = (
                f"ERROR DE VALIDACIÓN: {error_msg}\\n"
                f"ACCIÓN REQUERIDA: Explica el error y pide el dato de nuevo de forma amable."
                f"\\n{expected_reminder}"
            )
            assert state_manager.prepare_context(error_msg) == expected

    def test_is_complete(self, state_manager):
        """Test completion status checking."""
        assert not state_manager.is_complete()
        
        state_manager.user_data.first_name = "Juan"
        state_manager.user_data.age = 25
        assert not state_manager.is_complete()
        
        state_manager.user_data.preferred_schedule = "mañana"
        assert state_manager.is_complete()

    def test_get_user_data(self, state_manager):
        """Test user data retrieval."""
        # Test empty data
        assert state_manager.get_user_data() == {
            "first_name": None,
            "age": None,
            "preferred_schedule": None
        }

        # Test with data
        state_manager.user_data.first_name = "Juan"
        state_manager.user_data.age = 25
        state_manager.user_data.preferred_schedule = "mañana"
        
        assert state_manager.get_user_data() == {
            "first_name": "Juan",
            "age": 25,
            "preferred_schedule": "mañana"
        } 