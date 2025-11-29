#!/bin/bash

# Setup script for Dental Practice Chatbot

echo "🏥 Premium Dental Practice Chatbot - Setup"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version || { echo "Python 3.10+ required"; exit 1; }

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create data directory
echo ""
echo "Creating data directory..."
mkdir -p data

# Initialize database
echo ""
echo "Initializing database with sample data..."
python scripts/init_database.py

# Setup frontend
echo ""
echo "Setting up frontend..."
cd frontend
if [ ! -d "node_modules" ]; then
    npm install
fi
cd ..

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.template .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your LLM API key:"
    echo "   - DEEPSEEK_API_KEY (recommended - free tier)"
    echo "   - GOOGLE_API_KEY (alternative - free tier)"
    echo "   - OPENAI_API_KEY (alternative)"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Start backend: uvicorn main:app --reload"
echo "  3. In another terminal, start frontend: cd frontend && npm run dev"
echo ""
echo "Backend will run on http://localhost:8000"
echo "Frontend will run on http://localhost:3000"

