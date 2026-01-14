#!/bin/bash

# Production Setup Script for py-flowcheck
echo "🚀 Setting up py-flowcheck for production..."

# Set production environment variables
export PY_FLOWCHECK_ENV=prod
export PY_FLOWCHECK_SAMPLE_SIZE=0.1
export PY_FLOWCHECK_MODE=log
export PY_FLOWCHECK_ENABLE_METRICS=true
export PY_FLOWCHECK_MAX_METRICS_HISTORY=5000

echo "✅ Environment variables set:"
echo "   PY_FLOWCHECK_ENV=$PY_FLOWCHECK_ENV"
echo "   PY_FLOWCHECK_SAMPLE_SIZE=$PY_FLOWCHECK_SAMPLE_SIZE"
echo "   PY_FLOWCHECK_MODE=$PY_FLOWCHECK_MODE"

# Install production requirements
echo "📦 Installing production requirements..."
pip install -r requirements-prod.txt

# Install py-flowcheck in production mode
echo "🔧 Installing py-flowcheck..."
pip install -e .

# Test production setup
echo "🧪 Testing production setup..."
python -c "
from py_flowcheck import get_health_status, is_healthy, setup_production_logging, configure
setup_production_logging(level='INFO', enable_json=True)
configure(env='prod', sample_size=0.1, mode='log')
health = get_health_status()
print('Health Status:', health['status'])
print('Environment:', health['config']['env'])
print('Sample Rate:', health['config']['sample_size'])
print('Mode:', health['config']['mode'])
assert is_healthy(), 'Health check failed!'
print('✅ Production setup successful!')
"

echo ""
echo "🎉 py-flowcheck is ready for production!"
echo ""
echo "📋 Next steps:"
echo "   1. Start your application with production settings"
echo "   2. Monitor health at: /health and /health/detailed"
echo "   3. Check metrics at: /metrics"
echo "   4. Review logs for validation activity"
echo ""
echo "🔗 Quick start:"
echo "   python examples/fastapi_example.py"
echo ""