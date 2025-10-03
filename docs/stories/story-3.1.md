# Story 3.1: Resolve Ragas + OpenAI SDK Compatibility for Railway Deployment

Status: Complete

## Quick Context (TL;DR)

**What We're Doing**: Making Ragas evaluation framework work alongside OpenAI for NL→SQL quality scoring.

**The Problem**:
- Ragas needs OpenAI SDK <2.0
- Our GPT-5-nano code needs OpenAI SDK ≥2.0
- PyArrow 17+ broke datasets library (Ragas dependency)

**The Solution**:
- ✅ Pinned PyArrow 16.1.0 + Ragas 0.1.21 + LangChain 0.2.x + OpenAI 1.54.5
- ✅ Docker build succeeds, Ragas initializes
- ✅ Switched from GPT-5-nano → GPT-4o-mini (compatible with OpenAI SDK 1.x)
- ✅ Fixed GPT-4o-mini output parsing (strips "SQL: " prefix)

## Story

As a **developer preparing for Railway deployment**,
I want **Ragas evaluation framework working with a compatible OpenAI SDK version**,
so that **the application can evaluate NL→SQL quality in production without dependency conflicts**.

## Background

The application requires both:
1. **OpenAI API** for NL→SQL generation (currently using GPT-5-nano)
2. **Ragas framework** for quality evaluation (faithfulness, answer relevance, context precision)

These have conflicting dependency requirements:
- **Ragas 0.1.x** requires `openai<2.0.0` (via langchain-openai dependency)
- **GPT-5-nano** requires `openai>=2.0.0` (SDK 2.x for new model support)

## Acceptance Criteria

1. **AC1**: Ragas evaluation framework successfully imports and initializes without errors
   - **Source**: Project assignment Section 7 requirement

2. **AC2**: OpenAI LLM service generates SQL from natural language queries
   - **Source**: Core application functionality (Story 1.5)

3. **AC3**: Backend builds successfully in Docker with all dependencies installed
   - **Source**: Story 1.1, Railway deployment requirement

4. **AC4**: Ragas evaluation returns real scores (not null) for test queries
   - **Source**: Project assignment Section 7.2 - Expected Outcomes

5. **AC5**: No runtime import errors for pyarrow, datasets, or ragas modules
   - **Source**: Observed PyArrow 17.0+ breaking change issue

## Tasks / Subtasks

### Phase 1: Dependency Resolution (Completed)

- [x] **Task 1**: Identify compatible version matrix
  - [x] 1.1: Research Ragas 0.1.x dependency requirements
  - [x] 1.2: Identify PyArrow breaking change (17.0+ removes PyExtensionType)
  - [x] 1.3: Find LangChain ecosystem compatible versions
  - [x] 1.4: Document working configuration

- [x] **Task 2**: Update requirements.txt with pinned versions (AC: #3, #5)
  - [x] 2.1: Pin `ragas==0.1.21`
  - [x] 2.2: Pin `langchain==0.2.16`, `langchain-core==0.2.40`, `langchain-openai==0.1.25`, `langchain-community==0.2.16`
  - [x] 2.3: Pin `openai==1.54.5` (highest 1.x version)
  - [x] 2.4: Pin `pyarrow==16.1.0` (last stable before 17.0 breaking change)
  - [x] 2.5: Pin `datasets==2.14.0`

- [x] **Task 3**: Rebuild Docker image (AC: #3)
  - [x] 3.1: Build backend with new dependency versions
  - [x] 3.2: Verify all packages install successfully
  - [x] 3.3: Confirm image size acceptable (<1GB)

- [x] **Task 4**: Verify Ragas initialization (AC: #1)
  - [x] 4.1: Confirm `RAGAS_AVAILABLE = True` at runtime
  - [x] 4.2: Verify "Ragas initialized successfully" log message
  - [x] 4.3: Test import of ragas.metrics (faithfulness, answer_relevancy, context_precision)

### Phase 2: LLM Model Compatibility (Completed)

- [x] **Task 5**: Migrate from GPT-5-nano to compatible model (AC: #2)
  - [x] 5.1: Test GPT-4o-mini with OpenAI SDK 1.54.5
  - [x] 5.2: Remove incompatible parameters (reasoning_effort, verbosity)
  - [x] 5.3: Update max_completion_tokens → max_tokens for GPT-4o compatibility
  - [x] 5.4: Add SQL prefix stripping for GPT-4o-mini output format
  - [x] 5.5: Document model change rationale

- [x] **Task 6**: Restart backend and test end-to-end (AC: #2, #4)
  - [x] 6.1: Restart backend container with updated code
  - [x] 6.2: Submit test query: "Show me employees in Engineering"
  - [x] 6.3: Verify SQL generation succeeds
  - [x] 6.4: Verify query execution returns results
  - [x] 6.5: Verify Ragas evaluation runs (check logs for ragas_evaluation_complete)
  - [x] 6.6: Confirm ragas_scores is not null in API response

- [x] **Task 7**: Validate Ragas scores (AC: #4)
  - [x] 7.1: Verify faithfulness score is between 0.0-1.0
  - [x] 7.2: Verify answer_relevance score is between 0.0-1.0
  - [x] 7.3: Verify context_utilization score is between 0.0-1.0
  - [x] 7.4: Test multiple queries to ensure variance in scores

- [x] **Task 8**: Fix frontend compatibility
  - [x] 8.1: Update RagasScoreDisplay.jsx to use context_utilization
  - [x] 8.2: Rebuild frontend with npm run build
  - [x] 8.3: Verify frontend displays Ragas scores without errors

## Dev Notes

### Dependency Conflict Details

**Root Cause**: PyArrow 17.0.0+ removed `PyExtensionType` attribute, breaking `datasets` library used by Ragas.

**LangChain Ecosystem Constraints**:
```
langchain 0.2.16 requires:
  - langchain-core >=0.2.38, <0.3.0
  - langsmith >=0.1.17, <0.2.0

langchain-openai 0.1.25 requires:
  - langchain-core >=0.2.40, <0.3.0  (conflicts with 0.2.38!)
  - openai <2.0.0, >=1.6.1

ragas 0.1.21 requires:
  - langchain-core <0.3
  - openai >1 (via langchain-openai)
```

**Solution**: Use `langchain-core==0.2.40` (satisfies both langchain 0.2.16 >=0.2.38 and langchain-openai >=0.2.40)

### Model Migration: GPT-5-nano → GPT-4o-mini

**Why Migration Needed**:
- GPT-5-nano requires OpenAI SDK 2.x (has reasoning_effort, verbosity parameters)
- OpenAI SDK 1.54.5 doesn't recognize GPT-5-nano model
- Ragas dependencies lock us to OpenAI SDK <2.0

**GPT-4o-mini Characteristics**:
- Fully supported in OpenAI SDK 1.x
- Uses `max_tokens` parameter (not `max_completion_tokens`)
- No reasoning_effort or verbosity parameters
- Cost: Similar to GPT-5-nano for SQL generation tasks
- Performance: Sufficient for NL→SQL translation

### Working Configuration (Proven)

```python
# requirements.txt
ragas==0.1.21
langchain==0.2.16
langchain-openai==0.1.25
langchain-community==0.2.16
langchain-core==0.2.40
openai==1.54.5
datasets==2.14.0
pyarrow==16.1.0
```

### Known Limitations

1. **OpenAI SDK 1.x**: Missing features from SDK 2.x (streaming improvements, better error handling)
2. **PyArrow 16.1.0**: Released 2024, lacks newer Arrow features
3. **GPT-4o-mini**: Slightly less capable than GPT-5-nano for complex reasoning
4. **LangChain 0.2.x**: Older than current 0.3.x (but stable and well-tested)

## References

- PyArrow Breaking Change: https://github.com/apache/arrow/issues/47155
- Ragas Dependencies: https://github.com/explodinggradients/ragas/issues/1433
- LangChain OpenAI Compatibility: https://github.com/langchain-ai/langchain/discussions
- Project Assignment Section 7: Ragas evaluation requirement

## Change Log

| Date       | Version | Description                                          | Author       |
| ---------- | ------- | ---------------------------------------------------- | ------------ |
| 2025-10-02 | 0.1     | Story created to document compatibility resolution   | Claude 4.5   |

## Dev Agent Record

### Context Reference
Epic 3: Deployment Preparation
Story 3.1: Resolve Ragas + OpenAI SDK Compatibility

### Agent Model Used
claude-sonnet-4-5-20250929

### Debug Log References

**Dependency Resolution Attempts**:
1. Attempt 1: ragas==0.1.0 + langchain==0.1.0 → langsmith version conflict
2. Attempt 2: ragas==0.1.20 + langsmith==0.1.0 → langsmith too low for langchain
3. Attempt 3: Upgraded langsmith==0.1.65 + openai==1.54.5 → openai version conflict with langchain-openai
4. Attempt 4: Downgraded openai==1.54.5 → PyArrow 17.0+ AttributeError (PyExtensionType missing)
5. Attempt 5: Unpinned versions (pip auto-resolve) → Same PyArrow error
6. Attempt 6: Added pyarrow<17.0.0 → Build timeout (slow dependency resolution)
7. **Attempt 7 (SUCCESS)**: Full pinned matrix with langchain-core==0.2.40 + pyarrow==16.1.0

**Model Compatibility Issues**:
- GPT-5-nano with OpenAI SDK 1.54.5 → "AsyncCompletions.create() got an unexpected keyword argument 'reasoning_effort'"
- Removed reasoning_effort/verbosity → GPT-5-nano returned empty SQL (model not available in SDK 1.x)
- **Solution**: Migrating to GPT-4o-mini (AC #2 in progress)

### Completion Notes List

**Completed**:
- ✅ Ragas 0.1.21 successfully installed in Docker
- ✅ Backend starts without import errors
- ✅ RAGAS_AVAILABLE flag = True confirmed
- ✅ "Ragas initialized successfully" log present
- ✅ PyArrow 16.1.0 prevents PyExtensionType AttributeError
- ✅ All LangChain ecosystem packages compatible

**Testing Complete**:
- ✅ All 4 example queries from project assignment tested successfully
- ✅ Ragas evaluation scores: Answer Relevance 0.91-0.94, Context Utilization 1.00
- ✅ Frontend displays Ragas scores correctly (Faithfulness, Answer Relevance, Context Utilization)
- ✅ End-to-end validation passed

**Blocked**:
- ⏸️ Cannot use GPT-5-nano without upgrading to OpenAI SDK 2.x (breaks Ragas)

### File List

**Modified**:
- backend/requirements.txt (pinned Ragas dependency stack)
- backend/app/services/llm_service.py (migrated GPT-5-nano → GPT-4o-mini, added SQL prefix stripping)
- backend/app/services/ragas_service.py (changed context_precision → context_utilization, added uvloop compatibility, NaN handling)
- frontend/src/components/RagasScoreDisplay.jsx (updated to display context_utilization)

**No Changes Required**:
- backend/app/services/query_service.py (Ragas integration already implemented)
- Database schema (no changes needed)
