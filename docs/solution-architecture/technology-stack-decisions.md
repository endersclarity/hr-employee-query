# Technology Stack & Decisions

| Category | Technology | Version | Rationale |
|----------|-----------|---------|-----------|
| **Frontend Framework** | React | 18.3.1 | Industry-standard UI library, excellent ecosystem, component-based architecture suitable for simple interfaces |
| **Frontend Styling** | Tailwind CSS | 3.4.1 | Utility-first CSS framework, rapid development, no custom CSS needed, beginner-friendly |
| **Frontend Build Tool** | Vite | 5.0.0 | Modern build tool, fast HMR (Hot Module Replacement), better DX than Create React App |
| **Frontend HTTP Client** | Axios | 1.6.5 | Promise-based HTTP client, better error handling than fetch, interceptor support for logging |
| **Backend Framework** | FastAPI | 0.109.0 | Modern Python framework, automatic API documentation (OpenAPI), async support, type safety |
| **Backend Language** | Python | 3.11+ | Required for Ragas library, excellent LLM ecosystem, FastAPI support, beginner-friendly |
| **Database** | PostgreSQL | 15+ | Production-grade RDBMS, Railway managed service, better than SQLite for demo credibility |
| **Database ORM** | SQLAlchemy | 2.0.25 | Industry-standard Python ORM, type-safe queries, migration support via Alembic |
| **Database Migrations** | Alembic | 1.13.1 | Database migration tool for SQLAlchemy, version control for schema changes |
| **LLM Provider** | OpenAI | GPT-4o-mini | Cost-effective model, reliable NL→SQL conversion, structured output support |
| **LLM SDK** | OpenAI Python | 1.10.0 | Official SDK, async support, streaming capabilities, well-documented |
| **Evaluation Framework** | Ragas | 0.1.0+ | Purpose-built for RAG/LLM evaluation, Faithfulness/Relevance/Precision metrics |
| **Validation** | Pydantic | 2.5.3 | Data validation, settings management, integrates with FastAPI, type safety |
| **SQL Validation** | sqlparse | 0.4.4 | SQL parsing and validation, detect malicious queries, whitelist SELECT statements |
| **Logging** | structlog | 24.1.0 | Structured logging, JSON output, better than print() for production patterns |
| **Environment Config** | python-dotenv | 1.0.0 | Load environment variables from .env files, keeps secrets out of code |
| **CORS** | fastapi-cors | - | Built-in FastAPI CORS middleware (frontend-backend communication) |
| **Containerization** | Docker | 24.0+ | Container platform for consistent environments, required by assignment |
| **Container Orchestration** | Docker Compose | 2.23+ | Multi-container orchestration for local development (frontend + backend + DB) |
| **Deployment Platform** | Railway | - | PaaS with PostgreSQL, Docker support, simple deployment, good for demos |
| **HTTP Server (Production)** | Uvicorn | 0.27.0 | ASGI server for FastAPI, production-ready, handles async requests |

**Total Dependencies:** ~15 production packages (lean stack, no bloat)

---
