#!/bin/bash
# Script to test template generation

set -e

echo "FastAPI Microservice Template Generator"
echo "========================================"
echo ""

# Check if copier is installed
if ! command -v copier &> /dev/null; then
    echo "Error: copier is not installed"
    echo "Install it with: pip install copier"
    exit 1
fi

# Get project name
read -p "Enter project name (e.g., user-service): " PROJECT_NAME

if [ -z "$PROJECT_NAME" ]; then
    echo "Error: Project name is required"
    exit 1
fi

# Check if directory exists
if [ -d "$PROJECT_NAME" ]; then
    echo "Error: Directory $PROJECT_NAME already exists"
    exit 1
fi

echo ""
echo "Generating project: $PROJECT_NAME"
echo ""

# Generate project from template
copier copy . "$PROJECT_NAME"

echo ""
echo "✅ Project generated successfully!"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_NAME"
echo "  cp .env.example .env"
echo "  # Edit .env with your configuration"
echo "  docker-compose up -d"
echo ""
echo "Or for manual setup:"
echo "  cd $PROJECT_NAME"
echo "  pip install uv"
echo "  uv pip install -e \".[dev]\""
echo "  make dev"
echo ""
