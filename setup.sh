#!/bin/bash

echo "🎤 Voice-First AI Assistant Setup"
echo "=================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check for .env file
echo ""
if [ -f ".env" ]; then
    echo "✓ .env file found"
else
    echo "⚠️  No .env file found"
    echo "   Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "   Please edit .env and add your API keys:"
    echo "   - ANTHROPIC_API_KEY"
    echo "   - OPENAI_API_KEY"
fi

echo ""
echo "=================================="
echo "Setup complete! 🎉"
echo ""
echo "To run the assistant:"
echo "  1. Activate the virtual environment: source venv/bin/activate"
echo "  2. Make sure your API keys are in .env"
echo "  3. Run: python main.py"
echo ""
