#!/bin/bash
# Run the Voice-First AI Assistant

cd "$(dirname "$0")"

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo ""
    echo "Please run the setup first:"
    echo "  ./install.sh"
    echo ""
    echo "Or manually create .env with your API keys"
    exit 1
fi

# Run the assistant
python3 main.py
