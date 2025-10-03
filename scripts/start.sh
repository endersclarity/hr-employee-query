#!/bin/bash
# Database initialization and startup script
# Executes in strict order: migrations → read-only user → seed → server

set -e  # Exit on any error

echo "🚀 Starting HR Query API initialization..."

# Step 1: Run database migrations
echo "📋 Step 1/4: Running Alembic migrations..."
cd /app
alembic upgrade head
echo "✅ Migrations completed"

# Step 2: Create read-only user (idempotent)
echo "👤 Step 2/4: Creating read-only database user..."
# Set password from environment variable, default if not set
READONLY_PASSWORD=${READONLY_DB_PASSWORD:-readonly_secure_pass_2025}
psql "$DATABASE_URL" -v ON_ERROR_STOP=1 -c "SET app.readonly_password = '$READONLY_PASSWORD';" -f app/db/create_readonly_user.sql
echo "✅ Read-only user configured"

# Step 3: Seed database (only if empty)
echo "🌱 Step 3/4: Seeding database..."
python -m app.db.seed
echo "✅ Database seeding completed"

# Step 4: Start FastAPI server
echo "🌐 Step 4/4: Starting uvicorn server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
