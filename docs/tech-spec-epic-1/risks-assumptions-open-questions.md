# Risks, Assumptions, Open Questions

### Risks

**RISK-1: OpenAI API Reliability**
- **Description**: OpenAI API downtime or rate limiting could block demo
- **Probability**: Medium (occasional outages, rate limits on free tier)
- **Impact**: High (core functionality unavailable)
- **Mitigation**:
  - Implement retry logic with exponential backoff (3 attempts)
  - Prepare backup demo video in case of API failure on Oct 12
  - Use paid OpenAI tier for higher rate limits (10,000 RPM vs 500 RPM)
  - Cache successful query→SQL mappings for common queries (future enhancement)

**RISK-2: LLM Generates Invalid SQL**
- **Description**: GPT-4o-mini may generate syntactically invalid or semantically incorrect SQL for edge-case queries
- **Probability**: Medium (LLMs are probabilistic)
- **Impact**: Medium (query fails, but user can retry)
- **Mitigation**:
  - Validation layer catches syntax errors before execution
  - Few-shot examples improve reliability for common patterns
  - Test with diverse queries during development
  - Display generated SQL to user for transparency (build trust)

**RISK-3: Railway Deployment Issues**
- **Description**: Railway service crashes, database connection issues, or deployment failures on demo day
- **Probability**: Low (Railway is stable platform)
- **Impact**: Critical (no live demo possible)
- **Mitigation**:
  - Deploy 48+ hours before demo to identify issues early
  - Test health check endpoint before demo
  - Have local `docker-compose` environment as backup
  - Prepare screenshots/video as last resort

**RISK-4: Performance Degradation**
- **Description**: Response time exceeds 5s target, especially for complex queries or during high load
- **Probability**: Low (single-user demo, optimized indexes)
- **Impact**: Medium (poor user experience, interview impression)
- **Mitigation**:
  - Database indexes on frequently queried columns
  - Result limiting (max 1000 rows)
  - Async processing (FastAPI + OpenAI async client)
  - Load test before demo to establish baseline

**RISK-5: Integration Point Failures** (NEW - from Dependency Analysis)
- **Description**: Critical integration gaps cause cascade failures (CORS misconfiguration → frontend blocked; missing static file serving → production 404s; env var missing → service crashes)
- **Probability**: Medium (7 integration points identified, each has failure mode)
- **Impact**: High (single point of failure can break entire demo)
- **Mitigation**:
  - Implement all 7 integration points with explicit code (not assumptions)
  - Add integration tests for each point (CORS, static files, env vars, timeouts)
  - Test complete dependency chain: 1.1 → 1.2 → 1.4 → 1.5 → 1.6 → 1.7 → 1.8
  - Create smoke test script that validates all integration points before demo

### Assumptions

**ASSUMPTION-1: Database Size**
- **Assumption**: 50-100 employee records sufficient for demo
- **Validation**: Confirmed in PRD Story 1.2 (mock data requirements)
- **If False**: Easy to scale seed script to generate more records

**ASSUMPTION-2: OpenAI API Key Availability**
- **Assumption**: User (Kaelen) has valid OpenAI API key with sufficient credits
- **Validation**: Required for development; confirm before Epic 1 start
- **If False**: Use Anthropic Claude API as alternative (requires code changes to llm_service.py)

**ASSUMPTION-3: Single-User Demo**
- **Assumption**: No concurrent user load testing required (job interview demo context)
- **Validation**: Confirmed in PRD deployment intent
- **If False**: Add rate limiting, load balancing (beyond MVP scope)

**ASSUMPTION-4: No Authentication Required**
- **Assumption**: Public access to demo app is acceptable (no login/auth)
- **Validation**: Confirmed in PRD out-of-scope section
- **If False**: Add basic auth middleware (1-2 days effort)

### Open Questions

**QUESTION-1: Schema Prompt Strategy**
- **Question**: Should we include full schema with all 11 columns in LLM prompt, or only relevant columns per query?
- **Options**: (A) Full schema always, (B) Dynamic schema based on query intent
- **Decision Needed By**: Story 1.5 (LLM Integration)
- **Recommendation**: Start with full schema (simpler), optimize later if needed

**QUESTION-2: Generated SQL Display**
- **Question**: Should generated SQL be always visible, hidden by default (toggle), or developer-only?
- **Options**: (A) Always visible, (B) Expandable toggle, (C) Hidden in production
- **Decision Needed By**: Story 1.8 (Frontend Integration)
- **Recommendation**: Expandable toggle (transparency + clean UI)

**QUESTION-3: Result Set Limiting**
- **Question**: What's the max number of rows to return (prevent huge payloads)?
- **Options**: (A) 100 rows, (B) 500 rows, (C) 1000 rows, (D) Unlimited
- **Decision Needed By**: Story 1.7 (SQL Execution)
- **Recommendation**: 1000 rows (reasonable for demo, prevents abuse)

**QUESTION-4: Error Logging Detail**
- **Question**: Should we log full error stack traces or sanitized error messages?
- **Options**: (A) Full stack traces, (B) Sanitized messages only
- **Decision Needed By**: Story 1.4 (Backend setup)
- **Recommendation**: Full stack traces in development, sanitized in production (use `PYTHON_ENV` env var)
