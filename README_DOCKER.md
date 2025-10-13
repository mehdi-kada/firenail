# Docker Setup for ThumbnailAI

This Docker configuration runs all ThumbnailAI services including Next.js frontend, FastAPI backend, Celery workers, and Redis.

## Services

- **Frontend**: Next.js application (port 3000)
- **Backend**: FastAPI application (port 8000)
- **Redis**: Database and message broker (port 6379)
- **Celery Worker**: Background task processor
- **Flower**: Celery monitoring dashboard (port 5555)

## Quick Start

### Production Setup

1. Create environment file:
```bash
cp .env.docker .env
```

2. Run all services:
```bash
docker-compose up --build
```

### Development Setup

For development with hot reload:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

## Environment Variables

All environment variables are defined in `.env.docker`. Make sure to:

1. Copy the file to `.env`:
```bash
cp .env.docker .env
```

2. Update any API keys or configuration values as needed

## Service URLs

Once running, you can access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs
- Celery Flower: http://localhost:5555
- Redis: localhost:6379

## Development Commands

### Build and run all services
```bash
docker-compose up --build
```

### Run in detached mode
```bash
docker-compose up -d --build
```

### View logs
```bash
docker-compose logs -f
```

### View specific service logs
```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker
```

### Stop all services
```bash
docker-compose down
```

### Stop and remove volumes
```bash
docker-compose down -v
```

## Development Workflow

### Backend Development
- Make changes to backend code
- Changes are automatically reloaded in development mode
- Logs show in real-time with `docker-compose logs -f backend`

### Frontend Development
- Make changes to frontend code
- Next.js hot reloads the application
- Access development server at http://localhost:3000

### Background Tasks
- Celery workers process tasks from the queue
- Monitor task progress at http://localhost:5555 (Flower)
- Worker logs available with `docker-compose logs -f celery_worker`

## Troubleshooting

1. **Port conflicts**: Ensure ports 3000, 8000, 6379, and 5555 are available

2. **Build failures**: Check that all required files are present and environment variables are set correctly

3. **Permission issues**: Volume mounting may require proper permissions

4. **Redis connection**: Ensure Redis is healthy before starting other services

## Service Dependencies

- Backend and Celery workers depend on Redis
- Frontend depends on backend
- Flower depends on Redis

The Docker Compose configuration ensures proper startup order with health checks.
