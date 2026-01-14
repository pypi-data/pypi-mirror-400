import functools
import logging
import random
import time
from typing import Callable, Any
from py_flowcheck.schema import Schema, ValidationError
from py_flowcheck.config import get_config

# Configure logging
logger = logging.getLogger(__name__)

# Metrics storage
_metrics = {
    "validation_calls": 0,
    "validation_failures": 0,
    "validation_time_ms": [],
    "sampling_skips": 0
}

def get_metrics() -> dict:
    """Get validation metrics."""
    return _metrics.copy()

def reset_metrics() -> None:
    """Reset validation metrics."""
    global _metrics
    _metrics = {
        "validation_calls": 0,
        "validation_failures": 0,
        "validation_time_ms": [],
        "sampling_skips": 0
    }

def _validate_with_metrics(schema: Schema, data: dict) -> None:
    """Validate data with metrics collection."""
    global _metrics
    start_time = time.time()
    _metrics["validation_calls"] += 1
    
    try:
        schema.validate(data)
    except ValidationError as e:
        _metrics["validation_failures"] += 1
        raise
    finally:
        validation_time = (time.time() - start_time) * 1000
        _metrics["validation_time_ms"].append(validation_time)

def validate_with_mode(schema: Schema, data: dict, mode: str = None) -> None:
    """Validate data respecting the validation mode."""
    config = get_config()
    effective_mode = mode or config.mode
    
    try:
        _validate_with_metrics(schema, data)
    except ValidationError as e:
        if effective_mode == "raise":
            raise
        elif effective_mode == "log":
            logger.error(f"Validation failed: {e.violations}")
        elif effective_mode == "silent":
            pass

# For Logging Func calls
def log_function_call(func: Callable) -> Callable:
    """logs functions calls with their args"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.info(f"{func.__name__} returned: {result}")
        return result
    return wrapper


#Ensuring preconditions are met
def precondition(precondition: Callable[..., bool]) -> Callable:
    """Decorator to ensure the precondtions are met before executing the funcion"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not precondition(*args, **kwargs):
                raise ValueError(f"PreCondtion has been failed for function '{func.__name__}'")
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Decorator for debugging function calls
def debug_function_call(func: Callable) -> Callable:
    """Logs the function name, arguments, and return value for debugging purposes."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__} with args: {args}, kwargs: {kwargs}")
        result = func(*args, **kwargs)
        logger.debug(f"{func.__name__} returned: {result}")
        return result
    return wrapper


# Decorator for enforcing postconditions
def postcondition(postcondition: Callable[[Any], bool]) -> Callable:
    """Ensures a postcondition is met after executing the function."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if not postcondition(result):
                raise ValueError(f"Postcondition failed for function '{func.__name__}'")
            return result
        return wrapper
    return decorator


# Decorator for validating function inputs
def check_input(schema: Schema, source: str = "json", sample_rate: float = None) -> Callable:
    """
    Decorator to validate function inputs against a schema.

    :param schema: The Schema instance to validate against.
    :param source: The source of the data (e.g., "json", "query", "args").
    :param sample_rate: Override global sample rate for this validation.
    :return: The decorated function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            config = get_config()
            effective_sample_rate = sample_rate if sample_rate is not None else config.sample_size
            
            # Skip validation in production based on sample rate
            if config.env == "prod" and effective_sample_rate < 1.0:
                if random.random() > effective_sample_rate:
                    _metrics["sampling_skips"] += 1
                    return func(*args, **kwargs)

            try:
                # Extract data from the source
                if source == "json":
                    request = kwargs.get("request") or (args[0] if args else None)
                    if hasattr(request, 'json'):
                        data = request.json() if callable(request.json) else request.json
                    else:
                        raise ValueError("Request object does not have json attribute")
                elif source == "query":
                    request = kwargs.get("request") or (args[0] if args else None)
                    data = request.args if hasattr(request, 'args') else {}
                elif source == "args":
                    data = kwargs.get("data") or (args[0] if args else {})
                else:
                    raise ValueError(f"Unsupported source: {source}")

                # Validate data with metrics
                _validate_with_metrics(schema, data)
                
            except ValidationError as e:
                if config.mode == "raise":
                    raise ValidationError(f"Input validation failed: {e.violations}")
                elif config.mode == "log":
                    logger.error(f"Input validation failed for {func.__name__}: {e.violations}")
                elif config.mode == "silent":
                    pass
                    
            except Exception as e:
                _metrics["validation_failures"] += 1
                
                if config.mode == "raise":
                    raise ValueError(f"Input validation error: {str(e)}")
                elif config.mode == "log":
                    logger.error(f"Input validation error for {func.__name__}: {str(e)}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Decorator for validating function outputs
def check_output(schema: Schema, sample_rate: float = None) -> Callable:
    """
    Decorator to validate function outputs against a schema.

    :param schema: The Schema instance to validate the output.
    :param sample_rate: Override global sample rate for this validation.
    :return: The decorated function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            config = get_config()
            effective_sample_rate = sample_rate if sample_rate is not None else config.sample_size
            
            result = func(*args, **kwargs)
            
            # Skip validation in production based on sample rate
            if config.env == "prod" and effective_sample_rate < 1.0:
                if random.random() > effective_sample_rate:
                    _metrics["sampling_skips"] += 1
                    return result

            try:
                # Validate the result with metrics
                _validate_with_metrics(schema, result)
                
            except ValidationError as e:
                if config.mode == "raise":
                    raise ValidationError(f"Output validation failed: {e.violations}")
                elif config.mode == "log":
                    logger.error(f"Output validation failed for {func.__name__}: {e.violations}")
                elif config.mode == "silent":
                    pass
                    
            except Exception as e:
                _metrics["validation_failures"] += 1
                
                if config.mode == "raise":
                    raise ValueError(f"Output validation error: {str(e)}")
                elif config.mode == "log":
                    logger.error(f"Output validation error for {func.__name__}: {str(e)}")
            
            return result
        return wrapper
    return decorator