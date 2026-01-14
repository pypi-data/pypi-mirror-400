# py-flowcheck

A lightweight runtime contract validation library for Python backends and data pipelines.

## 🎯 Vision

py-flowcheck provides runtime validation for Python applications with minimal overhead. Add 1-2 decorators to your functions and get immediate contract checks in dev/staging, with configurable sampling in production.

## ✨ Features

- **Lightweight & Fast**: Minimal overhead with configurable sampling
- **Production Ready**: Environment-aware validation with sampling controls
- **Framework Integration**: Built-in support for FastAPI, Flask, and Celery
- **Advanced Validation**: Nested objects, arrays, custom validators, and more
- **Metrics & Monitoring**: Built-in performance metrics and validation tracking
- **Flexible Configuration**: Per-environment settings with multiple validation modes

## 🚀 Quick Start

### Installation

```bash
pip install py-flowcheck
```

### Basic Usage

```python
from py_flowcheck import Schema, check_input, check_output

# Define a schema
user_schema = Schema({
    "id": int,
    "email": {"type": str, "regex": r".+@.+\..+"},
    "age": {"type": int, "min": 0, "max": 120}
})

# Use as decorator
@check_input(user_schema, source="json")
@check_output(user_schema)
def create_user(data):
    # Your business logic here
    return data

# Or validate directly
try:
    user_schema.validate({"id": 1, "email": "test@example.com", "age": 25})
    print("✓ Valid!")
except ValidationError as e:
    print(f"✗ Invalid: {e.violations}")
```

## 📋 Schema Definition

### Basic Types

```python
Schema({
    "name": str,
    "age": int,
    "height": float,
    "active": bool
})
```

### Advanced Validation Rules

```python
Schema({
    # String validation
    "username": {
        "type": str,
        "min_length": 3,
        "max_length": 20,
        "regex": r"^[a-zA-Z0-9_]+$"
    },
    
    # Numeric validation
    "age": {
        "type": int,
        "min": 0,
        "max": 120
    },
    
    # Enum validation
    "status": {
        "type": str,
        "enum": ["active", "inactive", "pending"]
    },
    
    # Nullable fields
    "middle_name": {
        "type": str,
        "nullable": True
    },
    
    # Array validation
    "tags": {
        "type": list,
        "items": str
    },
    
    # Nested objects
    "profile": {
        "type": dict,
        "schema": {
            "bio": {"type": str, "max_length": 500},
            "interests": {"type": list, "items": str}
        }
    },
    
    # Custom validation
    "even_number": {
        "type": int,
        "validator": lambda x: x % 2 == 0
    }
})
```

## 🔧 Configuration

### Environment-Based Configuration

```python
from py_flowcheck import configure

# Development: Full validation, raise on errors
configure(env="dev", sample_size=1.0, mode="raise")

# Staging: Full validation, log errors
configure(env="staging", sample_size=1.0, mode="log")

# Production: Sampled validation, silent mode
configure(env="prod", sample_size=0.1, mode="silent")
```

### Configuration Options

- **env**: `"dev"`, `"staging"`, `"prod"`
- **sample_size**: `0.0` to `1.0` (percentage of validations to perform)
- **mode**: 
  - `"raise"`: Raise ValidationError on failure
  - `"log"`: Log errors but continue execution
  - `"silent"`: Ignore validation failures

### Environment Variables

```bash
export PY_FLOWCHECK_ENV=prod
export PY_FLOWCHECK_SAMPLE_SIZE=0.1
export PY_FLOWCHECK_MODE=silent
```

## 🎭 Decorators

### Input Validation

```python
@check_input(schema, source="json")  # For JSON payloads
@check_input(schema, source="query") # For query parameters
@check_input(schema, source="args")  # For function arguments
def my_function(data):
    return data
```

### Output Validation

```python
@check_output(response_schema)
def my_function():
    return {"status": "success", "data": {...}}
```

### Custom Sample Rates

```python
# Override global sampling for critical validations
@check_input(schema, sample_rate=1.0)  # Always validate
@check_output(schema, sample_rate=0.5)  # 50% sampling
def critical_function(data):
    return process(data)
```

## 🌐 Framework Integration

### FastAPI

```python
from fastapi import FastAPI, Depends
from py_flowcheck.integrations.fastapi import (
    create_validation_dependency,
    setup_fastapi_validation,
    check_output_fastapi
)

app = FastAPI()

# Method 1: Dependency Injection
ValidateUser = create_validation_dependency(user_schema, "json")

@app.post("/users")
@check_output_fastapi(user_response_schema)
async def create_user(validated_data: dict = Depends(ValidateUser)):
    return process_user(validated_data)

# Method 2: Middleware
validation_rules = {
    "post:/users": {
        "request_schema": user_schema,
        "response_schema": user_response_schema
    }
}
setup_fastapi_validation(app, validation_rules)
```

### Flask

```python
from flask import Flask, request, jsonify
from py_flowcheck import check_input, check_output

app = Flask(__name__)

@app.route('/users', methods=['POST'])
@check_input(user_schema, source="json")
@check_output(user_response_schema)
def create_user():
    data = request.get_json()
    return jsonify(process_user(data))
```

### Celery

```python
from celery import Celery
from py_flowcheck import check_input, check_output

app = Celery('tasks')

@app.task
@check_input(task_schema, source="args")
@check_output(result_schema)
def process_data(data):
    return {"result": "processed", "data": data}
```

## 📊 Metrics & Monitoring

### Collecting Metrics

```python
from py_flowcheck import get_metrics, reset_metrics

# Get current metrics
metrics = get_metrics()
print(f"Validation calls: {metrics['validation_calls']}")
print(f"Failures: {metrics['validation_failures']}")
print(f"Average time: {sum(metrics['validation_time_ms']) / len(metrics['validation_time_ms']):.2f}ms")

# Reset metrics
reset_metrics()
```

### Metrics Available

- `validation_calls`: Total number of validations performed
- `validation_failures`: Number of validation failures
- `validation_time_ms`: List of validation times in milliseconds
- `sampling_skips`: Number of validations skipped due to sampling

## 🏗️ Advanced Examples

### Complex Nested Validation

```python
company_schema = Schema({
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
```

### Custom Validators

```python
def validate_credit_card(number):
    """Luhn algorithm validation."""
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d*2))
        return checksum % 10
    return luhn_checksum(number) == 0

payment_schema = Schema({
    "card_number": {
        "type": str,
        "validator": validate_credit_card
    },
    "amount": {
        "type": float,
        "min": 0.01,
        "max": 10000.00
    }
})
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=py_flowcheck

# Run benchmarks
python examples/benchmarks.py
```

## 📈 Performance

py-flowcheck is designed for minimal overhead:

- **Validation overhead**: ~0.1-0.5ms for simple schemas
- **Memory usage**: Minimal, schemas are lightweight
- **Production sampling**: Configurable to reduce overhead in production
- **Caching**: Schema compilation is cached for repeated use

Run benchmarks to see performance on your system:

```bash
python examples/benchmarks.py
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Documentation](https://py-flowcheck.readthedocs.io/)
- [PyPI Package](https://pypi.org/project/py-flowcheck/)
- [GitHub Repository](https://github.com/your-username/py-flowcheck)
- [Issue Tracker](https://github.com/your-username/py-flowcheck/issues)

## 🙏 Acknowledgments

- Inspired by contract programming and design by contract principles
- Built for modern Python applications and microservices
- Designed with production reliability in mind