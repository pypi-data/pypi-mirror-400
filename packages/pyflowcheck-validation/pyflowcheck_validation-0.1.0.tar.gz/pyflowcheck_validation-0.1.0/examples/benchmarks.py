#!/usr/bin/env python3
"""
Performance benchmarks for py-flowcheck validation.
"""

import time
import statistics
from typing import List, Dict, Any
from py_flowcheck import Schema, ValidationError, configure, get_metrics, reset_metrics

def benchmark_function(func, iterations: int = 1000) -> Dict[str, float]:
    """
    Benchmark a function and return performance metrics.
    
    :param func: Function to benchmark
    :param iterations: Number of iterations to run
    :return: Performance metrics
    """
    times = []
    
    for _ in range(iterations):
        start_time = time.perf_counter()
        try:
            func()
        except Exception:
            pass  # Ignore validation errors for timing
        end_time = time.perf_counter()
        times.append((end_time - start_time) * 1000)  # Convert to milliseconds
    
    return {
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "std_dev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "total_ms": sum(times),
        "iterations": iterations
    }

def create_test_data() -> Dict[str, Any]:
    """Create test data for benchmarking."""
    return {
        "simple": {"id": 1, "name": "test"},
        "complex": {
            "user": {
                "id": 1,
                "username": "testuser",
                "email": "test@example.com",
                "profile": {
                    "bio": "Test user bio",
                    "interests": ["coding", "music", "travel"],
                    "settings": {
                        "theme": "dark",
                        "notifications": True
                    }
                }
            },
            "metadata": {
                "created_at": "2024-01-01T00:00:00Z",
                "tags": ["user", "test", "benchmark"],
                "version": 1
            }
        },
        "large_list": {
            "items": [{"id": i, "value": f"item_{i}"} for i in range(100)]
        }
    }

def create_schemas() -> Dict[str, Schema]:
    """Create test schemas for benchmarking."""
    return {
        "simple": Schema({
            "id": int,
            "name": str
        }),
        "complex": Schema({
            "user": {
                "type": dict,
                "schema": {
                    "id": int,
                    "username": {"type": str, "min_length": 3},
                    "email": {"type": str, "regex": r".+@.+\..+"},
                    "profile": {
                        "type": dict,
                        "schema": {
                            "bio": {"type": str, "max_length": 500},
                            "interests": {"type": list, "items": str},
                            "settings": {
                                "type": dict,
                                "schema": {
                                    "theme": {"type": str, "enum": ["light", "dark"]},
                                    "notifications": bool
                                }
                            }
                        }
                    }
                }
            },
            "metadata": {
                "type": dict,
                "schema": {
                    "created_at": str,
                    "tags": {"type": list, "items": str},
                    "version": int
                }
            }
        }),
        "large_list": Schema({
            "items": {
                "type": list,
                "items": {
                    "type": dict,
                    "schema": {
                        "id": int,
                        "value": str
                    }
                }
            }
        })
    }

def benchmark_validation_overhead():
    """Benchmark validation overhead compared to no validation."""
    print("=== Validation Overhead Benchmark ===")
    
    test_data = create_test_data()
    schemas = create_schemas()
    
    def no_validation():
        """Baseline: no validation."""
        data = test_data["simple"]
        # Simulate some processing
        return data["id"] + len(data["name"])
    
    def with_validation():
        """With validation."""
        data = test_data["simple"]
        schemas["simple"].validate(data)
        # Simulate some processing
        return data["id"] + len(data["name"])
    
    # Benchmark both approaches
    baseline = benchmark_function(no_validation, 10000)
    validated = benchmark_function(with_validation, 10000)
    
    overhead = validated["mean_ms"] - baseline["mean_ms"]
    overhead_percent = (overhead / baseline["mean_ms"]) * 100
    
    print(f"Baseline (no validation): {baseline['mean_ms']:.4f}ms")
    print(f"With validation: {validated['mean_ms']:.4f}ms")
    print(f"Overhead: {overhead:.4f}ms ({overhead_percent:.2f}%)")

def benchmark_schema_complexity():
    """Benchmark different schema complexities."""
    print("\n=== Schema Complexity Benchmark ===")
    
    test_data = create_test_data()
    schemas = create_schemas()
    
    for name, schema in schemas.items():
        data = test_data[name]
        
        def validate():
            schema.validate(data)
        
        results = benchmark_function(validate, 1000)
        print(f"{name.capitalize()} schema: {results['mean_ms']:.4f}ms ± {results['std_dev_ms']:.4f}ms")

def benchmark_sampling_performance():
    """Benchmark performance with different sampling rates."""
    print("\n=== Sampling Performance Benchmark ===")
    
    from py_flowcheck.decorators import check_input
    
    schema = Schema({"value": int})
    test_data = {"value": 42}
    
    sampling_rates = [1.0, 0.5, 0.1, 0.01]
    
    for rate in sampling_rates:
        configure(env="prod", sample_size=rate, mode="silent")
        reset_metrics()
        
        @check_input(schema, source="args")
        def test_function(data):
            return data["value"] * 2
        
        def run_test():
            test_function(test_data)
        
        results = benchmark_function(run_test, 1000)
        metrics = get_metrics()
        
        actual_rate = (metrics["validation_calls"] / 1000) if metrics["validation_calls"] > 0 else 0
        
        print(f"Sample rate {rate:4.2f}: {results['mean_ms']:.4f}ms, "
              f"actual validation rate: {actual_rate:.3f}")

def benchmark_validation_modes():
    """Benchmark different validation modes."""
    print("\n=== Validation Modes Benchmark ===")
    
    schema = Schema({"value": str})  # Will fail with int input
    test_data = {"value": 42}  # Invalid data
    
    modes = ["raise", "log", "silent"]
    
    for mode in modes:
        configure(env="dev", sample_size=1.0, mode=mode)
        
        def validate():
            try:
                schema.validate(test_data)
            except ValidationError:
                pass  # Expected for "raise" mode
        
        results = benchmark_function(validate, 1000)
        print(f"Mode '{mode}': {results['mean_ms']:.4f}ms")

def benchmark_nested_validation():
    """Benchmark nested object validation performance."""
    print("\n=== Nested Validation Benchmark ===")
    
    # Create schemas with different nesting levels
    schemas = {}
    test_data = {}
    
    for depth in [1, 3, 5, 7]:
        # Build nested schema
        schema_def = {"value": int}
        data = {"value": 42}
        
        for i in range(depth - 1):
            schema_def = {"nested": {"type": dict, "schema": schema_def}}
            data = {"nested": data}
        
        schemas[f"depth_{depth}"] = Schema(schema_def)
        test_data[f"depth_{depth}"] = data
    
    for name, schema in schemas.items():
        data = test_data[name]
        
        def validate():
            schema.validate(data)
        
        results = benchmark_function(validate, 1000)
        depth = name.split("_")[1]
        print(f"Nesting depth {depth}: {results['mean_ms']:.4f}ms")

def run_all_benchmarks():
    """Run all performance benchmarks."""
    print("py-flowcheck Performance Benchmarks")
    print("=" * 50)
    
    # Configure for benchmarking
    configure(env="dev", sample_size=1.0, mode="raise")
    
    benchmark_validation_overhead()
    benchmark_schema_complexity()
    benchmark_sampling_performance()
    benchmark_validation_modes()
    benchmark_nested_validation()
    
    print("\n" + "=" * 50)
    print("Benchmark completed!")

if __name__ == "__main__":
    run_all_benchmarks()