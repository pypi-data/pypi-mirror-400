# GitHub Actions Deployment Guide

## 🚀 Automated CI/CD with GitHub Actions

This repository includes comprehensive GitHub Actions workflows for automated testing, building, and deployment of py-flowcheck to production environments.

## 📋 Workflows Overview

### 1. **CI/CD Pipeline** (`.github/workflows/ci-cd.yml`)
- **Triggers**: Push to main/develop, Pull requests, Releases
- **Features**:
  - Multi-Python version testing (3.9, 3.11, 3.12)
  - Automated testing with coverage reporting
  - Performance benchmarking
  - Docker image building and publishing
  - Automatic deployment to production

### 2. **Manual Deployment** (`.github/workflows/deploy.yml`)
- **Triggers**: Manual workflow dispatch
- **Features**:
  - Choose staging or production environment
  - Environment-specific configuration
  - Health checks and smoke tests
  - Docker Compose deployment

### 3. **Release Management** (`.github/workflows/release.yml`)
- **Triggers**: Git tags (v*)
- **Features**:
  - Automated PyPI package publishing
  - GitHub release creation
  - Version management

### 4. **Security Scanning** (`.github/workflows/security.yml`)
- **Triggers**: Weekly schedule, Push to main, Pull requests
- **Features**:
  - Dependency vulnerability scanning
  - Code security analysis with Bandit and Semgrep
  - Dependency review for PRs

### 5. **Performance Monitoring** (`.github/workflows/performance.yml`)
- **Triggers**: Every 6 hours, Manual dispatch
- **Features**:
  - Automated benchmarking
  - Performance regression detection
  - Load testing with k6
  - Performance trend tracking

## 🔧 Setup Instructions

### 1. Repository Secrets

Add these secrets to your GitHub repository:

```bash
# Required for PyPI publishing
PYPI_API_TOKEN=your_pypi_token

# Required for AWS deployment (if using)
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret

# Optional: Slack notifications
SLACK_WEBHOOK=your_slack_webhook_url
```

### 2. Environment Configuration

Create environments in GitHub repository settings:

- **staging**: For staging deployments
- **production**: For production deployments (with protection rules)

### 3. Branch Protection

Configure branch protection for `main`:
- Require status checks to pass
- Require branches to be up to date
- Require review from code owners

## 🚀 Deployment Strategies

### Automatic Deployment
```bash
# Push to main branch triggers production deployment
git push origin main

# Push to develop branch triggers staging deployment  
git push origin develop
```

### Manual Deployment
1. Go to Actions tab in GitHub
2. Select "Docker Deploy" workflow
3. Click "Run workflow"
4. Choose environment (staging/production)
5. Monitor deployment progress

### Release Deployment
```bash
# Create and push a tag for release
git tag v1.0.0
git push origin v1.0.0

# This triggers:
# - PyPI package publishing
# - GitHub release creation
# - Production deployment
```

## 📊 Monitoring & Alerts

### Performance Monitoring
- Automated benchmarks run every 6 hours
- Performance regression alerts if overhead > 1ms
- Load testing on manual trigger

### Security Monitoring
- Weekly dependency scans
- Real-time security analysis on PRs
- Automated security reports

### Health Monitoring
- Post-deployment health checks
- Smoke tests validation
- Application metrics verification

## 🔄 Workflow Examples

### Development Workflow
```bash
# 1. Create feature branch
git checkout -b feature/new-validation

# 2. Make changes and commit
git add .
git commit -m "Add new validation feature"

# 3. Push and create PR
git push origin feature/new-validation
# Create PR in GitHub UI

# 4. Automated checks run:
#    - Tests across Python versions
#    - Security scans
#    - Performance benchmarks

# 5. After approval, merge to main
#    - Triggers production deployment
#    - Runs full test suite
#    - Deploys to production with health checks
```

### Hotfix Workflow
```bash
# 1. Create hotfix branch from main
git checkout -b hotfix/critical-fix main

# 2. Make fix and test
git commit -m "Fix critical validation bug"

# 3. Push and create PR
git push origin hotfix/critical-fix

# 4. Emergency deployment (if needed)
#    - Use manual deployment workflow
#    - Deploy directly to production
#    - Monitor health checks

# 5. Merge PR after validation
```

### Release Workflow
```bash
# 1. Prepare release
git checkout main
git pull origin main

# 2. Update version and changelog
# Edit pyproject.toml version
# Update CHANGELOG.md

# 3. Create release tag
git tag v1.2.0
git push origin v1.2.0

# 4. Automated release process:
#    - Builds and tests package
#    - Publishes to PyPI
#    - Creates GitHub release
#    - Deploys to production
```

## 🛠️ Customization

### Environment Variables
Customize deployment by modifying workflow environment variables:

```yaml
env:
  PY_FLOWCHECK_ENV: prod
  PY_FLOWCHECK_SAMPLE_SIZE: 0.1
  PY_FLOWCHECK_MODE: log
  PY_FLOWCHECK_ENABLE_METRICS: true
```

### Deployment Targets
Modify deployment steps for your infrastructure:

```yaml
# For Kubernetes
- name: Deploy to Kubernetes
  run: |
    kubectl apply -f k8s-deployment.yaml
    kubectl rollout status deployment/py-flowcheck-app

# For AWS ECS
- name: Deploy to ECS
  run: |
    aws ecs update-service --cluster prod --service py-flowcheck --force-new-deployment

# For Docker Swarm
- name: Deploy to Swarm
  run: |
    docker stack deploy -c docker-compose.yml py-flowcheck
```

### Notification Channels
Add notifications for deployment events:

```yaml
- name: Notify Teams
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.TEAMS_WEBHOOK }}
```

## 🔍 Troubleshooting

### Common Issues

1. **Test Failures**
   - Check test logs in Actions tab
   - Run tests locally: `pytest tests/ -v`
   - Verify dependencies: `pip install -r requirements-prod.txt`

2. **Deployment Failures**
   - Check health endpoints after deployment
   - Verify environment variables
   - Review application logs

3. **Security Scan Failures**
   - Update vulnerable dependencies
   - Review security scan reports
   - Fix code security issues

### Debug Commands
```bash
# Local testing
python -m pytest tests/ -v --tb=short

# Local benchmarking
python examples/benchmarks.py

# Local security scan
bandit -r src/
safety check -r requirements-prod.txt

# Local Docker build
docker build -t py-flowcheck-test .
docker run -p 8000:8000 py-flowcheck-test
```

## 📈 Best Practices

1. **Always test locally** before pushing
2. **Use feature branches** for development
3. **Keep PRs small** and focused
4. **Monitor deployment health** after releases
5. **Review security scans** regularly
6. **Update dependencies** frequently
7. **Document breaking changes** in releases

This GitHub Actions setup provides enterprise-grade CI/CD for py-flowcheck with automated testing, security scanning, performance monitoring, and production deployment! 🎯