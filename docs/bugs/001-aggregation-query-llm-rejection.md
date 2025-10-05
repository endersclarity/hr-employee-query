# Bug Investigation: Aggregation Query LLM Rejection

**Bug ID**: 001
**Date Reported**: 2025-10-05
**Reported By**: Kaelen (Product Owner)
**Severity**: High
**Status**: Investigated - Solution Proposed
**Affected Component**: LLM Service (NL-to-SQL conversion)

---

## Summary

The "All departments" suggested query button consistently fails with error message: *"Query validation failed. Only SELECT queries are permitted."* This prevents users from executing a fundamental aggregation query that should work.

---

## User Impact

**Affected Queries:**
- "List all departments"
- "Show me all departments"
- "All departments" (button click)
- Any DISTINCT or GROUP BY aggregation queries

**Business Impact:**
- Suggested UI button is broken (trust erosion)
- Aggregation queries are completely non-functional
- Users cannot explore dataset structure (departments, roles, etc.)

---

## Investigation Timeline

### Initial Observation
User clicked "All departments" suggestion button → Query failed with validation error

### Hypothesis 1: SQL Validation Logic Too Restrictive
**Status**: ❌ Rejected
**Evidence**: Validation logic never executed - failure occurs before validation

### Hypothesis 2: LLM Generating Non-SELECT Query
**Status**: ❌ Rejected
**Evidence**: LLM returns `INVALID_REQUEST` rather than generating SQL

### Root Cause Identified: Missing Training Examples
**Status**: ✅ Confirmed
**Evidence**:
- LLM prompt contains 5 examples, NONE showing aggregation queries
- LLM conservatively returns `INVALID_REQUEST` when pattern doesn't match examples
- Test confirms: `generate_sql("List all departments")` → `ValueError("Query cannot be fulfilled with SELECT statement")`

---

## Technical Analysis

### Dependency Mapping

```
USER: "List all departments"
  ↓
FRONTEND: Sends query to /api/query
  ↓
QUERY SERVICE: execute_query()
  ↓ Step 1: sanitize_input() ✓
VALIDATION SERVICE: Returns "List all departments" (clean)
  ↓ Step 2: generate_sql()
LLM SERVICE: generate_sql()
  ├─ SYSTEM_PROMPT (lines 40-71 in llm_service.py)
  │  ├─ Employee schema ✓
  │  ├─ Security rules ✓
  │  └─ Examples (5 total):
  │      - WHERE clause filtering ✓
  │      - Date range queries ✓
  │      - Manager lookup ✓
  │      - ❌ NO aggregation queries (DISTINCT, GROUP BY, COUNT)
  │
  ├─ GPT-4o-mini API call
  └─ Returns: "INVALID_REQUEST" ❌
      ↓
  Raises ValueError (line 129)
      ↓ [STOPS - Validation never reached]
VALIDATION SERVICE: validate_sql() - NEVER CALLED
      ↓
QUERY SERVICE: Catches ValueError (line 156)
      ↓
Returns: QueryResponse(success=False, error_type="LLM_ERROR")
      ↓
FRONTEND: Displays confusing message
```

### Key Findings

1. **LLM Prompt Gap**: No examples of `SELECT DISTINCT` or `GROUP BY`
2. **Error Message Mismatch**:
   - Backend error: "Query cannot be fulfilled with SELECT statement" (technical, wrong)
   - Frontend display: "Query validation failed. Only SELECT queries are permitted." (misleading)
3. **Validation Bypass**: SQL validation logic never executes when LLM rejects query
4. **UI/Backend Misalignment**: Frontend suggests queries backend cannot handle

---

## Elicitation Results

### Methods Applied

**1. Dependency Mapping** - Revealed component interaction flow and identified validation bypass

**2. Tree of Thoughts** - Explored 4 solution paths:
- Path 1: Enhanced LLM Prompt (prompt engineering)
- Path 2: Fallback SQL Generation (pattern matching)
- Path 3: Multi-Stage Validation (retry logic)
- Path 4: Hybrid Approach (comprehensive fix)

**3. Self-Consistency Validation** - Compared 4 implementation approaches:
- Approach A: Sequential Fix (backend first)
- Approach B: Atomic Fix (all-at-once) ← **Recommended**
- Approach C: Defense-in-Depth (layered)
- Approach D: Minimal Viable Fix (single example)

**4. Challenge from Critical Perspective** - Identified 7 critical weaknesses:
- LLM unreliability for query variations
- Bad error messages made visible
- **BLOCKER**: Untested assumption LLM will learn
- Over-engineering concerns
- **STRATEGIC**: Wrong architecture (LLM for structured queries)
- **BLOCKER**: No testing strategy
- Static suggestions not data-driven

---

## Proposed Solution

### Recommended Approach: Modified Approach B (Atomic with Safety)

**Core Fix:**
1. Add 3-5 aggregation query examples to LLM SYSTEM_PROMPT
2. Fix frontend error display to show actual backend errors
3. Test locally with multiple query variations
4. Deploy backend + frontend atomically

**Priority Breakdown:**

#### HIGH PRIORITY (Implement Now)
```python
# backend/app/services/llm_service.py - Add to SYSTEM_PROMPT examples:

User: "List all departments"
SQL: SELECT DISTINCT department FROM employees ORDER BY department

User: "How many employees are in each department?"
SQL: SELECT department, COUNT(*) as employee_count FROM employees GROUP BY department ORDER BY department

User: "What are the unique roles in Engineering?"
SQL: SELECT DISTINCT role FROM employees WHERE department = 'Engineering' ORDER BY role
```

```javascript
// frontend - Fix error display (exact file TBD):
// Display actual backend error instead of hardcoded message
const errorMessage = response.error || "An error occurred"
```

#### MEDIUM PRIORITY (Nice to Have)
- Add 2-3 more aggregation examples (AVG, SUM, MAX/MIN)
- Enhance validation error messages with actionable hints
- Improve LLM error messages for better user guidance

#### LOW PRIORITY (Future Enhancement)
- Fallback pattern matching for common queries
- Multi-stage retry logic with enhanced context
- Query classification layer (structured vs. natural language)

---

## Critical Blockers Identified

### BLOCKER 1: Untested Fix
**Issue**: Assumption that adding examples will fix the issue is unvalidated
**Required**: Test `generate_sql("List all departments")` with new examples before deployment
**Risk**: Deploy broken fix, create new issues

### BLOCKER 2: No Testing Strategy
**Issue**: No unit tests, integration tests, or regression tests planned
**Required**:
- Unit test: LLM generates correct SQL for new examples
- Integration test: Full query flow works end-to-end
- Regression test: Existing queries still work
**Risk**: Break working functionality, no rollback validation

### BLOCKER 3: No Rollback Plan
**Issue**: If fix fails in production, no documented recovery procedure
**Required**:
- Git branch strategy
- Railway rollback procedure
- Feature flag consideration
**Risk**: Extended downtime if deployment fails

---

## Strategic Questions (Unresolved)

### Architecture Decision: LLM for Structured Queries?

**Challenge**: Using LLM for aggregation queries that could be simple API endpoints

**Alternative Approach:**
```javascript
// Dedicated endpoints for common queries
GET /api/departments → ["Engineering", "Marketing", ...]
GET /api/roles → ["Software Engineer", "Manager", ...]
GET /api/stats/employees-per-department → [{dept: "Eng", count: 15}, ...]
```

**Pros:**
- Zero latency (no LLM call)
- Zero cost (no API tokens)
- 100% reliable (deterministic)
- Cacheable responses

**Cons:**
- Doesn't scale to arbitrary queries
- Requires API endpoint for each pattern
- Loses natural language interface benefit

**Decision Required**:
- When should we use LLM vs. dedicated endpoints?
- Should we build query classifier (structured vs. NL)?
- What's the cost-benefit threshold for LLM usage?

---

## Testing Requirements

### Pre-Deployment Tests

**Unit Tests (backend/app/services/test_llm_service.py):**
```python
async def test_generate_sql_list_departments():
    """Test that 'List all departments' generates correct SQL."""
    sql = await generate_sql("List all departments")
    assert "SELECT DISTINCT department" in sql
    assert "FROM employees" in sql

async def test_generate_sql_count_per_department():
    """Test that count queries work."""
    sql = await generate_sql("How many employees in each department?")
    assert "COUNT(*)" in sql
    assert "GROUP BY department" in sql
```

**Integration Tests (backend/tests/integration/):**
```python
async def test_aggregation_query_flow():
    """Test full query flow for aggregation."""
    response = await client.post("/api/query",
        json={"query": "List all departments"})
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert len(response.json()["results"]) > 0
```

**Regression Tests:**
```python
async def test_existing_queries_still_work():
    """Ensure new examples don't break existing queries."""
    queries = [
        "Show me employees in Engineering with salary > 120K",
        "List employees hired in last 6 months",
        "Who is on parental leave?"
    ]
    for query in queries:
        response = await client.post("/api/query", json={"query": query})
        assert response.json()["success"] == True
```

### Production Validation

**Smoke Tests Post-Deploy:**
1. Click "All departments" button → Should return department list
2. Type "How many employees in Sales?" → Should return count
3. Test existing working query → Should still work
4. Check Railway logs for LLM errors → Should be zero for test queries

**Monitoring:**
- Track LLM error rate (target: <5% of queries)
- Monitor INVALID_REQUEST frequency
- Measure query latency (should be <2s p95)

---

## Implementation Checklist

### Code Changes
- [ ] Update `backend/app/services/llm_service.py` SYSTEM_PROMPT with 3-5 aggregation examples
- [ ] Update frontend error display component (file TBD)
- [ ] Write unit tests for new LLM examples
- [ ] Write integration test for aggregation query flow
- [ ] Write regression tests for existing queries

### Validation
- [ ] Test locally: `generate_sql("List all departments")` returns valid SQL
- [ ] Test locally: Full query flow returns results
- [ ] Test locally: Existing queries still work
- [ ] Review with Murat (QA) for test coverage
- [ ] Review with Winston (Architect) for architecture concerns

### Deployment
- [ ] Create feature branch: `fix/aggregation-query-llm-rejection`
- [ ] Commit backend changes
- [ ] Commit frontend changes
- [ ] Run full test suite locally
- [ ] Push to GitHub
- [ ] Deploy to Railway (backend)
- [ ] Deploy to Railway (frontend)
- [ ] Run production smoke tests
- [ ] Monitor logs for 1 hour post-deploy

### Documentation
- [x] Bug investigation document created
- [ ] Update README with new query capabilities
- [ ] Document testing strategy
- [ ] Add rollback procedure to deployment docs

---

## Decision Log

| Decision | Rationale | Date | Decided By |
|----------|-----------|------|------------|
| Use Modified Approach B (Atomic Fix) | Balances thoroughness with deployment simplicity | 2025-10-05 | Team consensus |
| Add 3-5 aggregation examples | Comprehensive fix for entire query class | 2025-10-05 | Mary (Analyst) |
| Deploy backend + frontend together | Avoid broken intermediate states | 2025-10-05 | Winston (Architect) |
| **DEFER**: Architecture decision on LLM vs. endpoints | Requires cost-benefit analysis | 2025-10-05 | Kaelen (PO) |

---

## Next Steps

1. **Address Critical Blockers**:
   - Write and run tests for proposed fix
   - Document rollback procedure
   - Validate LLM generates correct SQL with new examples

2. **Implement Fix** (after blockers resolved):
   - Update LLM prompt with aggregation examples
   - Fix frontend error display
   - Deploy atomically to Railway

3. **Post-Deploy**:
   - Monitor error rates and query patterns
   - Gather user feedback on suggested queries
   - Consider strategic architecture review (LLM vs. endpoints)

4. **Future Enhancements**:
   - Dynamic query suggestions based on usage analytics
   - Query classification layer (structured vs. NL)
   - Dedicated endpoints for common aggregations

---

## References

**Files Analyzed:**
- `backend/app/services/llm_service.py` (lines 40-157)
- `backend/app/services/validation_service.py` (lines 48-167)
- `backend/app/services/query_service.py` (lines 61-187)
- `backend/app/api/routes.py` (lines 14-36)

**Elicitation Methods Applied:**
- Dependency Mapping
- Tree of Thoughts
- Self-Consistency Validation
- Challenge from Critical Perspective

**Team Contributors:**
- Mary (Business Analyst) - Root cause analysis
- Winston (Architect) - System design review
- Murat (Test Architect) - Critical challenges, testing strategy
- Sarah (Product Owner) - Documentation structure
- Bob (Scrum Master) - Process coordination
