import pytest
from py_flowcheck import check_input, check_output, Schema, ValidationError

# Sample schemas for testing
input_schema = Schema({
    "name": str,
    "age": {"type": int, "min": 0}
})

output_schema = Schema({
    "success": bool,
    "message": str
})

# Sample function to test decorators
@check_input(schema=input_schema, source="args")
@check_output(schema=output_schema)
def sample_function(data):
    return {"success": True, "message": "Data processed"}

def test_sample_function_valid_input():
    valid_data = {"name": "John", "age": 30}
    result = sample_function(valid_data)
    assert result == {"success": True, "message": "Data processed"}

def test_sample_function_invalid_input():
    invalid_data = {"name": "John", "age": -5}
    with pytest.raises(ValidationError):
        sample_function(invalid_data)

def test_sample_function_invalid_output():
    @check_output(schema=output_schema)
    def faulty_function():
        return {"success": True}  # Missing 'message' key

    with pytest.raises(ValidationError):
        faulty_function()