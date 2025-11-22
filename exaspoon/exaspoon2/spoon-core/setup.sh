#!/bin/bash

# SpoonAI Automatic Setup Script with uv
# This script automatically sets up the environment using uv

set -e

echo "🥄 Setting up SpoonAI environment with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   or visit https://github.com/astral-sh/uv"
    exit 1
fi

echo "✅ uv detected"

# Create virtual environment and install dependencies
echo "📦 Creating virtual environment and installing dependencies..."
uv sync

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your API keys and configuration"
fi

echo ""
echo "🎉 SpoonAI setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys and configuration"
echo "2. Run tests: uv run pytest"
echo "3. Start the application: uv run python -m spoon_ai"
echo "4. Activate shell: uv shell"
echo ""
echo "For more information, see README.md"
