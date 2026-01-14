import pytest
from py_flowcheck import Schema, ValidationError


def test_enum_validation():
    """Test enum validation."""
    schema = Schema({
        "status": {"type": str, "enum": ["active", "inactive", "pending"]}
    })
    
    # Valid enum value
    schema.validate({"status": "active"})
    
    # Invalid enum value
    with pytest.raises(ValidationError) as exc_info:
        schema.validate({"status": "unknown"})
    assert "must be one of ['active', 'inactive', 'pending']" in str(exc_info.value.violations)


def test_string_length_validation():
    """Test string length validation."""
    schema = Schema({
        "username": {"type": str, "min_length": 3, "max_length": 10},
        "bio": {"type": str, "max_length": 100}
    })
    
    # Valid lengths
    schema.validate({"username": "john", "bio": "Short bio"})
    
    # Too short
    with pytest.raises(ValidationError) as exc_info:
        schema.validate({"username": "jo", "bio": "Bio"})
    assert "must be at least 3 characters" in str(exc_info.value.violations)
    
    # Too long
    with pytest.raises(ValidationError) as exc_info:
        schema.validate({"username": "verylongusername", "bio": "Bio"})
    assert "must be at most 10 characters" in str(exc_info.value.violations)


def test_max_value_validation():
    """Test max value validation."""
    schema = Schema({
        "age": {"type": int, "min": 0, "max": 120},
        "score": {"type": float, "max": 100.0}
    })
    
    # Valid values
    schema.validate({"age": 25, "score": 85.5})
    
    # Too high
    with pytest.raises(ValidationError) as exc_info:
        schema.validate({"age": 150, "score": 85.5})
    assert "must be at most 120" in str(exc_info.value.violations)


def test_list_validation():
    """Test list item validation."""
    schema = Schema({
        "tags": {"type": list, "items": str},
        "scores": {"type": list, "items": int}
    })
    
    # Valid lists
    schema.validate({"tags": ["python", "coding"], "scores": [85, 90, 78]})
    
    # Invalid item type
    with pytest.raises(ValidationError) as exc_info:
        schema.validate({"tags": ["python", 123], "scores": [85, 90, 78]})
    assert "must be of type str" in str(exc_info.value.violations)


def test_nested_object_validation():
    """Test nested object validation."""
    schema = Schema({
        "user": {
            "type": dict,
            "schema": {
                "name": str,
                "profile": {
                    "type": dict,
                    "schema": {
                        "bio": str,
                        "age": {"type": int, "min": 0}
                    }
                }
            }
        }
    })
    
    # Valid nested object
    valid_data = {
        "user": {
            "name": "John",
            "profile": {
                "bio": "Software developer",
                "age": 30
            }
        }
    }
    schema.validate(valid_data)
    
    # Invalid nested field
    invalid_data = {
        "user": {
            "name": "John",
            "profile": {
                "bio": "Software developer",
                "age": -5
            }
        }
    }
    with pytest.raises(ValidationError) as exc_info:
        schema.validate(invalid_data)
    assert "user.profile.age" in str(exc_info.value.violations)


def test_custom_validator():
    """Test custom validation function."""
    def validate_even_number(value):
        return value % 2 == 0
    
    schema = Schema({
        "even_number": {"type": int, "validator": validate_even_number}
    })
    
    # Valid even number
    schema.validate({"even_number": 4})
    
    # Invalid odd number
    with pytest.raises(ValidationError) as exc_info:
        schema.validate({"even_number": 3})
    assert "failed custom validation" in str(exc_info.value.violations)


def test_custom_validator_exception():
    """Test custom validator that raises exception."""
    def failing_validator(value):
        raise ValueError("Custom validation error")
    
    schema = Schema({
        "test_field": {"type": str, "validator": failing_validator}
    })
    
    with pytest.raises(ValidationError) as exc_info:
        schema.validate({"test_field": "test"})
    assert "Custom validation error" in str(exc_info.value.violations)


def test_nullable_nested_objects():
    """Test nullable nested objects."""
    schema = Schema({
        "optional_profile": {
            "type": dict,
            "nullable": True,
            "schema": {
                "name": str,
                "age": int
            }
        }
    })
    
    # Valid with null
    schema.validate({"optional_profile": None})
    
    # Valid with object
    schema.validate({"optional_profile": {"name": "John", "age": 30}})
    
    # Invalid object structure
    with pytest.raises(ValidationError):
        schema.validate({"optional_profile": {"name": "John"}})  # Missing age


def test_complex_nested_validation():
    """Test complex nested validation with multiple levels."""
    schema = Schema({
        "company": {
            "type": dict,
            "schema": {
                "name": str,
                "departments": {
                    "type": list,
                    "items": {
                        "type": dict,
                        "schema": {
                            "name": str,
                            "employees": {
                                "type": list,
                                "items": {
                                    "type": dict,
                                    "schema": {
                                        "name": str,
                                        "email": {"type": str, "regex": r".+@.+\..+"},
                                        "skills": {"type": list, "items": str}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    })
    
    valid_data = {
        "company": {
            "name": "Tech Corp",
            "departments": [
                {
                    "name": "Engineering",
                    "employees": [
                        {
                            "name": "Alice",
                            "email": "alice@techcorp.com",
                            "skills": ["python", "javascript"]
                        },
                        {
                            "name": "Bob",
                            "email": "bob@techcorp.com",
                            "skills": ["java", "kotlin"]
                        }
                    ]
                }
            ]
        }
    }
    
    schema.validate(valid_data)
    
    # Test with invalid email in nested structure
    invalid_data = valid_data.copy()
    invalid_data["company"]["departments"][0]["employees"][0]["email"] = "invalid-email"
    
    with pytest.raises(ValidationError) as exc_info:
        schema.validate(invalid_data)
    assert "company.departments[0].employees[0].email" in str(exc_info.value.violations)


def test_field_path_in_violations():
    """Test that field paths are correctly reported in violations."""
    schema = Schema({
        "level1": {
            "type": dict,
            "schema": {
                "level2": {
                    "type": dict,
                    "schema": {
                        "level3": {"type": int, "min": 10}
                    }
                }
            }
        }
    })
    
    with pytest.raises(ValidationError) as exc_info:
        schema.validate({
            "level1": {
                "level2": {
                    "level3": 5
                }
            }
        })
    
    violations = exc_info.value.violations
    assert any("level1.level2.level3" in violation for violation in violations)