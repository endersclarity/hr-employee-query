# Component Architecture

### Frontend Components (React + Tailwind)

**Component Hierarchy:**
```
App
├── QueryInterface
│   ├── QueryInput (textarea + submit button)
│   ├── LoadingSpinner
│   └── ErrorDisplay
├── ResultsTable (data table with columns)
├── RagasScoreDisplay
│   ├── ScoreBadge (Faithfulness)
│   ├── ScoreBadge (Answer Relevance)
│   └── ScoreBadge (Context Precision)
└── GeneratedSQLDisplay (optional, collapsible)
```

**State Management:** React useState (no Redux needed for simple app)
- `query`: string (user input)
- `results`: array (query results)
- `ragasScores`: object (evaluation metrics)
- `loading`: boolean
- `error`: string | null
- `generatedSQL`: string (for transparency)

**Why Simple State?**
For a single-page app with minimal state, React's built-in useState is sufficient. Redux/Zustand would be overkill and add unnecessary complexity.

---

### Backend Modules (FastAPI)

**Module Structure:**
```
backend/
├── app/
│   ├── main.py (FastAPI app initialization, static serving)
│   ├── api/ (API routes)
│   │   ├── __init__.py
│   │   ├── routes.py (POST /api/query, GET /api/health)
│   │   └── models.py (Pydantic request/response models)
│   ├── services/ (Business logic)
│   │   ├── __init__.py
│   │   ├── query_service.py (orchestrates NL→SQL→Results flow)
│   │   ├── llm_service.py (OpenAI integration)
│   │   ├── ragas_service.py (evaluation metrics)
│   │   └── validation_service.py (SQL validation, security)
│   ├── db/ (Database layer)
│   │   ├── __init__.py
│   │   ├── models.py (SQLAlchemy ORM models)
│   │   ├── session.py (database connection)
│   │   └── seed.py (mock data generation)
│   ├── config.py (settings via Pydantic BaseSettings)
│   └── utils/
│       ├── __init__.py
│       └── logger.py (structured logging setup)
```

**Service Responsibilities:**

1. **query_service.py** - Main orchestrator
   - Receives natural language query
   - Calls llm_service for SQL generation
   - Calls validation_service for security check
   - Executes SQL via db layer
   - Calls ragas_service for evaluation
   - Returns combined response

2. **llm_service.py** - LLM integration
   - Schema-aware system prompt
   - Few-shot examples for reliability
   - Async OpenAI API calls
   - Error handling (rate limits, API failures)

3. **ragas_service.py** - Evaluation
   - Calculate Faithfulness (schema consistency)
   - Calculate Answer Relevance (intent alignment)
   - Calculate Context Precision (field selection)
   - Return scores 0.6-1.0 scale

4. **validation_service.py** - Security layer
   - Parse SQL with sqlparse
   - Whitelist SELECT only (block DELETE, DROP, UPDATE, INSERT)
   - Detect SQL injection patterns
   - Raise exceptions for malicious queries

---
