# Pre-Demo Validation Checklist

**Target Demo Date:** October 12, 2025
**Last Updated:** 2025-10-02

---

## Critical Path Testing (Must Pass Before Demo)

### 1. Database Setup & Seed Data
- [ ] Start database: `docker-compose up -d`
- [ ] Verify database connection: `psql $DATABASE_URL -c "SELECT 1;"`
- [ ] Confirm seed data exists: `psql $DATABASE_URL -c "SELECT COUNT(*) FROM employees;"`
  - Expected: At least 10-20 sample employees with varied data

### 2. Backend API Tests
- [ ] Run full test suite: `pytest backend/tests/ -v`
  - Expected: 39/39 tests passing
- [ ] Start backend server: `uvicorn backend.app.main:app --reload`
- [ ] Verify health endpoint: `curl http://localhost:8000/api/health`
  - Expected: `{"status": "healthy", "database": "connected"}`

### 3. LLM Integration Validation (Critical!)
- [ ] Set OpenAI API key in `.env`: `OPENAI_API_KEY=sk-...`
- [ ] Run integration test: `python -m backend.app.services.test_llm_integration`
  - Expected: All 4 mandatory queries return valid SQL and execute successfully
  - **If this fails, demo will not work!**

### 4. Manual End-to-End Smoke Tests
Test all 4 mandatory query types via API:

```bash
# Query 1: Date range
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show me employees hired in the last 6 months"}'

# Query 2: Department + Salary filter
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "List Engineering employees with salary greater than 120K"}'

# Query 3: Leave type
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who is on parental leave?"}'

# Query 4: Manager filter
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Show employees managed by John Doe"}'
```

**Expected for each:**
- ✅ `"success": true`
- ✅ `"generated_sql"` contains valid SQL
- ✅ `"results"` array has data (may be empty if no matching records)
- ✅ Response time < 5s

### 5. Frontend (When Available)
- [ ] Start frontend: `npm run dev` (or equivalent)
- [ ] Navigate to UI in browser
- [ ] Test search interface with sample queries
- [ ] Verify results display correctly in table

### 6. Ragas Evaluation (Epic 2)
- [ ] Run evaluation suite (when implemented)
- [ ] Review accuracy metrics
- [ ] Verify reports generate

---

## Known Issues / Workarounds

| Issue | Workaround | Story Reference |
|-------|------------|-----------------|
| Database connection fails | Ensure Docker is running: `docker ps` | Story 1.2 |
| OpenAI rate limits | Wait 60s or use different API key | Story 1.5 |
| (Add issues as discovered) | | |

---

## Performance Benchmarks

Target response times for demo queries:

| Component | Target | Acceptable | Red Flag |
|-----------|--------|------------|----------|
| LLM (NL→SQL) | < 1s | < 2.5s | > 5s |
| SQL Execution | < 100ms | < 500ms | > 1s |
| End-to-end | < 2s | < 4s | > 10s |

---

## Demo Day Emergency Contacts

- **OpenAI Support**: platform.openai.com/support
- **Database Issues**: Check Docker logs: `docker-compose logs db`
- **API Debugging**: Check backend logs in terminal

---

## Post-Demo Debrief

After demo, record:
- [ ] What worked well?
- [ ] What broke or was close to breaking?
- [ ] Questions you couldn't answer?
- [ ] Follow-up improvements needed?

**Notes:**
_(Add post-demo notes here)_
