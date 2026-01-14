from fastapi import FastAPI, Request, Response, HTTPException, Depends
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response as StarletteResponse
import json
from typing import Callable, Optional
from py_flowcheck import Schema, ValidationError, get_config


class ValidationMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic request/response validation.
    """
    
    def __init__(self, app, validation_rules: dict = None):
        super().__init__(app)
        self.validation_rules = validation_rules or {}
    
    async def dispatch(self, request: StarletteRequest, call_next: Callable) -> StarletteResponse:
        # Get validation rule for this endpoint
        path = request.url.path
        method = request.method.lower()
        rule_key = f"{method}:{path}"
        
        if rule_key in self.validation_rules:
            rule = self.validation_rules[rule_key]
            
            # Validate request if schema provided
            if "request_schema" in rule:
                try:
                    if request.method in ["POST", "PUT", "PATCH"]:
                        body = await request.body()
                        if body:
                            data = json.loads(body)
                            rule["request_schema"].validate(data)
                except ValidationError as e:
                    return JSONResponse(
                        status_code=422,
                        content={"detail": f"Request validation failed: {e.violations}"}
                    )
                except Exception as e:
                    return JSONResponse(
                        status_code=400,
                        content={"detail": f"Request parsing error: {str(e)}"}
                    )
        
        # Process request
        response = await call_next(request)
        
        # Validate response if schema provided
        if rule_key in self.validation_rules and "response_schema" in self.validation_rules[rule_key]:
            rule = self.validation_rules[rule_key]
            try:
                # Only validate successful responses
                if 200 <= response.status_code < 300:
                    response_body = b""
                    async for chunk in response.body_iterator:
                        response_body += chunk
                    
                    if response_body:
                        data = json.loads(response_body)
                        rule["response_schema"].validate(data)
                    
                    # Recreate response with same body
                    return StarletteResponse(
                        content=response_body,
                        status_code=response.status_code,
                        headers=response.headers,
                        media_type=response.media_type
                    )
            except ValidationError as e:
                config = get_config()
                if config.mode == "raise":
                    return JSONResponse(
                        status_code=500,
                        content={"detail": f"Response validation failed: {e.violations}"}
                    )
                # In log or silent mode, return original response
        
        return response


def create_validation_dependency(schema: Schema, source: str = "json"):
    """
    Create a FastAPI dependency for request validation.
    
    :param schema: Schema to validate against
    :param source: Source of data ("json", "query", "form")
    :return: FastAPI dependency function
    """
    async def validate_request(request: Request):
        try:
            if source == "json":
                data = await request.json()
            elif source == "query":
                data = dict(request.query_params)
            elif source == "form":
                form_data = await request.form()
                data = dict(form_data)
            else:
                raise ValueError(f"Unsupported source: {source}")
            
            schema.validate(data)
            return data
            
        except ValidationError as e:
            raise HTTPException(
                status_code=422,
                detail=f"Validation failed: {e.violations}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Request parsing error: {str(e)}"
            )
    
    return validate_request


def check_output_fastapi(schema: Schema):
    """
    Decorator for validating FastAPI response payloads.
    
    :param schema: The Schema instance to validate the response.
    :return: The decorated function.
    """
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            response = await func(*args, **kwargs)
            try:
                schema.validate(response)
            except ValidationError as e:
                config = get_config()
                if config.mode == "raise":
                    raise HTTPException(
                        status_code=500, 
                        detail=f"Response validation failed: {e.violations}"
                    )
                elif config.mode == "log":
                    import logging
                    logging.error(f"Response validation failed for {func.__name__}: {e.violations}")
            return response
        return wrapper
    return decorator


# Example usage functions
def setup_fastapi_validation(app: FastAPI, validation_rules: dict = None):
    """
    Setup validation middleware for FastAPI app.
    
    :param app: FastAPI application instance
    :param validation_rules: Dictionary mapping endpoints to validation schemas
    """
    app.add_middleware(ValidationMiddleware, validation_rules=validation_rules)


# Example validation rules format:
# validation_rules = {
#     "post:/users": {
#         "request_schema": user_create_schema,
#         "response_schema": user_response_schema
#     },
#     "get:/users/{user_id}": {
#         "response_schema": user_response_schema
#     }
# }


# Initialize FastAPI app with validation
app = FastAPI()

# Define input schema for user creation
user_input_schema = Schema({
    "id": int,
    "email": {"type": str, "regex": r".+@.+\..+"},
    "age": {"type": int, "nullable": True, "min": 0},
})

# Define output schema for user response
user_output_schema = Schema({
    "id": int,
    "email": str,
    "age": {"type": int, "nullable": True},
    "status": {"type": str, "enum": ["active", "inactive"]},
})

# Setup validation rules
validation_rules = {
    "post:/users": {
        "request_schema": user_input_schema,
        "response_schema": user_output_schema
    }
}

# Add validation middleware
setup_fastapi_validation(app, validation_rules)

# Alternative: Using dependency injection
ValidateUserInput = create_validation_dependency(user_input_schema, "json")

@app.post("/users")
@check_output_fastapi(schema=user_output_schema)
async def create_user(validated_data: dict = Depends(ValidateUserInput)):
    """
    Endpoint to create a user using dependency injection for validation.
    """
    # Simulate user creation logic
    user = {
        "id": validated_data["id"],
        "email": validated_data["email"],
        "age": validated_data.get("age"),
        "status": "active",  # Default status
    }
    return user

@app.post("/users-middleware")
async def create_user_middleware(request: Request):
    """
    Endpoint that relies on middleware for validation.
    """
    data = await request.json()
    
    # Simulate user creation logic
    user = {
        "id": data["id"],
        "email": data["email"],
        "age": data.get("age"),
        "status": "active",
    }
    return user

# Example usage of the FastAPI app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)