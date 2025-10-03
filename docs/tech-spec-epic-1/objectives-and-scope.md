# Objectives and Scope

### Objectives
1. **Deliver Core User Functionality**: Enable HR professionals to query employee data using natural language without SQL knowledge
2. **Demonstrate Multi-Layered Security**: Implement database-level permissions, prompt engineering safeguards, input sanitization, and SQL validation
3. **Establish Production-Quality Patterns**: Create modular, maintainable code architecture suitable for job interview demonstration
4. **Support Mandatory Query Types**: Handle all 4 required query patterns (date range, department+salary, leave type, manager name)

### In-Scope (Epic 1)
- ✅ React frontend with query input, submit button, and results table display
- ✅ FastAPI backend with REST API (`POST /api/query`, `GET /api/health`)
- ✅ PostgreSQL database with employee schema and 50+ mock records
- ✅ OpenAI GPT-4o-mini integration for NL→SQL conversion with schema-aware prompting
- ✅ SQL validation layer (whitelist SELECT, block malicious operations)
- ✅ Read-only database connection for security
- ✅ Error handling and user feedback for failed queries
- ✅ Docker Compose for local development
- ✅ Basic logging (structured logs via structlog)

### Out-of-Scope (Epic 1)
- ❌ Ragas evaluation metrics (handled in Epic 2)
- ❌ Comparative reporting and recommendations (Epic 2)
- ❌ User authentication/authorization (beyond MVP)
- ❌ Query history persistence across sessions (beyond MVP)
- ❌ Advanced visualizations (charts/graphs)
- ❌ Multi-tenant architecture
