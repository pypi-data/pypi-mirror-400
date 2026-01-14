from py_flowcheck import Schema, check_input, ValidationError
import pytest


# Define a sample schema for testing
user_schema = Schema({
    "id": int,
    "email": {"type": str, "regex": r".+@.+\..+"},
    "age": {"type": int, "nullable": True, "min": 0},
})

def test_schema_validation_valid():
    valid_data = {
        "id": 1,
        "email": "test@example.com",
        "age": 30
    }
    user_schema.validate(valid_data)

def test_schema_validation_invalid_email():
    invalid_data = {
        "id": 1,
        "email": "invalid-email",
        "age": 30
    }
    with pytest.raises(ValidationError, match="Schema validation failed"):
        user_schema.validate(invalid_data)

def test_schema_validation_missing_required_field():
    invalid_data = {
        "email": "test@example.com",
        "age": 30
    }
    with pytest.raises(ValidationError, match="Schema validation failed"):
        user_schema.validate(invalid_data)

def test_schema_validation_nullable_field():
    valid_data = {
        "id": 1,
        "email": "test@example.com",
        "age": None
    }
    user_schema.validate(valid_data)

def test_schema_validation_invalid_age():
    invalid_data = {
        "id": 1,
        "email": "test@example.com",
        "age": -1
    }
    with pytest.raises(ValidationError, match="Schema validation failed"):
        user_schema.validate(invalid_data)