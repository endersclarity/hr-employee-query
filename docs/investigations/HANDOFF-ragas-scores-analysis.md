# CONTEXT HANDOFF - RAGAS Scores Analysis Investigation

**Date:** 2025-10-06
**From:** Mary (Business Analyst)
**To:** Next Session/Agent
**Status:** Active Investigation - Ready for Deep Dive

---

## TL;DR - What You're Walking Into

We just fixed Bug #002 (RAGAS faithfulness timeout) but discovered **new potential issues** with RAGAS scores and query validation. Need to investigate whether these are real problems or misunderstandings.

---

## Background Context

### What We Just Fixed (30 minutes ago)
- **Bug #002:** RAGAS faithfulness returned NaN due to timeout
- **Root cause:** 192 claims × network latency = timeout
- **Solution:** Reduced sample from 10 → 3 records
- **Result:** Faithfulness now works! Score: 0.973
- **Deployment:** Commit `64e22c0`, live in production

### New Issues Raised by User (Kaelen)

**Issue #1:** "Faithfulness is so low"
- User thinks 0.973 is bad
- Actually 0.973 = 97.3% = **excellent** by RAGAS standards
- May be misunderstanding of metrics

**Issue #2:** "Context utilization always says 0"
- Production logs show: `context_utilization=0.9999999999666668`
- User is seeing 0.0 somewhere
- Discrepancy needs investigation - WHERE is user seeing this?

**Issue #3:** "Queries return 'INVALID_REQUEST' or 'query invalid'"
- User frustrated by query rejections
- System prompt (llm_service.py line 51) tells LLM to give up
- User's point: GPT-4o-mini should ALWAYS generate SELECT, not reject

---

## Current System Architecture

### Query Flow (When User Presses Enter)
1. Frontend → POST `/api/query`
2. `query_service.py` sanitizes input
3. **OpenAI GPT-4o-mini** generates SQL (with system prompt)
4. `validation_service.py` validates SQL (SELECT only, 'employees' table only)
5. PostgreSQL executes query
6. Results returned immediately
7. **Background:** RAGAS evaluates quality (60-90 seconds)

### RAGAS Metrics
- **Faithfulness:** Are claims in answer supported by context? (0-1 scale)
- **Answer Relevance:** Does answer address the question? (0-1 scale)
- **Context Utilization:** How much context was used? (0-1 scale)

### Current Production Scores (Query 50)
```json
{
  "faithfulness": 0.973,
  "answer_relevance": 0.893,
  "context_utilization": 0.999  // But user sees 0.0 somewhere?
}
```

---

## Key Files You'll Need

### Investigation Documents
- **Main investigation:** `docs/investigations/ragas-scores-analysis.md`
- **Previous bug:** `docs/investigations/ragas-faithfulness-nan-production.md`
- **Bug tracker:** `docs/bugs/002-ragas-faithfulness-always-zero.md`

### Code Files
- **System prompt:** `backend/app/services/llm_service.py` (lines 40-80)
- **Validation logic:** `backend/app/services/validation_service.py`
- **RAGAS service:** `backend/app/services/ragas_service.py`
- **Query flow:** `backend/app/services/query_service.py`
- **API routes:** `backend/app/api/routes.py`
- **Database models:** `backend/app/db/models.py`

### Production Info
- **Railway deployment:** `e1725295-f217-4e67-9e0f-b0f49c1d7d32`
- **Latest commit:** `64e22c0` (3-record sampling fix)
- **Production URL:** https://hr-employee-query-production.up.railway.app
- **Database:** PostgreSQL on Railway (hr_query_db)

---

## Investigation Tasks - What Needs Doing

### Priority 1: Find Where User Sees context_utilization=0

**Task:** Determine where the discrepancy is
- [ ] Check production database: `SELECT * FROM query_logs WHERE id=50`
- [ ] Check API response: `curl https://hr-employee-query-production.up.railway.app/api/query/50`
- [ ] Check analysis report: `curl .../api/reports/analysis`
- [ ] Check database schema - is column named correctly?
- [ ] Review ragas_service.py - does update actually happen?

**Hypothesis:** Frontend display bug OR database column name mismatch OR default value issue

---

### Priority 2: Verify Faithfulness Score Interpretation

**Task:** Confirm 0.973 is good, not bad
- [ ] Read RAGAS documentation for score ranges
- [ ] Run same query 5 times, check variance
- [ ] Test different query types, compare scores
- [ ] Document expected ranges (excellent/good/fair/poor)

**Expected result:** 0.973 is excellent, no action needed

---

### Priority 3: Fix INVALID_REQUEST Query Rejections

**Task:** Remove instruction that tells LLM to give up
- [ ] Edit `backend/app/services/llm_service.py` line 51
- [ ] Remove: "If the user's request cannot be fulfilled with a SELECT query, respond with: 'INVALID_REQUEST'"
- [ ] Add examples of reinterpreting non-SELECT as SELECT
- [ ] Test with queries that previously failed
- [ ] Deploy and verify improvement

**Security check:** validation_service.py still enforces SELECT-only rule ✅

---

### Priority 4: Comprehensive RAGAS Testing

**Task:** Build confidence in current implementation
- [ ] Test query types: aggregation, WHERE filter, DISTINCT, COUNT, etc.
- [ ] Test edge cases: 0 results, 1 result, 3 results, NULL-heavy data
- [ ] Document score patterns for each query type
- [ ] Create regression test suite

---

## Key Questions to Answer

1. **Where is user seeing context_utilization=0.0?**
   - Logs show 0.999
   - API response shows ???
   - Database shows ???
   - Frontend shows ???

2. **Is faithfulness 0.973 a problem?**
   - RAGAS scale: 0.0-1.0
   - Our score: 0.973
   - Good or bad?

3. **Which queries are getting rejected with INVALID_REQUEST?**
   - User reports frustration
   - Need examples of failing queries
   - Can we fix without security risk?

4. **Do RAGAS scores vary for same query?**
   - Deterministic or random?
   - LLM-based evaluation = inherent variance?
   - How much variance is acceptable?

---

## Tools Available

### Railway MCP Tools
```bash
# Get deployment logs
mcp__railway-mcp-server__get-logs

# Check deployment status
mcp__railway-mcp-server__list-deployments

# Monitor production
mcp__railway-mcp-server__get-logs --logType=deploy --lines=200
```

### Supabase MCP Tools (Database)
```bash
# Query database directly
mcp__supabase__execute_sql

# Check schema
mcp__supabase__list_tables
```

### Production Testing
```bash
# Submit test query
curl -X POST https://hr-employee-query-production.up.railway.app/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"Show employees in Engineering"}'

# Check results (replace {id})
curl https://hr-employee-query-production.up.railway.app/api/query/{id}

# Get analysis report
curl https://hr-employee-query-production.up.railway.app/api/reports/analysis
```

---

## Important Context

### User (Kaelen) Communication Style
- Direct, no-nonsense
- Frustrated when over-explained
- Wants one question answered at a time
- Prefers action over discussion
- Values evidence over speculation

### Current Emotional State
- Just spent hours fixing RAGAS timeout bug
- Tired of getting "query invalid" errors
- Wants simple explanations, not walls of text
- Ready to debug but needs clear next steps

### Project Status
- **Assignment deadline:** Unknown (assumed soon)
- **RAGAS requirement:** Must be functional for grading
- **Current status:** Faithfulness working, but user has concerns
- **Risk level:** Medium - scores work but user lacks confidence

---

## Recommended Approach

### Step 1: Quick Win - Find the 0.0
Start with the easiest verification - where is user actually seeing 0?
```bash
# Check database directly
curl https://hr-employee-query-production.up.railway.app/api/query/50 | jq
```

### Step 2: Educate on Metrics
Once we find the 0.0 issue, explain RAGAS scale:
- 0.973 faithfulness = 97.3% = **A+** grade
- Not "low" by any definition

### Step 3: Fix INVALID_REQUEST
Remove the problematic prompt instruction
- One-line change
- Deploy immediately
- Show improvement

### Step 4: Comprehensive Testing
Build confidence through systematic testing
- Run 10 different query types
- Document score patterns
- Create test suite for future

---

## What User Needs From You

1. **Answer ONE question at a time** (user specifically requested this)
2. **Show evidence, not speculation**
3. **Take action quickly** (user is tired of talking)
4. **Be concise** (no walls of text)
5. **Fix problems, don't just analyze them**

---

## Success Criteria

You'll know you're done when:
- ✅ Found where context_utilization shows 0.0
- ✅ Confirmed faithfulness 0.973 is excellent (or improved it if truly low)
- ✅ Removed INVALID_REQUEST, query success rate improved
- ✅ User has confidence in RAGAS implementation
- ✅ Test suite exists for regression detection

---

## Open Questions / Blockers

**None currently** - All tools available, production accessible, full context documented

---

## Last Known State

- **Time:** 2025-10-06 ~03:30 UTC
- **Location:** User's local machine, Claude Code session
- **Agent:** Mary (Business Analyst)
- **Mode:** Investigation phase
- **User Status:** Waiting for action, frustrated with query errors
- **System Status:** Production running, RAGAS functional but questioned

---

## Handoff Command

**To start fresh:**
```
"I'm investigating RAGAS scores and query validation issues. Three problems:

1. Context utilization shows 0.0 somewhere but logs show 0.999
2. User thinks faithfulness 0.973 is low (it's actually excellent)
3. Queries getting rejected with INVALID_REQUEST errors

Start with Priority 1: Find where context_utilization=0.0 is appearing.
Check production API response for query ID 50."
```

---

## Emergency Contacts / Resources

- **Investigation doc:** `docs/investigations/ragas-scores-analysis.md`
- **Production URL:** https://hr-employee-query-production.up.railway.app
- **Database:** PostgreSQL via Supabase MCP
- **Monitoring:** Railway MCP logs
- **Rollback:** `git revert 64e22c0 && git push` (if needed)

---

**Good luck! The user is counting on you to be direct and action-oriented.** 🎯
