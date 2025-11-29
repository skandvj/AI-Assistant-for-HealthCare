# Docker Setup Guide

This guide explains how to run the Dental Chatbot using Docker.

## Prerequisites

- Docker Desktop installed and running
- Docker Compose (included with Docker Desktop)
- `.env` file configured with API keys

## Quick Start

### Automated Setup (Recommended)

```bash
# Run the initialization script
./scripts/docker-init.sh
```

This script will:
- Check Docker is running
- Create .env from template if needed
- Build Docker images
- Start all services
- Initialize the database
- Verify everything is working

### Manual Setup

### Production Build

```bash
# Build and start all services
docker-compose up -d

# Initialize database (first time only)
docker-compose exec backend python scripts/init_database.py

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Development Build (with hot reload)

```bash
# Build and start with hot reload
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

## Services

### Backend (FastAPI)
- **Port:** 8000
- **Health Check:** http://localhost:8000/api/health
- **API Docs:** http://localhost:8000/docs

### Frontend (Next.js)
- **Port:** 3000
- **URL:** http://localhost:3000

## Environment Variables

Create a `.env` file in the project root with:

```env
DEEPSEEK_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here (optional)
```

The `.env` file is mounted as read-only in the container.

## Data Persistence

The `data/` directory is mounted as a volume, so your database persists between container restarts.

## Building Individual Services

### Backend Only

```bash
docker build -t dental-chatbot-backend .
docker run -p 8000:8000 --env-file .env dental-chatbot-backend
```

### Frontend Only

```bash
docker build -f frontend/Dockerfile -t dental-chatbot-frontend .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 dental-chatbot-frontend
```

## Useful Commands

```bash
# View running containers
docker-compose ps

# View logs for specific service
docker-compose logs backend
docker-compose logs frontend

# Restart a service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build

# Execute command in container
docker-compose exec backend python scripts/init_database.py

# Remove everything (including volumes)
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If ports 8000 or 3000 are already in use, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "8001:8000"  # Change host port
```

### Environment Variables Not Loading

Ensure your `.env` file is in the project root and contains the required variables.

### Database Not Persisting

Check that the `data/` directory exists and is writable. The volume mount should preserve data between restarts.

### Frontend Can't Connect to Backend

In production, ensure `NEXT_PUBLIC_API_URL` points to the backend service name or external URL.

For local development with Docker:
- Use `http://backend:8000` for inter-container communication
- Use `http://localhost:8000` for browser access

## Production Deployment

For production, consider:

1. **Use environment-specific compose files:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

2. **Add reverse proxy (nginx/traefik):**
   - Handle SSL/TLS
   - Route traffic
   - Load balancing

3. **Use managed database:**
   - Replace JSON file with PostgreSQL/Supabase
   - Update connection strings

4. **Add monitoring:**
   - Health checks (already included)
   - Log aggregation
   - Metrics collection

## Multi-Architecture Build

To build for different architectures:

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t dental-chatbot-backend .
```

## Security Notes

- Never commit `.env` files
- Use Docker secrets for sensitive data in production
- Keep base images updated
- Run containers as non-root user (already configured for frontend)

