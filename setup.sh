#!/bin/bash

# Create and activate virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "Installing development dependencies..."
pip install pytest pytest-cov

# Create necessary directories
echo "Creating project structure..."
mkdir -p docs
mkdir -p src
mkdir -p tests

# Copy documentation if it doesn't exist
if [ ! -f docs/testing_cheatsheet.md ]; then
    echo "Setting up documentation..."
    touch docs/testing_cheatsheet.md
    touch docs/development_journal.md
    touch docs/setup_guide.md
fi

echo "Setup complete! Activate your virtual environment with:"
echo "source venv/bin/activate"
