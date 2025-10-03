# Implementation Guidance

### Development Phases (Aligned with Epics)

**Phase 1: Epic 1 - Core Application (Stories 1.1-1.8)**

**Week 1: Foundation**
- Set up monorepo structure
- Docker Compose configuration
- PostgreSQL setup with migrations
- Mock data seed script

**Week 2: Backend Core**
- FastAPI app skeleton
- Database models (SQLAlchemy)
- LLM integration (OpenAI)
- SQL validation service

**Week 3: Frontend + Integration**
- React + Tailwind UI
- API client (Axios)
- End-to-end query flow
- Error handling

**Phase 2: Epic 2 - Ragas Evaluation (Stories 2.1-2.4)**

**Week 4: Evaluation Framework**
- Ragas integration
- Metrics calculation
- Frontend score display
- Comparative reporting

**Phase 3: Deployment & Polish**

**Week 5: Deployment**
- Railway setup
- Environment variables
- Production build testing
- Demo rehearsal

**Week 6: Documentation & Presentation**
- README finalization
- Project Report
- Architecture diagrams
- Demo script preparation

---

### Key Implementation Notes

**1. Schema-Aware Prompting (Critical for Ragas Faithfulness)**

Include full schema in system prompt:
```python
SCHEMA_PROMPT = """
Table: employees
Columns:
  - employee_id: Integer, Primary Key
  - first_name: String (100 chars max)
  - last_name: String (100 chars max)
  - department: String (100 chars max)
  - role: String (100 chars max)
  - employment_status: String ('Active', 'Terminated', 'On Leave')
  - hire_date: Date
  - leave_type: String (nullable, 'Parental Leave', 'Medical Leave', 'Sick Leave')
  - salary_local: Decimal (12,2)
  - salary_usd: Decimal (12,2)
  - manager_name: String (nullable, 200 chars max)
"""
```

**2. Few-Shot Examples (Boosts Reliability)**

```python
FEW_SHOT_EXAMPLES = """
Example 1:
Query: "Show me employees hired in the last 6 months"
SQL: SELECT * FROM employees WHERE hire_date >= CURRENT_DATE - INTERVAL '6 months'

Example 2:
Query: "List Engineering employees with salary over 120K"
SQL: SELECT * FROM employees WHERE department = 'Engineering' AND salary_usd > 120000

Example 3:
Query: "Who is on parental leave?"
SQL: SELECT * FROM employees WHERE leave_type = 'Parental Leave'

Example 4:
Query: "Show employees managed by John Doe"
SQL: SELECT * FROM employees WHERE manager_name = 'John Doe'
"""
```

**3. Error Handling Pattern**

```python
from fastapi import HTTPException

try:
    # Service call
    result = await query_service.execute(query)
except ValidationError as e:
    raise HTTPException(status_code=400, detail=str(e))
except LLMError as e:
    raise HTTPException(status_code=500, detail="LLM service unavailable")
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Database query failed")
```

**4. Logging Best Practice**

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "query_executed",
    query=nl_query,
    generated_sql=sql,
    result_count=len(results),
    faithfulness_score=scores['faithfulness']
)
```

**5. Frontend API Client**

```javascript
// src/services/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

export const executeQuery = async (query) => {
  try {
    const response = await api.post('/query', { query });
    return response.data;
  } catch (error) {
    if (error.response?.data?.error) {
      throw new Error(error.response.data.error);
    }
    throw new Error('Failed to execute query');
  }
};
```

---
