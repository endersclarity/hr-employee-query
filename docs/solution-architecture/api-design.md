# API Design

### REST API Endpoints

**Base URL:** `https://your-app.railway.app/api`

#### POST /api/query

**Purpose:** Execute natural language query and return results with Ragas scores

**Request:**
```json
{
  "query": "Show me employees in Engineering with salary greater than 120K"
}
```

**Response (Success - 200):**
```json
{
  "success": true,
  "query": "Show me employees in Engineering with salary greater than 120K",
  "generated_sql": "SELECT employee_id, first_name, last_name, department, salary_usd FROM employees WHERE department = 'Engineering' AND salary_usd > 120000",
  "results": [
    {
      "employee_id": 42,
      "first_name": "Alice",
      "last_name": "Johnson",
      "department": "Engineering",
      "salary_usd": 135000.00
    },
    {
      "employee_id": 73,
      "first_name": "Bob",
      "last_name": "Smith",
      "department": "Engineering",
      "salary_usd": 142000.00
    }
  ],
  "ragas_scores": {
    "faithfulness": 0.92,
    "answer_relevance": 0.88,
    "context_precision": 0.85
  },
  "result_count": 2,
  "execution_time_ms": 1243
}
```

**Response (Validation Error - 400):**
```json
{
  "success": false,
  "error": "Query validation failed: Only SELECT queries are permitted",
  "error_type": "VALIDATION_ERROR"
}
```

**Response (LLM Error - 500):**
```json
{
  "success": false,
  "error": "Failed to generate SQL from natural language query",
  "error_type": "LLM_ERROR"
}
```

#### GET /api/health

**Purpose:** Health check endpoint for monitoring

**Response (200):**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-10-01T14:30:00Z"
}
```

---
