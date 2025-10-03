# Architecture Decision Records

### ADR-001: Monolith vs Microservices

**Decision:** Modular Monolith

**Context:** Level 2 project, solo developer, demo/interview context

**Rationale:**
- ✅ Simpler deployment (one container)
- ✅ No distributed systems complexity
- ✅ Easier debugging
- ✅ Faster development
- ✅ Appropriate for project scope (12 stories)
- ❌ Less scalable (but not needed for demo)

**Consequences:**
- Single point of failure (acceptable for demo)
- All services deploy together (simpler CI/CD)

---

### ADR-002: Railway for Deployment

**Decision:** Railway (single platform)

**Context:** Need Docker support, PostgreSQL, and simple deployment

**Alternatives Considered:**
- Vercel + Railway (more complex, CDN unnecessary for demo)
- Heroku (more expensive)
- AWS (overkill, steep learning curve for beginner)

**Rationale:**
- ✅ Built-in PostgreSQL
- ✅ Docker support
- ✅ Simple deployment (git push)
- ✅ Affordable ($5-10/month for demo)
- ✅ Good for interview demonstration

---

### ADR-003: PostgreSQL vs SQLite

**Decision:** PostgreSQL (Railway managed)

**Context:** Database choice for demo application

**Rationale:**
- ✅ More production-like (better for interview impression)
- ✅ Railway provides managed instance
- ✅ Better showcase of real-world patterns
- ✅ SQL features (indexes, constraints) work better
- ❌ Slightly more complex than SQLite (but Railway handles it)

**Consequences:**
- More impressive for technical interview
- Managed by Railway (no manual DB management)

---

### ADR-004: FastAPI Serves React Build

**Decision:** Single service serves both API and static files

**Context:** Deployment simplification

**Alternatives:**
- Separate Vercel (frontend) + Railway (backend)
- Two Railway services

**Rationale:**
- ✅ Simpler deployment (one service)
- ✅ No CORS issues (same origin)
- ✅ Fewer environment variables
- ✅ Easier demo day troubleshooting
- ❌ No CDN benefits (but unnecessary for demo)

---

### ADR-005: OpenAI GPT-4o-mini vs Claude

**Decision:** OpenAI GPT-4o-mini

**Context:** LLM provider selection

**Rationale:**
- ✅ Preference stated by user
- ✅ Cost-effective ($0.150 per 1M input tokens)
- ✅ Reliable for NL→SQL
- ✅ Structured output support
- ✅ Well-documented Python SDK

**Consequences:**
- OpenAI API key required
- Cost ~$0.01 per demo session (very cheap)

---
