# Deployment Architecture

### Railway Deployment Strategy

**Why Railway?**
- ✅ Built-in PostgreSQL (no separate DB management)
- ✅ Docker support (can deploy FastAPI container)
- ✅ Simple environment variable management
- ✅ GitHub integration for CI/CD
- ✅ Affordable for demos
- ✅ Single platform (simpler than Vercel + Railway)

**Deployment Components:**

```
Railway Project: hr-query-app
├── Service 1: FastAPI Backend
│   ├── Dockerfile: backend/Dockerfile
│   ├── Environment Variables:
│   │   - OPENAI_API_KEY (secret)
│   │   - DATABASE_URL (auto-provided by Railway)
│   │   - PYTHON_ENV=production
│   └── Exposed Port: 8000
│
└── Service 2: PostgreSQL Database
    ├── Provisioned by Railway
    ├── Automatic DATABASE_URL injection
    └── Backups enabled
```

**FastAPI serves React build:**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# API routes
app.include_router(api_router, prefix="/api")

# Serve React static files
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    """Serve React SPA for all non-API routes."""
    return FileResponse("frontend/dist/index.html")
```

**Environment Variables (Railway):**

```bash
# Set in Railway dashboard
OPENAI_API_KEY=sk-proj-xxxxx
DATABASE_URL=postgresql://user:pass@host:5432/db  # Auto-provided
PYTHON_ENV=production
ALLOWED_ORIGINS=https://hr-query-app.railway.app
```

**Build Process:**

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY ./backend/app ./app

# Copy frontend build (created in CI/CD before Docker build)
COPY ./frontend/dist ./frontend/dist

# Run migrations on startup (via startup script)
COPY ./scripts/start.sh .
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
```

**Startup Script:**

```bash
#!/bin/bash
# scripts/start.sh

# Run database migrations
alembic upgrade head

# Seed database with mock data (if empty)
python -m app.db.seed

# Start Uvicorn server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---
