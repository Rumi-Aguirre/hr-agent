"""Tests for the UserDataValidator class."""

import pytest
from src.agent.validators import UserDataValidator

class TestUserDataValidator:
    """Test cases for UserDataValidator."""

    class TestAgeValidation:
        """Test cases for age validation."""

        @pytest.mark.parametrize("age", [19, 25, 45, 79, 80])
        def test_valid_ages(self, age):
            """Test that valid ages are accepted."""
            assert UserDataValidator.validate_age(age) is None

        @pytest.mark.parametrize("age", [-1, 0, 17, 18, 81, 100])
        def test_invalid_ages(self, age):
            """Test that invalid ages are rejected."""
            error = UserDataValidator.validate_age(age)
            assert error == "La edad debe estar entre 18 y 80 años."

    class TestNameValidation:
        """Test cases for name validation."""

        @pytest.mark.parametrize("name", [
            "Juan",
            "María José",
            "Jean Pierre",
            "Çetin",
            "José María",
            "Ñandu",
            "Zoë"
        ])
        def test_valid_names(self, name):
            """Test that valid names are accepted."""
            assert UserDataValidator.validate_name(name) is None

        @pytest.mark.parametrize("name,expected_error", [
            ("J", "El nombre debe tener al menos 2 caracteres."),
            ("", "El nombre debe contener solo letras."),
            ("Juan123", "El nombre debe contener solo letras."),
            ("Juan!", "El nombre debe contener solo letras."),
            ("Juan@García", "El nombre debe contener solo letras."),
            ("123", "El nombre debe contener solo letras."),
            ("J@ne", "El nombre debe contener solo letras.")
        ])
        def test_invalid_names(self, name, expected_error):
            """Test that invalid names are rejected with correct error message."""
            error = UserDataValidator.validate_name(name)
            assert error == expected_error

        def test_whitespace_handling(self):
            """Test that names with whitespace are handled correctly."""
            # Valid cases with whitespace
            assert UserDataValidator.validate_name("Juan Carlos") is None
            assert UserDataValidator.validate_name("María  José") is None
            # Invalid cases with whitespace
            assert UserDataValidator.validate_name("  ") == "El nombre debe contener solo letras."

    class TestScheduleValidation:
        """Test cases for schedule validation."""

        @pytest.mark.parametrize("schedule", [
            "mañana", "tarde",
            "MAÑANA", "TARDE",
            "Mañana", "Tarde"
        ])
        def test_valid_schedules(self, schedule):
            """Test that valid schedules are accepted."""
            assert UserDataValidator.validate_schedule(schedule) is None

        @pytest.mark.parametrize("schedule", [
            "",
            "morning",
            "afternoon",
            "noche",
            "medio día",
            "123",
            "mañana tarde",
            "manana",
            "tardé"
        ])
        def test_invalid_schedules(self, schedule):
            """Test that invalid schedules are rejected."""
            error = UserDataValidator.validate_schedule(schedule)
            assert error == "El horario debe ser 'mañana' o 'tarde'."

        def test_case_insensitivity(self):
            """Test that schedule validation is case-insensitive."""
            assert UserDataValidator.validate_schedule("MAÑANA") is None
            assert UserDataValidator.validate_schedule("tarde") is None
            assert UserDataValidator.validate_schedule("Mañana") is None
            assert UserDataValidator.validate_schedule("TARDE") is None 