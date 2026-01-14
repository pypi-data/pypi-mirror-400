from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
import uvicorn
from py_flowcheck import Schema, ValidationError, configure
from py_flowcheck.integrations.fastapi import (
    setup_fastapi_validation,
    create_validation_dependency,
    check_output_fastapi
)
from py_flowcheck.monitoring import get_health_status, is_healthy
from py_flowcheck.decorators import get_metrics
from py_flowcheck.logging_config import setup_production_logging

# Setup production logging
setup_production_logging(level="INFO", enable_json=True)

# Configure py-flowcheck for production
configure(env="prod", sample_size=0.1, mode="log")

# Create FastAPI app
app = FastAPI(
    title="py-flowcheck Production Example", 
    version="1.0.0",
    description="Production-ready FastAPI application with py-flowcheck validation"
)

# Health check endpoints
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    if is_healthy():
        return {"status": "healthy"}
    else:
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/health/detailed")
async def detailed_health():
    """Detailed health status with metrics."""
    return get_health_status()

@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus-style metrics endpoint."""
    metrics = get_metrics()
    health = get_health_status()
    
    # Convert to Prometheus format
    prometheus_metrics = []
    prometheus_metrics.append(f"py_flowcheck_validation_calls_total {metrics['validation_calls']}")
    prometheus_metrics.append(f"py_flowcheck_validation_failures_total {metrics['validation_failures']}")
    prometheus_metrics.append(f"py_flowcheck_sampling_skips_total {metrics['sampling_skips']}")
    prometheus_metrics.append(f"py_flowcheck_success_rate_percent {health['metrics']['success_rate_percent']}")
    prometheus_metrics.append(f"py_flowcheck_avg_validation_time_ms {health['metrics']['average_time_ms']}")
    prometheus_metrics.append(f"py_flowcheck_uptime_seconds {health['uptime_seconds']}")
    
    return "\n".join(prometheus_metrics)

# Define schemas
user_create_schema = Schema({
    "username": {"type": str, "min_length": 3, "max_length": 50},
    "email": {"type": str, "regex": r".+@.+\..+"},
    "age": {"type": int, "min": 13, "max": 120},
    "profile": {
        "type": dict,
        "nullable": True,
        "schema": {
            "bio": {"type": str, "max_length": 500},
            "interests": {"type": list, "items": str}
        }
    }
})

user_response_schema = Schema({
    "id": int,
    "username": str,
    "email": str,
    "age": int,
    "profile": {"type": dict, "nullable": True},
    "created_at": str,
    "status": {"type": str, "enum": ["active", "inactive"]}
})

# Setup validation rules for middleware
validation_rules = {
    "post:/users": {
        "request_schema": user_create_schema,
        "response_schema": user_response_schema
    },
    "get:/users/{user_id}": {
        "response_schema": user_response_schema
    }
}

# Add validation middleware
setup_fastapi_validation(app, validation_rules)

# Create validation dependencies
ValidateUserCreate = create_validation_dependency(user_create_schema, "json")

# Mock database
users_db = {}
next_user_id = 1

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "py-flowcheck Production FastAPI Example",
        "version": "1.0.0",
        "environment": "production",
        "validation": "enabled with sampling",
        "endpoints": [
            "GET /health - Health check",
            "GET /health/detailed - Detailed health status",
            "GET /metrics - Prometheus metrics",
            "GET /users - List all users",
            "POST /users - Create a new user",
            "GET /users/{user_id} - Get user by ID"
        ]
    }

@app.get("/users")
@check_output_fastapi(Schema({"users": {"type": list}}))
async def list_users():
    """List all users."""
    return {"users": list(users_db.values())}

@app.post("/users")
async def create_user(validated_data: dict = Depends(ValidateUserCreate)):
    """Create a new user with validation."""
    global next_user_id
    
    user = {
        "id": next_user_id,
        "username": validated_data["username"],
        "email": validated_data["email"],
        "age": validated_data["age"],
        "profile": validated_data.get("profile"),
        "created_at": "2024-01-01T00:00:00Z",
        "status": "active"
    }
    
    users_db[next_user_id] = user
    next_user_id += 1
    
    return user

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    """Get a user by ID."""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    return users_db[user_id]

# Error handlers
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc: ValidationError):
    """Handle validation errors."""
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "detail": exc.violations,
            "message": str(exc)
        }
    )

if __name__ == "__main__":
    print("Starting py-flowcheck Production FastAPI Application...")
    print("Health check: http://127.0.0.1:8000/health")
    print("Metrics: http://127.0.0.1:8000/metrics")
    print("API docs: http://127.0.0.1:8000/docs")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True
    )