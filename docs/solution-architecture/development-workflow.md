# Development Workflow

### Local Development with Docker Compose

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: hr_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: localdevpassword
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: backend/Dockerfile.dev
    environment:
      DATABASE_URL: postgresql://postgres:localdevpassword@db:5432/hr_db
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      PYTHON_ENV: development
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app/backend
    depends_on:
      db:
        condition: service_healthy
    command: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      VITE_API_URL: http://localhost:8000/api
    command: npm run dev -- --host

volumes:
  postgres_data:
```

**Development Commands:**

```bash
# Start all services
docker-compose up

# Access services:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000/api
# - Backend Docs: http://localhost:8000/docs (FastAPI auto-generated)
# - Database: localhost:5432

# Stop services
docker-compose down

# Reset database
docker-compose down -v && docker-compose up
```

**Why Docker Compose for Local Dev?**
- ✅ Consistent environment across team members
- ✅ No "works on my machine" issues
- ✅ PostgreSQL without manual installation
- ✅ Required by assignment deliverables

---
