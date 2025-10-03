# Dependencies and Integrations

### Python Backend Dependencies (`backend/requirements.txt`)

**Core Framework**:
```
fastapi==0.109.0          # Web framework
uvicorn[standard]==0.27.0 # ASGI server
pydantic==2.5.3           # Data validation
python-dotenv==1.0.0      # Environment variables
```

**Database**:
```
sqlalchemy==2.0.25        # ORM
psycopg2-binary==2.9.9    # PostgreSQL driver
alembic==1.13.1           # Database migrations
```

**LLM Integration**:
```
openai==1.10.0            # OpenAI SDK
```

**Security & Validation**:
```
sqlparse==0.4.4           # SQL parsing and validation
```

**Logging**:
```
structlog==24.1.0         # Structured logging
```

**CORS**:
```
# fastapi-cors (built-in to FastAPI, no separate install)
```

**Total**: ~10 production dependencies

### Frontend Dependencies (`frontend/package.json`)

**Core Framework**:
```json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "axios": "^1.6.5"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.1",
    "@vitejs/plugin-react": "^4.2.1",
    "postcss": "^8.4.33",
    "autoprefixer": "^10.4.16"
  }
}
```

**Total**: 3 runtime dependencies, 5 dev dependencies

### External Service Integrations

| Service | Purpose | API Version | Authentication | Rate Limits |
|---------|---------|-------------|----------------|-------------|
| **OpenAI API** | NL→SQL generation | GPT-4o-mini | API Key (env var) | 500 RPM (free tier), 10,000 RPM (paid) |
| **Railway PostgreSQL** | Managed database | PostgreSQL 15+ | Auto-injected `DATABASE_URL` | No explicit limit (managed service) |
| **Railway Platform** | Deployment & hosting | - | GitHub OAuth | Free tier: 500 hours/month |

### Configuration Requirements

**Environment Variables** (`.env` for local, Railway secrets for production):
```bash
# Required
OPENAI_API_KEY=sk-proj-xxxxx                    # OpenAI API key
DATABASE_URL=postgresql://user:pass@host:5432/db # Auto-provided by Railway

# Optional
PYTHON_ENV=development|production               # Environment mode
ALLOWED_ORIGINS=http://localhost:5173           # CORS origins (comma-separated)
LOG_LEVEL=INFO                                  # Logging verbosity
```

### Integration Points Summary

1. **Frontend ↔ Backend**: REST API over HTTP/HTTPS
2. **Backend ↔ OpenAI**: HTTPS API calls to `https://api.openai.com/v1/chat/completions`
3. **Backend ↔ PostgreSQL**: TCP connection via SQLAlchemy (read-only user)
4. **Development ↔ Docker**: Docker Compose orchestration for local services
