"""Tests for the ExtractedInfo model."""

import pytest
from pydantic import ValidationError
from src.agent.models.extracted_info_model import ExtractedInfo

class TestInitialization:
    """Tests for ExtractedInfo initialization."""
    
    def test_empty_initialization(self):
        """Test that ExtractedInfo can be initialized with no values."""
        info = ExtractedInfo()
        assert info.first_name is None
        assert info.age is None
        assert info.preferred_schedule is None

    def test_partial_initialization(self):
        """Test that ExtractedInfo can be initialized with partial values."""
        test_cases = [
            ({"first_name": "Juan"}, {"first_name": "Juan", "age": None, "preferred_schedule": None}),
            ({"age": 25}, {"first_name": None, "age": 25, "preferred_schedule": None}),
            ({"preferred_schedule": "mañana"}, {"first_name": None, "age": None, "preferred_schedule": "mañana"}),
        ]
        
        for input_data, expected in test_cases:
            info = ExtractedInfo(**input_data)
            assert info.model_dump() == expected

    def test_complete_initialization(self):
        """Test that ExtractedInfo can be initialized with all values."""
        info = ExtractedInfo(
            first_name="Juan",
            age=25,
            preferred_schedule="mañana"
        )
        assert info.first_name == "Juan"
        assert info.age == 25
        assert info.preferred_schedule == "mañana"

class TestFieldValidation:
    """Tests for field validation."""

    class TestNameValidation:
        """Tests for name field validation."""

        def test_valid_names(self):
            """Test that valid names are accepted."""
            valid_names = ["Juan", "María José", "Çetin"]
            for name in valid_names:
                info = ExtractedInfo(first_name=name)
                assert info.first_name == name

        def test_none_name(self):
            """Test that None is accepted for name."""
            info = ExtractedInfo(first_name=None)
            assert info.first_name is None

    class TestAgeValidation:
        """Tests for age field validation."""

        def test_valid_ages(self):
            """Test that valid ages are accepted."""
            valid_ages = [18, 25, 45, 80]
            for age in valid_ages:
                info = ExtractedInfo(age=age)
                assert info.age == age

        def test_none_age(self):
            """Test that None is accepted for age."""
            info = ExtractedInfo(age=None)
            assert info.age is None

    class TestScheduleValidation:
        """Tests for schedule field validation."""

        def test_valid_schedules(self):
            """Test that valid schedules are accepted."""
            valid_schedules = ["mañana", "tarde", "MAÑANA", "TARDE"]
            for schedule in valid_schedules:
                info = ExtractedInfo(preferred_schedule=schedule)
                assert info.preferred_schedule.lower() in ["mañana", "tarde"]

        def test_none_schedule(self):
            """Test that None is accepted for schedule."""
            info = ExtractedInfo(preferred_schedule=None)
            assert info.preferred_schedule is None

class TestSerialization:
    """Tests for model serialization."""

    def test_empty_serialization(self):
        """Test serialization of empty ExtractedInfo."""
        info = ExtractedInfo()
        data_dict = info.model_dump()
        assert isinstance(data_dict, dict)
        assert all(v is None for v in data_dict.values())

    def test_partial_serialization(self):
        """Test serialization of partially complete ExtractedInfo."""
        info = ExtractedInfo(first_name="Juan", age=25)
        data_dict = info.model_dump()
        assert isinstance(data_dict, dict)
        assert data_dict["first_name"] == "Juan"
        assert data_dict["age"] == 25
        assert data_dict["preferred_schedule"] is None

    def test_complete_serialization(self):
        """Test serialization of complete ExtractedInfo."""
        info = ExtractedInfo(
            first_name="Juan",
            age=25,
            preferred_schedule="mañana"
        )
        data_dict = info.model_dump()
        assert isinstance(data_dict, dict)
        assert data_dict["first_name"] == "Juan"
        assert data_dict["age"] == 25
        assert data_dict["preferred_schedule"] == "mañana"
