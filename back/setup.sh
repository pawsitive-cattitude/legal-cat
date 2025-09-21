#!/bin/bash

# Legal Cat Backend Setup Script
# This script helps set up the development environment

set -e

echo "🐱 Legal Cat Backend Setup"
echo "=========================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv is installed"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "⚠️  gcloud CLI is not installed."
    echo "   Install it from: https://cloud.google.com/sdk/docs/install"
    echo "   This is required for Google Cloud authentication."
else
    echo "✅ gcloud CLI is installed"
fi

# Install dependencies
echo "📦 Installing dependencies..."
uv sync

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo "   Please edit .env with your Google Cloud project details"
else
    echo "✅ .env file already exists"
fi

# Create directories
echo "📁 Creating required directories..."
mkdir -p uploads
mkdir -p analysis_cache
mkdir -p chroma_db
mkdir -p /tmp/legal_docs
echo "✅ Directories created"

# Check environment configuration
echo "🔍 Checking environment configuration..."

if [ -f .env ]; then
    source .env
    
    if [ -z "$GOOGLE_CLOUD_PROJECT" ] || [ "$GOOGLE_CLOUD_PROJECT" = "your-project-id" ]; then
        echo "⚠️  GOOGLE_CLOUD_PROJECT not configured in .env"
        echo "   Please set your Google Cloud project ID"
        SETUP_NEEDED=true
    fi
    
    if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ] || [ "$GOOGLE_APPLICATION_CREDENTIALS" = "/path/to/your/service-account-key.json" ]; then
        echo "⚠️  GOOGLE_APPLICATION_CREDENTIALS not configured in .env"
        echo "   Please set the path to your service account key file"
        SETUP_NEEDED=true
    fi
    
    if [ "$SETUP_NEEDED" = true ]; then
        echo ""
        echo "📋 Next steps:"
        echo "1. Follow the Google Cloud setup guide: ./GOOGLE_CLOUD_SETUP.md"
        echo "2. Edit .env with your project details"
        echo "3. Run the server: uv run uvicorn app.main:app --reload"
    else
        echo "✅ Environment configuration looks good"
    fi
fi

# Test basic functionality
echo "🧪 Testing basic imports..."
if uv run python -c "from app.mcp_enhanced_analyzer import MCPEnhancedLegalAnalyzer; print('✅ Imports successful')" 2>/dev/null; then
    echo "✅ Core modules can be imported"
else
    echo "❌ Import test failed. Check your environment setup."
    exit 1
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To start the development server:"
echo "  uv run uvicorn app.main:app --reload"
echo ""
echo "To run tests:"
echo "  uv run python test_system.py"
echo ""
echo "API documentation will be available at:"
echo "  http://localhost:8000/docs"
echo ""
echo "📚 For detailed setup instructions, see:"
echo "  - ./README.md"
echo "  - ./GOOGLE_CLOUD_SETUP.md"