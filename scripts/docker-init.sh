#!/bin/bash

# Docker initialization script
# This script initializes the database and sets up the application in Docker

echo "🐳 Docker Initialization Script"
echo "================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f .env.template ]; then
        cp .env.template .env
        echo "✅ Created .env file. Please edit it and add your API keys."
    else
        echo "❌ .env.template not found. Please create .env manually."
        exit 1
    fi
fi

# Create data directory if it doesn't exist
mkdir -p data

# Build Docker images
echo ""
echo "📦 Building Docker images..."
docker-compose build

# Start services
echo ""
echo "🚀 Starting services..."
docker-compose up -d

# Wait for backend to be healthy
echo ""
echo "⏳ Waiting for backend to be ready..."
timeout=60
counter=0
while [ $counter -lt $timeout ]; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done

if [ $counter -ge $timeout ]; then
    echo ""
    echo "⚠️  Backend took too long to start. Check logs with: docker-compose logs backend"
else
    # Initialize database
    echo ""
    echo "💾 Initializing database..."
    docker-compose exec -T backend python scripts/init_database.py
    
    echo ""
    echo "✅ Setup complete!"
    echo ""
    echo "Services are running:"
    echo "  - Backend:  http://localhost:8000"
    echo "  - Frontend: http://localhost:3000"
    echo "  - API Docs: http://localhost:8000/docs"
    echo ""
    echo "Useful commands:"
    echo "  make logs          # View logs"
    echo "  make down          # Stop services"
    echo "  make restart       # Restart services"
fi

