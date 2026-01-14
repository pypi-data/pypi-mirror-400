# Production Deployment Guide

## 🚀 Quick Production Setup

### 1. Environment Configuration

Set these environment variables for production:

```bash
export PY_FLOWCHECK_ENV=prod
export PY_FLOWCHECK_SAMPLE_SIZE=0.1          # 10% validation sampling
export PY_FLOWCHECK_MODE=log                 # Log errors, don't raise
export PY_FLOWCHECK_ENABLE_METRICS=true      # Enable metrics collection
export PY_FLOWCHECK_MAX_METRICS_HISTORY=5000 # Keep last 5000 metrics
```

### 2. Docker Deployment

```bash
# Build the image
docker build -t py-flowcheck-app .

# Run with production settings
docker run -d \
  --name py-flowcheck-prod \
  -p 8000:8000 \
  -e PY_FLOWCHECK_ENV=prod \
  -e PY_FLOWCHECK_SAMPLE_SIZE=0.1 \
  -e PY_FLOWCHECK_MODE=log \
  py-flowcheck-app
```

### 3. Docker Compose (Recommended)

```bash
# Start the full stack with monitoring
docker-compose up -d

# Check health
curl http://localhost:8000/health

# View metrics
curl http://localhost:8000/metrics
```

### 4. Kubernetes Deployment

```bash
# Deploy to Kubernetes
kubectl apply -f k8s-deployment.yaml

# Check status
kubectl get pods -l app=py-flowcheck
kubectl get svc py-flowcheck-service
```

## 📊 Monitoring & Observability

### Health Checks

- **Simple**: `GET /health` - Returns 200 if healthy
- **Detailed**: `GET /health/detailed` - Full health status with metrics
- **Kubernetes**: Built-in liveness and readiness probes

### Metrics

- **Prometheus**: `GET /metrics` - Prometheus-compatible metrics
- **Grafana**: Pre-configured dashboards in `monitoring/grafana/`
- **Custom**: Use `get_metrics()` and `get_health_status()` in your code

### Key Metrics to Monitor

```
py_flowcheck_validation_calls_total      # Total validations performed
py_flowcheck_validation_failures_total   # Total validation failures
py_flowcheck_success_rate_percent        # Success rate percentage
py_flowcheck_avg_validation_time_ms      # Average validation time
py_flowcheck_sampling_skips_total        # Validations skipped due to sampling
py_flowcheck_uptime_seconds             # Service uptime
```

## ⚙️ Production Configuration

### Recommended Settings by Environment

**Development:**
```python
configure(env=\"dev\", sample_size=1.0, mode=\"raise\")
```

**Staging:**
```python
configure(env=\"staging\", sample_size=1.0, mode=\"log\")
```

**Production:**
```python
configure(env=\"prod\", sample_size=0.1, mode=\"log\")
```

### Performance Tuning

1. **Sampling Rate**: Start with 10% (0.1) in production, adjust based on load
2. **Metrics History**: Limit to 1000-5000 entries to control memory usage
3. **Validation Mode**: Use \"log\" or \"silent\" in production to avoid exceptions
4. **Schema Caching**: Schemas are automatically cached for performance

### Memory Management

```python
from py_flowcheck import reset_metrics, configure

# Reset metrics periodically to prevent memory growth
reset_metrics()

# Limit metrics history
configure(max_metrics_history=1000)
```

## 🔒 Security Considerations

1. **Input Validation**: Always validate user inputs in production
2. **Error Handling**: Use \"log\" mode to prevent information leakage
3. **Monitoring**: Monitor validation failures for potential attacks
4. **Rate Limiting**: Implement rate limiting on validation-heavy endpoints

## 📈 Scaling Guidelines

### Horizontal Scaling

- py-flowcheck is stateless and scales horizontally
- Each instance maintains its own metrics
- Use load balancers to distribute traffic

### Vertical Scaling

- Validation overhead is typically <1ms per request
- Memory usage scales with metrics history size
- CPU usage is minimal for most validation rules

### Performance Benchmarks

Run benchmarks to understand overhead:

```bash
python examples/benchmarks.py
```

Expected performance:
- Simple validation: 0.1-0.5ms overhead
- Complex nested validation: 1-5ms overhead
- 10% sampling reduces overhead by ~90%

## 🚨 Troubleshooting

### High Validation Failures

1. Check `/health/detailed` for failure patterns
2. Review logs for validation error details
3. Consider adjusting validation rules
4. Monitor for potential data quality issues

### Performance Issues

1. Reduce sampling rate in production
2. Optimize complex validation rules
3. Use \"silent\" mode if validation is non-critical
4. Monitor validation timing metrics

### Memory Usage

1. Reduce `max_metrics_history`
2. Call `reset_metrics()` periodically
3. Monitor metrics collection overhead

## 📋 Production Checklist

- [ ] Environment variables configured
- [ ] Health checks responding
- [ ] Metrics endpoint accessible
- [ ] Logging configured and working
- [ ] Monitoring dashboards set up
- [ ] Sampling rate appropriate for load
- [ ] Error handling tested
- [ ] Performance benchmarks run
- [ ] Security review completed
- [ ] Scaling strategy defined

## 🔄 Deployment Pipeline

### CI/CD Integration

```yaml
# Example GitHub Actions
- name: Test py-flowcheck
  run: |
    pip install -e .
    pytest tests/
    python examples/benchmarks.py

- name: Build Docker image
  run: docker build -t py-flowcheck:${{ github.sha }} .

- name: Deploy to production
  run: |
    kubectl set image deployment/py-flowcheck-app py-flowcheck=py-flowcheck:${{ github.sha }}
    kubectl rollout status deployment/py-flowcheck-app
```

### Blue-Green Deployment

1. Deploy new version to green environment
2. Run health checks and validation tests
3. Switch traffic from blue to green
4. Monitor metrics for any issues
5. Keep blue environment as rollback option

## 📞 Support

For production issues:

1. Check health endpoints first
2. Review application logs
3. Monitor validation metrics
4. Check resource usage (CPU/memory)
5. Verify configuration settings

Remember: py-flowcheck is designed to fail gracefully. Even if validation fails, your application should continue running in \"log\" or \"silent\" mode.