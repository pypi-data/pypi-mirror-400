#!/usr/bin/env python3
"""
Comprehensive example demonstrating all py-flowcheck features.
"""

from py_flowcheck import (
    Schema, ValidationError, check_input, check_output,
    configure, get_config, get_metrics, reset_metrics
)
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure py-flowcheck for different environments
def setup_environment(env: str):
    """Setup py-flowcheck for different environments."""
    if env == "dev":
        configure(env="dev", sample_size=1.0, mode="raise")
    elif env == "staging":
        configure(env="staging", sample_size=1.0, mode="log")
    elif env == "prod":
        configure(env="prod", sample_size=0.1, mode="silent")

# Example 1: Basic Schema Validation
def example_basic_validation():
    """Demonstrate basic schema validation."""
    print("=== Basic Schema Validation ===")
    
    user_schema = Schema({
        "id": int,
        "email": {"type": str, "regex": r".+@.+\..+"},
        "age": {"type": int, "min": 0, "max": 120}
    })
    
    # Valid data
    valid_user = {"id": 1, "email": "john@example.com", "age": 30}
    try:
        user_schema.validate(valid_user)
        print("✓ Valid user data passed validation")
    except ValidationError as e:
        print(f"✗ Validation failed: {e.violations}")
    
    # Invalid data
    invalid_user = {"id": "abc", "email": "invalid-email", "age": -5}
    try:
        user_schema.validate(invalid_user)
        print("✓ Invalid user data passed validation")
    except ValidationError as e:
        print(f"✗ Validation failed: {e.violations}")

# Example 2: Advanced Schema Features
def example_advanced_schema():
    """Demonstrate advanced schema features."""
    print("\n=== Advanced Schema Features ===")
    
    # Custom validator function
    def validate_username(username):
        return len(username) >= 3 and username.isalnum()
    
    advanced_schema = Schema({
        "user": {
            "type": dict,
            "schema": {
                "username": {"type": str, "validator": validate_username},
                "profile": {
                    "type": dict,
                    "schema": {
                        "bio": {"type": str, "max_length": 500},
                        "interests": {"type": list, "items": str}
                    }
                }
            }
        },
        "tags": {"type": list, "items": str},
        "status": {"type": str, "enum": ["active", "inactive", "pending"]}
    })
    
    # Test data
    test_data = {
        "user": {
            "username": "john123",
            "profile": {
                "bio": "Software developer",
                "interests": ["coding", "music", "travel"]
            }
        },
        "tags": ["developer", "python"],
        "status": "active"
    }
    
    try:
        advanced_schema.validate(test_data)
        print("✓ Advanced schema validation passed")
    except ValidationError as e:
        print(f"✗ Advanced validation failed: {e.violations}")

# Example 3: Function Decorators
def example_decorators():
    """Demonstrate function decorators."""
    print("\n=== Function Decorators ===")
    
    input_schema = Schema({
        "name": str,
        "age": {"type": int, "min": 0}
    })
    
    output_schema = Schema({
        "message": str,
        "user_id": int
    })
    
    @check_input(input_schema, source="args")
    @check_output(output_schema)
    def create_user(data):
        """Create a user with validation."""
        return {
            "message": f"User {data['name']} created successfully",
            "user_id": 12345
        }
    
    # Test with valid data
    try:
        result = create_user({"name": "Alice", "age": 25})
        print(f"✓ User creation successful: {result}")
    except Exception as e:
        print(f"✗ User creation failed: {e}")

# Example 4: Configuration and Metrics
def example_config_and_metrics():
    """Demonstrate configuration and metrics."""
    print("\n=== Configuration and Metrics ===")
    
    # Reset metrics
    reset_metrics()
    
    # Setup for development
    setup_environment("dev")
    config = get_config()
    print(f"Current config: env={config.env}, sample_size={config.sample_size}, mode={config.mode}")
    
    # Run some validations to generate metrics
    schema = Schema({"value": int})
    
    for i in range(5):
        try:
            schema.validate({"value": i})
        except ValidationError:
            pass
    
    # Try some invalid data
    try:
        schema.validate({"value": "invalid"})
    except ValidationError:
        pass
    
    # Show metrics
    metrics = get_metrics()
    print(f"Validation metrics: {metrics}")

# Example 5: Production Sampling
def example_production_sampling():
    """Demonstrate production sampling behavior."""
    print("\n=== Production Sampling ===")
    
    # Setup for production with low sampling
    configure(env="prod", sample_size=0.1, mode="silent")
    
    schema = Schema({"test": str})
    
    @check_input(schema, source="args")
    def test_function(data):
        return f"Processed: {data}"
    
    # Run multiple times to see sampling in action
    results = []
    for i in range(10):
        try:
            result = test_function({"test": f"value_{i}"})
            results.append(f"Call {i}: Success")
        except Exception as e:
            results.append(f"Call {i}: {e}")
    
    print("Production sampling results:")
    for result in results:
        print(f"  {result}")
    
    metrics = get_metrics()
    print(f"Sampling skips: {metrics['sampling_skips']}")

if __name__ == "__main__":
    # Run all examples
    example_basic_validation()
    example_advanced_schema()
    example_decorators()
    example_config_and_metrics()
    example_production_sampling()
    
    print("\n=== Final Metrics ===")
    final_metrics = get_metrics()
    print(f"Total validation calls: {final_metrics['validation_calls']}")
    print(f"Total failures: {final_metrics['validation_failures']}")
    print(f"Total sampling skips: {final_metrics['sampling_skips']}")
    if final_metrics['validation_time_ms']:
        avg_time = sum(final_metrics['validation_time_ms']) / len(final_metrics['validation_time_ms'])
        print(f"Average validation time: {avg_time:.2f}ms")