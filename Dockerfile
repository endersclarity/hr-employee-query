# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install --production=false

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Stage 2: Python backend with frontend
FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck, postgresql-client for database operations, and bash
RUN apt-get update && apt-get install -y curl postgresql-client bash && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Copy built frontend from stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

EXPOSE 8000

# Multi-stage startup: migrations (critical) -> seed (optional) -> server
CMD ["sh", "-c", "\
    echo '=== Starting deployment ===' && \
    echo 'Waiting for database...' && sleep 3 && \
    echo 'Running migrations...' && alembic upgrade head && \
    echo 'Migrations complete. Running seed...' && \
    (python -m app.db.seed || echo 'WARNING: Seed failed or skipped') && \
    echo 'Starting application server...' && \
    uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
