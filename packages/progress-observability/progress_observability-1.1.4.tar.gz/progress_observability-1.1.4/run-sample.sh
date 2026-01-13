#!/bin/bash

set -e  # Exit on any error

# Check required environment variables
echo "🔍 Checking required environment variables..."
REQUIRED_VARS=(
    "AZURE_API_KEY"
    "AZURE_API_ENDPOINT"
    "AZURE_API_VERSION"
    "OBSERVABILITY_ENDPOINT"
    "OBSERVABILITY_API_KEY"
)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: Required environment variable $var is not set"
        exit 1
    fi
done

echo "✅ All required environment variables are set"

echo "🔨 Building Progress Observability Python SDK..."
uv build

echo "📦 Copying wheel to sample_apps..."
cp dist/progress_observability-*.whl sample_apps/

echo "📥 Installing dependencies in sample_apps..."
cd sample_apps
uv sync

echo "🚀 Running test_azure_langchain.py..."
uv run python test_azure_langchain.py

echo "✅ Done!"
