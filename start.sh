#!/bin/bash

# Font Precision Recognizer - Startup Script
# This script sets up and runs the application

set -e

echo "🎨 Font Precision Recognizer - Startup Script"
echo "=============================================="

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version detected"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt
echo "✓ Dependencies installed"

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p data
mkdir -p logs
mkdir -p static/images
echo "✓ Directories created"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env configuration file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your Google Generative AI API key"
    echo "   Visit: https://ai.google.dev/tutorials/setup"
fi

# Initialize database
echo "Initializing font database..."
python3 << 'EOF'
import os
import json

data_dir = './data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)

db_path = os.path.join(data_dir, 'font_database.json')
if not os.path.exists(db_path):
    initial_db = {
        'version': '1.0.0',
        'last_updated': '2026-09-16',
        'fonts': []
    }
    with open(db_path, 'w') as f:
        json.dump(initial_db, f, indent=2)
    print("✓ Font database initialized")
else:
    print("✓ Font database already exists")

EOF

echo ""
echo "=============================================="
echo "✅ Setup Complete!"
echo "=============================================="
echo ""
echo "Starting Font Precision Recognizer..."
echo "🌐 Server will run on: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Run the application
python app.py
