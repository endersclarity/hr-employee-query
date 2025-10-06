# TEA Instrumentation Complete - RAGAS Debugging

**Date:** 2025-10-06
**Test Architect:** Murat
**Status:** ✅ READY FOR HYPOTHESIS TESTING

---

## What Was Done

### 1. NFR Assessment Completed

**Key Findings:**
- ✅ **Observability:** Good logging infrastructure, but missing actual data
- ✅ **Controllability:** Can modify code, but no local test environment
- ⚠️ **Debuggability:** AssertionError not being captured
- ✅ **Reliability:** 100% consistent failure (good for debugging)

**Gate Decision:** 🟡 CONCERNS - System testable but needs instrumentation

---

### 2. Instrumentation Added (Recommendation #1)

**File Modified:** `backend/app/services/ragas_service.py`

**Changes Made:**

#### A. Debug Logging (Lines 140-146)
```python
# DEBUG: Log actual data being passed to RAGAS for hypothesis verification
logger.debug("ragas_input_data",
    answer_preview=formatted_results[:500],
    context_preview=[c[:200] for c in result_contexts[:3]],
    question=nl_query
)
```

**Purpose:**
- See actual answer/context formats in Railway logs
- Verify Hypothesis #1 (format mismatch)
- Check data quality issues

**How to Use:**
1. Set Railway env var: `LOG_LEVEL=DEBUG`
2. Deploy changes
3. Run a query
4. Check Railway logs for `ragas_input_data` event

---

#### B. Enhanced Exception Handling (Lines 159-181)
```python
try:
    evaluation_result = await loop.run_in_executor(...)
except AssertionError as e:
    logger.error("ragas_assertion_error",
        error=str(e),
        message="RAGAS metric configuration issue - likely missing LLM setup",
        traceback_preview=traceback.format_exc()[:1000])
    return None
except Exception as e:
    logger.error("ragas_evaluation_exception",
        error=str(e),
        error_type=type(e).__name__,
        traceback_preview=traceback.format_exc()[:1000])
    return None
```

**Purpose:**
- Capture the mysterious AssertionError: "llm must be set to compute score"
- Verify Hypothesis #2 (missing LLM configuration)
- Get full traceback instead of generic "Exception raised in Job[0]"

---

### 3. Local Test Harness Created (Recommendation #2)

**Files Created:**
- `backend/tests/manual/test_ragas_local.py` - Test script
- `backend/tests/manual/README.md` - Instructions

**Purpose:**
- Test RAGAS locally WITHOUT deploying to Railway
- Verify if issue reproduces in local environment
- Test hypotheses safely before deployment

**How to Run:**
```bash
cd backend
export OPENAI_API_KEY="your-key-here"
python -m tests.manual.test_ragas_local
```

**What It Tests:**
1. **Test 1:** Current implementation with production data format
2. **Test 2:** Hypothesis #1 placeholder (format matching)
3. **Test 3:** Hypothesis #2 placeholder (LLM config)

**Expected Outcomes:**
- **If faithfulness = 0.0 locally:** Issue reproduces, can test fixes safely
- **If faithfulness > 0.0 locally:** Environment-specific issue, need to compare configs

---

## Next Steps for Kaelen

### Option A: Run Local Test FIRST (Recommended)

**Time:** 5 minutes
**Risk:** ZERO (doesn't touch production)

**Steps:**
1. Run `python -m tests.manual.test_ragas_local`
2. Check if faithfulness returns 0.0 or >0.0
3. Report results back

**If Test Passes (faithfulness > 0.0):**
- Problem is Railway-specific
- Compare environment differences
- Skip to Option C

**If Test Fails (faithfulness = 0.0):**
- Problem reproduces locally
- Can test fixes safely
- Proceed to Option B

---

### Option B: Deploy Instrumentation to Railway

**Time:** 10 minutes
**Risk:** LOW (only adds logging, no logic changes)

**Steps:**
1. Commit changes to `ragas_service.py`
2. Push to GitHub (Railway auto-deploys)
3. Set Railway env var: `LOG_LEVEL=DEBUG`
4. Run a test query on production
5. Check Railway logs for new debug events

**What to Look For:**
```json
{
  "event": "ragas_input_data",
  "answer_preview": "The employee_id is 1. The first_name is Emma...",
  "context_preview": ["Database record 1: employee_id=1, first_name=Emma..."]
}
```

**OR:**
```json
{
  "event": "ragas_assertion_error",
  "error": "llm must be set to compute score",
  "message": "RAGAS metric configuration issue - likely missing LLM setup"
}
```

**This gives us PROOF of which hypothesis is correct.**

---

### Option C: Compare Environment Differences

**If local test passes but Railway fails:**

**Check These:**
1. **Package Versions:**
   ```bash
   # Local
   pip freeze | grep ragas

   # Railway (check build logs or add to startup)
   ```

2. **Python Version:**
   ```bash
   # Local
   python --version

   # Railway (check Dockerfile or Railway settings)
   ```

3. **Environment Variables:**
   - Compare local `.env` vs Railway env vars
   - Check for missing/different values

---

## Hypothesis Verification Plan

Once we have evidence from instrumentation:

### If Hypothesis #1 is Correct (Format Mismatch):
**Test:** Modify `ragas_service.py` lines 106-132 to use matching formats
**Expected:** Faithfulness > 0.0
**Risk:** LOW - can test locally first

### If Hypothesis #2 is Correct (Missing LLM):
**Test:** Add explicit LLM configuration to `initialize_ragas()`
**Expected:** Faithfulness > 0.0
**Risk:** MEDIUM - requires understanding RAGAS API

### If Both Are Wrong:
**Test:** Use evidence from debug logs to form new hypothesis
**Expected:** TBD
**Risk:** UNKNOWN

---

## Quality Gate Status

**Current:** 🟡 CONCERNS → ✅ READY FOR TESTING

**Gate Lifted Because:**
- ✅ Observability gap fixed (debug logging added)
- ✅ Controllability gap fixed (local test harness created)
- ✅ Can now verify hypotheses systematically
- ✅ No more blind deployments

**Remaining Risks:**
- ⚠️ Still don't know which hypothesis is correct
- ⚠️ Deployment to Railway required for final verification
- ⚠️ 6 days until presentation

**Recommended Next Action:**
1. Run local test (5 min, zero risk)
2. Deploy instrumentation (10 min, low risk)
3. Gather evidence from logs
4. Verify hypothesis
5. Design fix with TEA's `*test-design`

---

## Files Modified

**Modified:**
- `backend/app/services/ragas_service.py` (added logging + exception handling)

**Created:**
- `backend/tests/manual/test_ragas_local.py` (local test harness)
- `backend/tests/manual/README.md` (test instructions)
- `docs/investigations/tea-instrumentation-complete.md` (this file)

**No Files Deleted**

---

## Rollback Plan

If instrumentation causes issues:

```bash
git revert HEAD
git push origin master
# Railway auto-deploys previous version
```

**Risk:** MINIMAL - only added logging, didn't change logic

---

**Kaelen, the ball is in your court. Which option do you want to try first?**

**A) Run local test**
**B) Deploy instrumentation to Railway**
**C) Both in sequence (A then B)**

I recommend **Option C** - run local test first to see if we can avoid deploying at all.
