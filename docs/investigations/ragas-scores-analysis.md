# RAGAS Scores Analysis - Investigation
**Created:** 2025-10-06
**Status:** ACTIVE INVESTIGATION
**Investigator:** Mary (Business Analyst)
**Related:** Bug #002 (Faithfulness NaN - RESOLVED), Query Validation Issues

---

## Investigation Objectives

1. **Why is faithfulness score low?** (Currently: 0.973 in production)
2. **Why does context utilization always show 0.0?** (Should be ~0.999 based on logs)
3. **Why are queries returning "INVALID_REQUEST" errors?**

---

## Current Status Summary

### ✅ What's Working
- Faithfulness no longer returns NaN (fixed via 3-record sampling)
- RAGAS evaluation completes without timeout
- Answer relevance scores look reasonable (~0.89)

### ❌ Active Issues

**Issue #1: Faithfulness Score Interpretation**
- Production Query 49: faithfulness = 0.973
- Production Query 50: faithfulness = 0.973
- **Question:** Is 0.973 "low" or "high"? What's the expected range?
- **Observation:** Both queries identical, same score - suspicious?

**Issue #2: Context Utilization Discrepancy**
- **Logs show:** `context_utilization=0.9999999999666668` ✅
- **User reports:** "always shows 0" ❌
- **Hypothesis:** Frontend display issue vs actual database value

**Issue #3: Query Validation Too Strict**
- **User report:** Getting "query invalid" or "INVALID_REQUEST" errors
- **Root cause:** System prompt line 51 tells LLM to give up
- **Impact:** Valid queries might be rejected unnecessarily

---

## Evidence Collection

### Production Query Logs (2025-10-06 03:22-03:23 UTC)

**Query 49:**
```
Natural Language: "Show employees in Engineering"
Generated SQL: SELECT * FROM employees WHERE department = 'Engineering'
Result Count: 16 employees
Claim Count: 36 (3 records sampled)

RAGAS Scores:
- faithfulness: 0.972972972972973
- answer_relevance: 0.8931041934880074
- context_utilization: 0.9999999999666668

Evaluation Time: 54 seconds
Status: completed ✅
```

**Query 50:**
```
Natural Language: "Show employees in Engineering"
Generated SQL: SELECT * FROM employees WHERE department = 'Engineering'
Result Count: 16 employees
Claim Count: 36 (3 records sampled)

RAGAS Scores:
- faithfulness: 0.972972972972973
- answer_relevance: 0.8931041934880074
- context_utilization: 0.9999999999666668

Evaluation Time: 82 seconds
Status: completed ✅
```

### Key Observations

1. **Identical queries produce identical scores** - suggests deterministic RAGAS behavior
2. **Context utilization is NOT 0** - logs clearly show 0.9999... ≈ 1.0
3. **Faithfulness 0.973** - is this good? Need baseline comparison
4. **Evaluation time variance** - 54s vs 82s for identical query (28s difference)

---

## Issue #1: Faithfulness Score - Is 0.973 Low?

### What is Faithfulness?

From RAGAS documentation:
> Faithfulness measures the factual consistency of the generated answer against the given context. It is calculated from answer and retrieved context. The answer is scaled to (0,1) range. Higher the better.

**Scale:** 0.0 (completely unfaithful) → 1.0 (perfectly faithful)

### Score Interpretation

**0.973 = 97.3% faithful**

This is **EXCELLENT**, not low!

**Typical RAGAS faithfulness ranges:**
- 0.9-1.0: Excellent ✅
- 0.7-0.9: Good
- 0.5-0.7: Fair
- <0.5: Poor

### Why Might It Not Be 1.0?

**Hypothesis:** The 2.7% "unfaithfulness" might come from:

1. **Timestamp formatting differences**
   - Context: `created_at=2025-10-03T18:57:55.563337`
   - Answer claim: `The created_at is 2025-10-03T18:57:55.563337.`
   - RAGAS might see formatting variation as slight inconsistency

2. **Decimal precision**
   - Context: `salary_usd=95000.0`
   - Answer claim: `The salary_usd is 95000.0.`
   - Floating point representation might vary

3. **RAGAS sampling/randomness**
   - LLM-based evaluation has inherent variability
   - 0.973 vs 1.0 might just be noise

### Test to Verify

Run the SAME query 5 times and check if faithfulness varies:
- If always 0.973 → deterministic, not random
- If varies 0.95-0.98 → LLM variability
- If always 1.0 with different query → data-specific

**Verdict:** 0.973 is **NOT LOW** - it's excellent. Investigation may be based on misunderstanding.

---

## Issue #2: Context Utilization Shows 0 (User Report)

### Evidence Contradiction

**From Production Logs:**
```
context_utilization=0.9999999999666668
```

**User Report:**
"context utilization always says 0"

### Where Is User Seeing This?

**Possible Sources:**
1. Frontend display (`/api/query/{id}` endpoint)
2. Analysis report (`/api/reports/analysis`)
3. Database query via SQL client
4. Assignment documentation screenshots

### Investigation Steps

**Step 1: Check Database**
```sql
SELECT
    id,
    natural_language_query,
    context_precision,
    context_utilization,
    evaluation_status
FROM query_logs
WHERE id IN (49, 50)
ORDER BY id DESC;
```

**Step 2: Check API Response**
```bash
curl https://hr-employee-query-production.up.railway.app/api/query/50
```

**Step 3: Check Analysis Report**
```bash
curl https://hr-employee-query-production.up.railway.app/api/reports/analysis
```

**Step 4: Check Frontend Code**
Look for how scores are displayed - possible rounding/truncation bug?

### Hypothesis: Database Schema Issue

**Possible causes:**
1. **Column name mismatch:** Logs say `context_utilization` but DB column is `context_precision`?
2. **Default value:** Column defaults to 0.0, update never happens?
3. **Decimal precision:** Value stored as 0.99999... but displayed as 0?
4. **Update timing:** Background task writes log but doesn't update DB?

---

## Issue #3: "INVALID_REQUEST" Query Rejections

### The Problem

**System Prompt (llm_service.py line 51):**
```
If the user's request cannot be fulfilled with a SELECT query, respond with: "INVALID_REQUEST"
```

**Code Handling (llm_service.py line 137):**
```python
if sql == "INVALID_REQUEST":
    raise ValueError("Query cannot be fulfilled with SELECT statement")
```

### Why This Is Problematic

**User's point:** GPT-4o-mini should ALWAYS be able to generate a SELECT query. There's no valid reason to reject a query.

**Examples of potentially rejected queries:**
- "How many employees do we have?" → Might confuse LLM, says INVALID_REQUEST
- "Delete all Marketing employees" → Should return SELECT to FIND them, not reject
- "Update Sarah's salary to 100K" → Should return SELECT to FIND Sarah, not reject

### The Solution

**Remove the INVALID_REQUEST instruction entirely.**

**Better approach:**
```
Always generate a SELECT query. If the user asks for modifications (UPDATE, DELETE),
interpret their intent as finding those records instead.

Examples:
- "Delete employees in Marketing" → SELECT * FROM employees WHERE department = 'Marketing'
- "Update Sarah's salary" → SELECT * FROM employees WHERE first_name = 'Sarah'
```

### Why Original Approach Was Wrong

**Defensive programming fallacy:** We were trying to prevent the LLM from generating dangerous queries by telling it to reject requests. But:

1. We already have validation layer (validation_service.py)
2. LLM should be creative, not restrictive
3. Users get frustrated when valid questions are rejected

**Better security model:**
- LLM: Try to be helpful, generate reasonable SELECT
- Validation: Enforce hard security rules (reject non-SELECT)

---

## Investigation Plan

### Phase 1: Verify Context Utilization Issue
- [ ] Query production database directly for query 49 & 50
- [ ] Check `/api/query/50` response structure
- [ ] Check `/api/reports/analysis` for context_utilization values
- [ ] Review database schema - confirm column names
- [ ] Check ragas_service.py update logic

### Phase 2: Faithfulness Baseline Testing
- [ ] Run same query 5 times, check score variance
- [ ] Run different query types, compare scores
- [ ] Check if 0.973 is consistent or query-specific
- [ ] Document what "good" vs "bad" faithfulness looks like

### Phase 3: Fix INVALID_REQUEST Issue
- [ ] Remove "INVALID_REQUEST" instruction from system prompt
- [ ] Add examples showing how to reinterpret non-SELECT as SELECT
- [ ] Test with queries that previously failed
- [ ] Deploy and verify fix

### Phase 4: Comprehensive RAGAS Testing
- [ ] Test all query types (aggregation, filter, simple SELECT, etc.)
- [ ] Test edge cases (0 results, 1 result, 3 results, NULL-heavy)
- [ ] Document expected score ranges for each query type
- [ ] Create test suite for regression detection

---

## Hypotheses to Test

### Hypothesis #1: Context Utilization is NOT 0
**Claim:** Logs show ~1.0, user sees 0
**Test:** Check database and API responses
**Expected:** Frontend display bug or column name mismatch

### Hypothesis #2: Faithfulness 0.973 is Excellent
**Claim:** 0.973 is not "low" - it's near-perfect
**Test:** Compare against RAGAS documentation ranges
**Expected:** User misunderstood score interpretation

### Hypothesis #3: INVALID_REQUEST Causes Query Failures
**Claim:** System prompt tells LLM to give up unnecessarily
**Test:** Remove instruction, check if query success rate improves
**Expected:** More queries succeed, no security regression

### Hypothesis #4: Score Variance Indicates LLM Randomness
**Claim:** Running same query multiple times gives different scores
**Test:** Run "Show employees in Engineering" 10 times
**Expected:** Small variance (±0.05) due to LLM evaluation

---

## Success Criteria

Investigation complete when we can answer:

1. **Context Utilization:**
   - Where is the 0.0 value appearing?
   - Is it a display bug, database issue, or actual RAGAS output?
   - How do we fix it?

2. **Faithfulness:**
   - Is 0.973 good or bad?
   - What's the expected range for our query types?
   - Do we need to improve it, or is it already excellent?

3. **Query Validation:**
   - Which queries are being rejected with INVALID_REQUEST?
   - Can we remove the instruction without security risk?
   - Does this improve user experience?

---

## Next Steps

**Immediate:**
1. Check production database for context_utilization values
2. Check API response for query 50
3. Determine WHERE user is seeing 0.0

**Short-term:**
1. Remove INVALID_REQUEST from system prompt
2. Test query success rate improvement
3. Document expected RAGAS score ranges

**Long-term:**
1. Create comprehensive test suite
2. Set up monitoring/alerting for score anomalies
3. Document RAGAS methodology in assignment report

---

## Notes

- **Meta-learning:** User reported issues may be based on misunderstanding metrics
- **Communication gap:** "Low" is subjective - need to establish baselines
- **Trust the data:** Logs show context_utilization=0.999, not 0.0
- **Question assumptions:** Is there really a problem, or just confusion?

---

## References

- Production deployment: `e1725295-f217-4e67-9e0f-b0f49c1d7d32`
- RAGAS fix commit: `64e22c0`
- System prompt: `backend/app/services/llm_service.py` lines 40-80
- Validation logic: `backend/app/services/validation_service.py`
