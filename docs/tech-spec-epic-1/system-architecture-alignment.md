# System Architecture Alignment

This epic implements the core architecture defined in `solution-architecture.md`:

**Architectural Pattern**: Modular Monolith with logical service boundaries (query_service, llm_service, validation_service)

**Repository Strategy**: Monorepo structure with `/frontend` and `/backend` directories

**Key Architectural Components Implemented**:
- **Frontend Layer**: React 18.3.1 + Tailwind CSS 3.4.1 + Vite 5.0.0 (ADR-001)
- **Backend Layer**: FastAPI 0.109.0 + Python 3.11+ with async support
- **Data Layer**: PostgreSQL 15+ (Railway managed) with SQLAlchemy 2.0.25 ORM (ADR-003)
- **LLM Integration**: OpenAI GPT-4o-mini via official Python SDK 1.10.0 (ADR-005)
- **Security Layer**: Multi-layered approach (DB permissions + prompt engineering + input sanitization + SQL validation)
- **Deployment**: Docker Compose for local dev, Railway for production (ADR-002, ADR-004)

**Constraints Adhered To**:
- Single-service deployment (FastAPI serves both API and React static files)
- Read-only database connection (`query_app_readonly` user)
- Maximum 500 character query length
- 5-second response time target (NFR002)
