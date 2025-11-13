# Frontend Docker Setup

This document explains how to run the Next.js frontend application using Docker.

## Quick Start

### Running with Docker Compose (Recommended)

The frontend is now integrated into the main docker-compose.yml file.

**Start all services including the frontend:**

```bash
docker-compose up -d
```

**Start only the frontend and its dependencies (API):**

```bash
docker-compose up -d frontend
```

The frontend will be available at [http://localhost:3000](http://localhost:3000)

### Running Frontend Standalone

If you want to run just the frontend container:

```bash
# Build the image
docker build -t reddit-frontend ./frontend

# Run the container
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  reddit-frontend
```

## Docker Configuration

### Dockerfile

The frontend uses a **multi-stage build** for optimal image size and security:

1. **deps stage**: Installs production dependencies
2. **builder stage**: Builds the Next.js application
3. **runner stage**: Creates minimal runtime image with only necessary files

Key features:
- Based on `node:18-alpine` for small image size
- Runs as non-root user (`nextjs`) for security
- Uses Next.js standalone output for minimal runtime
- Includes only production dependencies

### Docker Compose Service

The frontend service in [docker-compose.yml](docker-compose.yml):

```yaml
frontend:
  build:
    context: ./frontend
    dockerfile: Dockerfile
    args:
      NEXT_PUBLIC_API_URL: http://localhost:8000
  container_name: reddit-frontend
  environment:
    NEXT_PUBLIC_API_URL: http://localhost:8000
  ports:
    - "3000:3000"
  depends_on:
    - api
  restart: unless-stopped
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL accessible from browser | `http://localhost:8000` |

**Important Notes:**
- `NEXT_PUBLIC_API_URL` must be set at **build time** as a build arg
- It's also set as a runtime environment variable
- This URL must be accessible from the **user's browser**, not just from the container

### Network Configuration

When running in Docker Compose:
- The frontend connects to the API via the service name `api` internally
- Users access the API via `http://localhost:8000` from their browser
- All services are on the same Docker network

## Usage

### Starting the Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f frontend

# Check status
docker-compose ps
```

### Stopping the Services

```bash
# Stop all services
docker-compose down

# Stop only frontend
docker-compose stop frontend
```

### Rebuilding After Changes

If you make changes to the frontend code:

```bash
# Rebuild and restart
docker-compose up -d --build frontend

# Or rebuild without cache
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Accessing the Application

- **Frontend UI**: [http://localhost:3000](http://localhost:3000)
- **API Backend**: [http://localhost:8000](http://localhost:8000)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

## Development vs Production

### Development Mode (Local)

For active development, use npm directly instead of Docker:

```bash
cd frontend
npm install
npm run dev
```

Benefits:
- Hot reload
- Faster rebuild times
- Direct file system access
- Better debugging experience

### Production Mode (Docker)

Use Docker for production-like testing and deployment:

```bash
docker-compose up -d
```

Benefits:
- Consistent environment
- Optimized builds
- Security hardening
- Easy deployment

## Troubleshooting

### Frontend can't connect to API

**Issue**: Frontend shows "Failed to fetch" errors

**Solutions**:
1. Check API is running: `docker-compose ps api`
2. Verify API health: `curl http://localhost:8000/health`
3. Check API logs: `docker-compose logs api`
4. Ensure CORS is enabled (already configured in API)

### Port 3000 already in use

**Solution**:
```bash
# Option 1: Stop the conflicting process
lsof -i :3000
kill -9 <PID>

# Option 2: Change the port in docker-compose.yml
ports:
  - "3001:3000"  # Map host port 3001 to container port 3000
```

### Build fails or is very slow

**Solutions**:
```bash
# Clear Docker cache
docker-compose build --no-cache frontend

# Prune unused Docker resources
docker system prune -a

# Check Docker disk space
docker system df
```

### Container keeps restarting

**Check logs**:
```bash
docker-compose logs frontend
```

**Common issues**:
- Build artifacts missing (rebuild with `--no-cache`)
- Port conflict
- Out of memory (check `docker stats`)

### Changes not reflecting

**Solution**:
```bash
# Rebuild with no cache
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Verify new image is running
docker-compose ps frontend
docker images | grep reddit-frontend
```

## Production Deployment

### Environment Variables for Production

Update the API URL for your production environment:

```yaml
# docker-compose.yml or docker-compose.prod.yml
frontend:
  build:
    args:
      NEXT_PUBLIC_API_URL: https://api.yourcompany.com
  environment:
    NEXT_PUBLIC_API_URL: https://api.yourcompany.com
```

### Security Considerations

1. **Always use HTTPS in production**
2. **Set proper CORS origins in the API**
3. **Use environment-specific configs**
4. **Keep base images updated**
5. **Scan for vulnerabilities**: `docker scan reddit-frontend`

### Performance Optimization

The Dockerfile is already optimized with:
- Multi-stage builds (smaller image)
- Next.js standalone output (minimal dependencies)
- Alpine Linux base (reduced attack surface)
- Non-root user (security)

### Monitoring

```bash
# View resource usage
docker stats reddit-frontend

# View real-time logs
docker-compose logs -f frontend

# Check container health
docker inspect reddit-frontend --format='{{.State.Health.Status}}'
```

## Image Size

Expected image sizes:
- **Development build**: ~500MB
- **Production build**: ~150-200MB (with standalone mode)

Check your image size:
```bash
docker images reddit-frontend
```

## Advanced Configuration

### Custom Port Mapping

```yaml
# docker-compose.yml
frontend:
  ports:
    - "8080:3000"  # Access at http://localhost:8080
```

### Resource Limits

```yaml
# docker-compose.yml
frontend:
  deploy:
    resources:
      limits:
        memory: 512M
        cpus: '0.5'
      reservations:
        memory: 256M
```

### Volume Mounts for Development

If you want hot-reload in Docker (not recommended, use npm dev instead):

```yaml
frontend:
  volumes:
    - ./frontend:/app
    - /app/node_modules
    - /app/.next
```

## CI/CD Integration

### Building for CI/CD

```bash
# Build with specific tag
docker build -t registry.example.com/reddit-frontend:v1.0.0 ./frontend

# Push to registry
docker push registry.example.com/reddit-frontend:v1.0.0
```

### GitHub Actions Example

```yaml
- name: Build and push frontend
  run: |
    docker build \
      --build-arg NEXT_PUBLIC_API_URL=${{ secrets.API_URL }} \
      -t ${{ secrets.REGISTRY }}/reddit-frontend:${{ github.sha }} \
      ./frontend
    docker push ${{ secrets.REGISTRY }}/reddit-frontend:${{ github.sha }}
```

## Summary

The frontend Docker setup provides:
- ✅ Production-ready containerization
- ✅ Multi-stage builds for optimization
- ✅ Security hardening with non-root user
- ✅ Easy integration with docker-compose
- ✅ Configurable via environment variables
- ✅ Minimal image size with standalone output

For development, use `npm run dev` directly.
For production and testing, use Docker with `docker-compose up`.
