"""Tests for the UserData model."""

from src.agent.models.user_data_model import UserData

class TestNameValidation:
    """Tests for name validation."""
    
    def test_valid_names(self):
        """Test that valid names are accepted."""
        valid_names = ["Juan", "María José", "Çetin"]
        for name in valid_names:
            user_data = UserData(first_name=name)
            assert user_data.first_name == name

class TestAgeValidation:
    """Tests for age validation."""
    
    def test_valid_ages(self):
        """Test that valid ages are accepted."""
        valid_ages = [19, 30, 45, 80]
        for age in valid_ages:
            user_data = UserData(age=age)
            assert user_data.age == age

class TestScheduleValidation:
    """Tests for schedule validation."""
    
    def test_valid_schedules(self):
        """Test that valid schedules are accepted."""
        valid_schedules = ["mañana", "tarde", "MAÑANA", "TARDE"]
        for schedule in valid_schedules:
            user_data = UserData(preferred_schedule=schedule)
            assert user_data.preferred_schedule.lower() in ["mañana", "tarde"]

class TestCompletionStatus:
    """Tests for completion status methods."""
    
    def test_empty_user_data(self):
        """Test that empty UserData reports correct missing fields."""
        user_data = UserData()
        missing = user_data.get_missing_fields()
        assert len(missing) == 3
        assert set(missing) == {"first_name", "age", "preferred_schedule"}
        assert not user_data.is_complete()

    def test_partially_complete_user_data(self):
        """Test that partially complete UserData reports correct missing fields."""
        user_data = UserData(first_name="Juan")
        missing = user_data.get_missing_fields()
        assert len(missing) == 2
        assert set(missing) == {"age", "preferred_schedule"}
        assert not user_data.is_complete()

    def test_complete_user_data(self):
        """Test that complete UserData reports no missing fields."""
        user_data = UserData(
            first_name="Juan",
            age=25,
            preferred_schedule="mañana"
        )
        assert len(user_data.get_missing_fields()) == 0
        assert user_data.is_complete()

def test_model_serialization():
    """Test that UserData can be serialized to dict."""
    user_data = UserData(
        first_name="Juan",
        age=25,
        preferred_schedule="mañana"
    )
    data_dict = user_data.model_dump()
    assert isinstance(data_dict, dict)
    assert data_dict["first_name"] == "Juan"
    assert data_dict["age"] == 25
    assert data_dict["preferred_schedule"] == "mañana" 