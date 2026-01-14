#!/bin/bash

echo "🔑 py-flowcheck Production Secrets Setup Guide"
echo "=============================================="
echo ""

echo "📦 1. PyPI API Token Setup:"
echo "   1. Go to: https://pypi.org/account/register/"
echo "   2. Create account and verify email"
echo "   3. Go to: https://pypi.org/manage/account/"
echo "   4. Create API token with name: py-flowcheck-github-actions"
echo "   5. Copy token (starts with pypi-)"
echo ""

echo "☁️  2. AWS Access Keys Setup:"
echo "   1. Go to: https://aws.amazon.com/"
echo "   2. Create account or sign in"
echo "   3. Go to: IAM → Users → Create user"
echo "   4. Username: py-flowcheck-github"
echo "   5. Enable programmatic access"
echo "   6. Attach policies: AmazonEKSClusterPolicy, AmazonEC2ContainerRegistryFullAccess"
echo "   7. Copy Access Key ID and Secret Access Key"
echo ""

echo "💬 3. Slack Webhook Setup:"
echo "   1. Go to: https://api.slack.com/apps"
echo "   2. Create New App → From scratch"
echo "   3. App Name: py-flowcheck-notifications"
echo "   4. Enable Incoming Webhooks"
echo "   5. Add webhook to #deployments channel"
echo "   6. Copy webhook URL"
echo ""

echo "🔧 4. Add to GitHub Repository:"
echo "   1. Go to: https://github.com/Swastik-Swarup-Dash/Py_FlowCheck/settings/secrets/actions"
echo "   2. Add these secrets:"
echo "      - PYPI_API_TOKEN: [your PyPI token]"
echo "      - AWS_ACCESS_KEY_ID: [your AWS access key]"
echo "      - AWS_SECRET_ACCESS_KEY: [your AWS secret key]"
echo "      - SLACK_WEBHOOK: [your Slack webhook URL]"
echo ""

echo "✅ After adding secrets, your GitHub Actions will have full automation!"
echo ""

# Check if secrets are set (for local testing)
if [ -n "$PYPI_API_TOKEN" ]; then
    echo "✅ PYPI_API_TOKEN is set"
else
    echo "❌ PYPI_API_TOKEN not set"
fi

if [ -n "$AWS_ACCESS_KEY_ID" ]; then
    echo "✅ AWS_ACCESS_KEY_ID is set"
else
    echo "❌ AWS_ACCESS_KEY_ID not set"
fi

if [ -n "$SLACK_WEBHOOK" ]; then
    echo "✅ SLACK_WEBHOOK is set"
else
    echo "❌ SLACK_WEBHOOK not set"
fi