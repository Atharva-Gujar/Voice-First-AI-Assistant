#!/bin/bash
# Installation script for Voice-First AI Assistant

echo "=================================================="
echo "  Voice-First AI Assistant - Installation"
echo "=================================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✓ Python 3 found"
echo ""

# Install packages
echo "Installing required packages..."
echo "This may take a few minutes..."
echo ""

python3 -m pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Installation failed"
    echo "Please check the error messages above"
    exit 1
fi

echo ""
echo "✓ All packages installed successfully!"
echo ""

# Run setup
echo "=================================================="
echo "  Running Setup Wizard"
echo "=================================================="
echo ""

python3 setup_assistant.py

echo ""
echo "Installation complete!"
