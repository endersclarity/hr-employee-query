# Executive Summary

This document defines the technical architecture for a full-stack web application that enables natural language querying of HR employee records. The system leverages OpenAI's LLM to convert natural language to SQL, executes queries securely, and evaluates results using the Ragas framework. Built as a job interview demonstration, the architecture emphasizes production-quality patterns, security, and systematic methodology while maintaining appropriate scope for a Level 2 project.

**Related Documentation:**
- Requirements: `docs/project-assignment.md`, `docs/PRD.md`
- Research: `docs/Research/Comprehensive Research Report_ Ragas Evaluation Fr.md`
- Planning: `docs/brainstorming-session-results-2025-10-01.md`, `docs/epic-stories.md`
- Classification: `docs/project-workflow-analysis.md`

**Key Architectural Decisions:**
- **Modular Monolith:** Single FastAPI application with logical module boundaries
- **Monorepo:** Frontend and backend in a single repository
- **Railway Deployment:** Unified platform for frontend, backend, and database
- **Docker-First Development:** Local development via docker-compose

**Target Audience:** This document is written for beginner-level full-stack developers, with detailed explanations and rationale for each decision.

---
