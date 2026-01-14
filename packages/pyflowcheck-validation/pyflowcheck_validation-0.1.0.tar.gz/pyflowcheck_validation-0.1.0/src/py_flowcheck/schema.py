import re
import os
import functools
from typing import Any, Dict, Callable, Optional, List, Union

class ValidationError(Exception):
    """
    Custom exception raised when schema validation fails.
    """
    def __init__(self, message: str, violations: Optional[List[str]] = None):
        super().__init__(message)
        self.violations = violations or []


class Schema:
    """
    A class for defining and validating schemas for data validation.

    Example:
        user_schema = Schema({
            "id": int,
            "email": {"type": str, "regex": r".+@.+\..+"},
            "age": {"type": int, "nullable": True, "min": 0, "max": 120},
            "tags": {"type": list, "items": str},
            "profile": {
                "type": dict,
                "schema": {
                    "name": str,
                    "bio": {"type": str, "max_length": 500}
                }
            }
        })
    """

    def __init__(self, schema: Dict[str, Any]):
        """
        Initializes the schema with validation rules.

        :param schema: A dictionary defining the schema rules.
        """
        self.schema = schema

    @staticmethod
    def from_dict(defn: Dict[str, Any]) -> "Schema":
        """
        Creates a Schema instance from a dictionary definition.

        :param defn: The schema definition as a dictionary.
        :return: A Schema instance.
        """
        return Schema(defn)

    def validate(self, data: Dict[str, Any], path: str = "") -> None:
        """
        Validates the given data against the schema.

        :param data: The data to validate.
        :param path: Current path in nested validation.
        :raises ValidationError: If validation fails.
        """
        violations = []
        
        for field, rule in self.schema.items():
            field_path = f"{path}.{field}" if path else field
            value = data.get(field)

            # Check for missing required fields
            if value is None and not (isinstance(rule, dict) and rule.get("nullable")):
                violations.append(f"Field '{field_path}' is required but missing")
                continue

            # Handle nullable fields
            if isinstance(rule, dict) and rule.get("nullable") and value is None:
                continue

            # Type validation
            expected_type = rule if isinstance(rule, type) else rule.get("type")
            if expected_type and not isinstance(value, expected_type):
                violations.append(f"Field '{field_path}' must be of type {expected_type.__name__}, got {type(value).__name__}")
                continue

            # Additional validations for dict rules
            if isinstance(rule, dict):
                violations.extend(self._validate_field(value, rule, field_path))

        if violations:
            raise ValidationError("Schema validation failed", violations)

    def _validate_field(self, value: Any, rule: Dict[str, Any], field_path: str) -> List[str]:
        """
        Validate a single field with its rule.
        """
        violations = []

        # Regex validation
        if "regex" in rule and value is not None:
            if not re.match(rule["regex"], str(value)):
                violations.append(f"Field '{field_path}' does not match the required pattern")

        # Enum validation
        if "enum" in rule and value is not None:
            if value not in rule["enum"]:
                violations.append(f"Field '{field_path}' must be one of {rule['enum']}, got '{value}'")

        # Min/Max value validation
        if "min" in rule and value is not None:
            if value < rule["min"]:
                violations.append(f"Field '{field_path}' must be at least {rule['min']}")
        
        if "max" in rule and value is not None:
            if value > rule["max"]:
                violations.append(f"Field '{field_path}' must be at most {rule['max']}")

        # String length validation
        if "min_length" in rule and isinstance(value, str):
            if len(value) < rule["min_length"]:
                violations.append(f"Field '{field_path}' must be at least {rule['min_length']} characters")
        
        if "max_length" in rule and isinstance(value, str):
            if len(value) > rule["max_length"]:
                violations.append(f"Field '{field_path}' must be at most {rule['max_length']} characters")

        # List validation
        if rule.get("type") == list and "items" in rule and isinstance(value, list):
            item_rule = rule["items"]
            for i, item in enumerate(value):
                if isinstance(item_rule, type):
                    # Simple type validation
                    if not isinstance(item, item_rule):
                        violations.append(f"Field '{field_path}[{i}]' must be of type {item_rule.__name__}")
                elif isinstance(item_rule, dict):
                    # Complex item validation
                    if item_rule.get("type") == dict and "schema" in item_rule:
                        # Nested object in list
                        nested_schema = Schema(item_rule["schema"])
                        try:
                            nested_schema.validate(item, f"{field_path}[{i}]")
                        except ValidationError as e:
                            violations.extend(e.violations)
                    else:
                        # Other complex validations for list items
                        violations.extend(self._validate_field(item, item_rule, f"{field_path}[{i}]"))

        # Nested object validation
        if rule.get("type") == dict and "schema" in rule and isinstance(value, dict):
            nested_schema = Schema(rule["schema"])
            try:
                nested_schema.validate(value, field_path)
            except ValidationError as e:
                violations.extend(e.violations)

        # Custom validation function
        if "validator" in rule and value is not None:
            try:
                if not rule["validator"](value):
                    violations.append(f"Field '{field_path}' failed custom validation")
            except Exception as e:
                violations.append(f"Field '{field_path}' validation error: {str(e)}")

        return violations

    def __repr__(self) -> str:
        return f"<Schema rules={self.schema}>"


def check_input(schema: Schema, source: str = "json", sample_rate: float = 1.0) -> Callable:
    """
    Decorator to validate function inputs against a schema.

    :param schema: The Schema instance to validate against.
    :param source: The source of the data (e.g., "json", "query").
    :param sample_rate: Probability of validation in production (0.0 to 1.0).
    :return: The decorated function.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Determine environment
            env = os.getenv("ENV", "dev").lower()

            # Skip validation in production based on sample rate
            if env == "prod" and sample_rate < 1.0:
                import random
                if random.random() > sample_rate:
                    return func(*args, **kwargs)

            # Extract data from the source
            if source == "json":
                request = kwargs.get("request") or args[0]
                data = request.json
            elif source == "query":
                request = kwargs.get("request") or args[0]
                data = request.args
            else:
                raise ValueError(f"Unsupported source: {source}")

            # Validate data
            try:
                schema.validate(data)
            except ValidationError as e:
                raise ValidationError(f"Input validation failed: {e.violations}")

            return func(*args, **kwargs)
        return wrapper
    return decorator