import pytest
from py_flowcheck import (
    Schema, ValidationError, check_input, check_output,
    configure, get_config, get_metrics, reset_metrics
)
from py_flowcheck.decorators import validate_with_mode


def test_metrics_collection():
    """Test that metrics are collected correctly."""
    reset_metrics()
    
    schema = Schema({"value": int})
    
    # Valid validation
    validate_with_mode(schema, {"value": 42})
    
    # Invalid validation
    try:
        validate_with_mode(schema, {"value": "invalid"})
    except ValidationError:
        pass
    
    metrics = get_metrics()
    assert metrics["validation_calls"] == 2
    assert metrics["validation_failures"] == 1
    assert len(metrics["validation_time_ms"]) == 2


def test_metrics_reset():
    """Test that metrics can be reset."""
    schema = Schema({"value": int})
    
    # Generate some metrics
    validate_with_mode(schema, {"value": 42})
    
    # Check metrics exist
    metrics = get_metrics()
    assert metrics["validation_calls"] > 0
    
    # Reset and check
    reset_metrics()
    metrics = get_metrics()
    assert metrics["validation_calls"] == 0
    assert metrics["validation_failures"] == 0
    assert len(metrics["validation_time_ms"]) == 0


def test_sampling_behavior():
    """Test sampling behavior in production mode."""
    reset_metrics()
    configure(env="prod", sample_size=0.0, mode="silent")  # No sampling
    
    schema = Schema({"value": int})
    
    @check_input(schema, source="args")
    def test_function(data):
        return data["value"]
    
    # Run multiple times
    for _ in range(10):
        test_function({"value": 42})
    
    metrics = get_metrics()
    # With 0% sampling, all should be skipped
    assert metrics["sampling_skips"] == 10
    assert metrics["validation_calls"] == 0


def test_sampling_with_rate():
    """Test sampling with a specific rate."""
    reset_metrics()
    configure(env="prod", sample_size=1.0, mode="silent")  # 100% sampling
    
    schema = Schema({"value": int})
    
    @check_input(schema, source="args")
    def test_function(data):
        return data["value"]
    
    # Run multiple times
    for _ in range(10):
        test_function({"value": 42})
    
    metrics = get_metrics()
    # With 100% sampling, none should be skipped
    assert metrics["sampling_skips"] == 0
    assert metrics["validation_calls"] == 10


def test_validation_modes():
    """Test different validation modes."""
    schema = Schema({"value": str})  # Will fail with int
    
    # Test raise mode
    configure(env="dev", sample_size=1.0, mode="raise")
    with pytest.raises(ValidationError):
        validate_with_mode(schema, {"value": 42})
    
    # Test log mode (should not raise)
    configure(env="dev", sample_size=1.0, mode="log")
    validate_with_mode(schema, {"value": 42})  # Should not raise
    
    # Test silent mode (should not raise)
    configure(env="dev", sample_size=1.0, mode="silent")
    validate_with_mode(schema, {"value": 42})  # Should not raise


def test_decorator_with_different_modes():
    """Test decorators with different validation modes."""
    schema = Schema({"value": str})
    
    @check_input(schema, source="args")
    def test_function(data):
        return data["value"]
    
    # Test raise mode
    configure(env="dev", sample_size=1.0, mode="raise")
    with pytest.raises(ValidationError):
        test_function({"value": 42})
    
    # Test log mode
    configure(env="dev", sample_size=1.0, mode="log")
    result = test_function({"value": 42})  # Should not raise
    assert result == 42
    
    # Test silent mode
    configure(env="dev", sample_size=1.0, mode="silent")
    result = test_function({"value": 42})  # Should not raise
    assert result == 42


def test_output_validation_modes():
    """Test output validation with different modes."""
    schema = Schema({"result": str})
    
    @check_output(schema)
    def test_function():
        return {"result": 42}  # Invalid: should be string
    
    # Test raise mode
    configure(env="dev", sample_size=1.0, mode="raise")
    with pytest.raises(ValidationError):
        test_function()
    
    # Test log mode
    configure(env="dev", sample_size=1.0, mode="log")
    result = test_function()  # Should not raise
    assert result == {"result": 42}
    
    # Test silent mode
    configure(env="dev", sample_size=1.0, mode="silent")
    result = test_function()  # Should not raise
    assert result == {"result": 42}


def test_custom_sample_rate_override():
    """Test that decorators can override global sample rate."""
    reset_metrics()
    configure(env="prod", sample_size=0.0, mode="silent")  # Global: no sampling
    
    schema = Schema({"value": int})
    
    @check_input(schema, source="args", sample_rate=1.0)  # Override: 100% sampling
    def test_function(data):
        return data["value"]
    
    test_function({"value": 42})
    
    metrics = get_metrics()
    # Should validate despite global 0% sampling
    assert metrics["validation_calls"] == 1
    assert metrics["sampling_skips"] == 0


def test_performance_timing():
    """Test that performance timing is recorded."""
    reset_metrics()
    configure(env="dev", sample_size=1.0, mode="raise")
    
    schema = Schema({"value": int})
    
    # Run some validations
    for i in range(5):
        validate_with_mode(schema, {"value": i})
    
    metrics = get_metrics()
    assert len(metrics["validation_time_ms"]) == 5
    assert all(time >= 0 for time in metrics["validation_time_ms"])


def test_config_persistence():
    """Test that configuration persists across calls."""
    configure(env="staging", sample_size=0.5, mode="log")
    
    config1 = get_config()
    config2 = get_config()
    
    assert config1.env == config2.env == "staging"
    assert config1.sample_size == config2.sample_size == 0.5
    assert config1.mode == config2.mode == "log"


def test_environment_based_behavior():
    """Test different behavior based on environment."""
    schema = Schema({"value": int})
    
    @check_input(schema, source="args")
    def test_function(data):
        return data["value"]
    
    # Development: should always validate
    configure(env="dev", sample_size=0.5, mode="raise")
    reset_metrics()
    
    for _ in range(10):
        test_function({"value": 42})
    
    dev_metrics = get_metrics()
    
    # Production: should respect sampling
    configure(env="prod", sample_size=0.5, mode="silent")
    reset_metrics()
    
    for _ in range(100):  # More iterations to see sampling effect
        test_function({"value": 42})
    
    prod_metrics = get_metrics()
    
    # In dev, all should be validated (sample_size ignored in dev for this test)
    # In prod, some should be skipped due to sampling
    assert prod_metrics["sampling_skips"] > 0