import time
from typing import Dict, Any, Optional
from py_flowcheck.decorators import get_metrics
from py_flowcheck.config import get_config

class HealthChecker:
    """Health check utilities for py-flowcheck in production."""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status."""
        metrics = get_metrics()
        config = get_config()
        uptime = time.time() - self.start_time
        
        # Calculate health metrics
        total_calls = metrics["validation_calls"]
        failures = metrics["validation_failures"]
        success_rate = ((total_calls - failures) / total_calls * 100) if total_calls > 0 else 100
        
        avg_time = (
            sum(metrics["validation_time_ms"]) / len(metrics["validation_time_ms"])
            if metrics["validation_time_ms"] else 0
        )
        
        status = {
            "status": "healthy" if success_rate >= 95 else "degraded" if success_rate >= 90 else "unhealthy",
            "uptime_seconds": uptime,
            "config": {
                "env": config.env,
                "sample_size": config.sample_size,
                "mode": config.mode
            },
            "metrics": {
                "total_validations": total_calls,
                "success_rate_percent": round(success_rate, 2),
                "average_time_ms": round(avg_time, 3),
                "sampling_skips": metrics["sampling_skips"]
            }
        }
        
        return status
    
    def is_healthy(self) -> bool:
        """Simple health check."""
        return self.get_health_status()["status"] == "healthy"

# Global health checker instance
health_checker = HealthChecker()

def get_health_status() -> Dict[str, Any]:
    """Get health status."""
    return health_checker.get_health_status()

def is_healthy() -> bool:
    """Check if py-flowcheck is healthy."""
    return health_checker.is_healthy()