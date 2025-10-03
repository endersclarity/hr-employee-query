# Technical Specification: Epic 2 - Ragas Evaluation & Reporting

Date: 2025-10-01
Author: Kaelen
Epic ID: Epic 2
Status: Draft

---

## Overview

Epic 2 implements the Ragas evaluation framework to assess the quality and reliability of the NL→SQL query system built in Epic 1. This epic adds three critical evaluation metrics—Faithfulness (schema consistency), Answer Relevance (intent alignment), and Context Precision (field selection)—to every query response. The system calculates Ragas scores in real-time, displays them in the frontend alongside results, and generates comparative analysis reports to identify weak spots and provide actionable improvement recommendations. This evaluation layer transforms the demo from a basic query tool into a production-quality system that demonstrates awareness of LLM reliability concerns and systematic quality measurement.

## Objectives and Scope

### Objectives
1. **Demonstrate LLM Quality Awareness**: Show interview panel that you understand LLM reliability challenges and measure output quality systematically
2. **Implement Production-Grade Evaluation**: Integrate Ragas framework with Faithfulness (0.9+ target), Answer Relevance (0.8+ target), and Context Precision (0.8+ target) metrics
3. **Enable Continuous Improvement**: Generate comparative reports that identify low-scoring queries and provide specific recommendations for prompt engineering, schema refinement, or few-shot example additions
4. **Differentiate Demo from Basic Tools**: Transform from "ChatGPT wrapper" to "evaluated, reliable system" suitable for enterprise deployment

### In-Scope (Epic 2)
- ✅ Ragas framework integration (Python library + embeddings model)
- ✅ Three core metrics: Faithfulness, Answer Relevance, Context Precision
- ✅ Real-time score calculation for every query (integrated into query flow)
- ✅ Frontend display of Ragas scores with color-coded badges (green >0.8, yellow 0.7-0.8, red <0.7)
- ✅ Query logging to database (query_logs table with NL query, SQL, scores, timestamp)
- ✅ Comparative analysis report generation (score trends, weak spot identification)
- ✅ Actionable recommendations engine (prompt improvements, schema suggestions)

### Out-of-Scope (Epic 2)
- ❌ Additional Ragas metrics beyond the core 3 (Context Recall, Context Relevancy)
- ❌ A/B testing framework for prompt variations
- ❌ Automated prompt optimization based on Ragas feedback
- ❌ Historical trend analysis over weeks/months (demo is single-session)
- ❌ User feedback integration (thumbs up/down on results)
- ❌ Custom evaluation metrics beyond Ragas

## System Architecture Alignment

Epic 2 extends the Epic 1 architecture with evaluation layer components:

**Architectural Pattern**: Modular Monolith (maintains same pattern as Epic 1, adds evaluation modules)

**Key Components Added**:
- **Evaluation Layer**: Ragas service module (`ragas_service.py`) integrated into query flow
- **Data Persistence**: `query_logs` table added to PostgreSQL schema
- **Frontend Components**: `RagasScoreDisplay.jsx` component with score badges
- **Reporting Module**: `report_service.py` for comparative analysis and recommendations

**Integration with Epic 1**:
- Ragas service called AFTER successful query execution (Epic 1 Story 1.7)
- Extends QueryResponse model to include `ragas_scores` field
- Reuses existing logging infrastructure (structlog) for evaluation metrics
- No changes to security layer, LLM integration, or database schema (employees table)

**Dependencies on Epic 1**:
- `query_service.py` must be complete (orchestrates Ragas call)
- `QueryResponse` Pydantic model must be extensible
- Database connection (`db/session.py`) must support query_logs table
- Frontend must render additional UI components without breaking existing layout

**Constraints Adhered To**:
- Maintains < 5 second response time (Ragas adds ~500-800ms overhead)
- No additional external services (Ragas runs in-process)
- Same deployment model (Railway, Docker Compose)

## Detailed Design

### Services and Modules

| Module | Responsibility | Inputs | Outputs | Owner/Location |
|--------|---------------|--------|---------|----------------|
| **ragas_service** (Python) | Calculate Faithfulness, Answer Relevance, Context Precision | NL query, SQL, results, schema | RagasScores dict | `backend/app/services/ragas_service.py` |
| **report_service** (Python) | Generate comparative analysis and recommendations | List[QueryLog] | AnalysisReport | `backend/app/services/report_service.py` |
| **RagasScoreDisplay** (React) | Display scores with color-coded badges | RagasScores object | Rendered score UI | `frontend/src/components/RagasScoreDisplay.jsx` |
| **QueryLog** (SQLAlchemy) | Persist query history with scores | Query data | Database record | `backend/app/db/models.py` |

### Data Models and Contracts

**query_logs table** (PostgreSQL):
```sql
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    natural_language_query TEXT NOT NULL,
    generated_sql TEXT NOT NULL,
    faithfulness_score DECIMAL(3, 2),  -- 0.00-1.00
    answer_relevance_score DECIMAL(3, 2),
    context_precision_score DECIMAL(3, 2),
    result_count INTEGER,
    execution_time_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_created_at ON query_logs(created_at DESC);
CREATE INDEX idx_faithfulness ON query_logs(faithfulness_score);
```

**Extended QueryResponse** (Pydantic):
```python
class RagasScores(BaseModel):
    faithfulness: float = Field(..., ge=0.0, le=1.0)
    answer_relevance: float = Field(..., ge=0.0, le=1.0)
    context_precision: float = Field(..., ge=0.0, le=1.0)

class QueryResponse(BaseModel):  # Extended from Epic 1
    # ... existing fields ...
    ragas_scores: RagasScores | None = None  # NEW
```

**AnalysisReport** (Pydantic):
```python
class AnalysisReport(BaseModel):
    total_queries: int
    average_scores: RagasScores
    weak_queries: List[Dict]  # Queries with scores < 0.7
    recommendations: List[str]  # Actionable improvements
```

### APIs and Interfaces

**GET /api/reports/analysis** (NEW)

Generate comparative analysis report.

**Response (200)**:
```json
{
  "total_queries": 25,
  "average_scores": {
    "faithfulness": 0.89,
    "answer_relevance": 0.82,
    "context_precision": 0.79
  },
  "weak_queries": [
    {"query": "Show me high earners", "scores": {...}, "reason": "Ambiguous threshold"}
  ],
  "recommendations": [
    "Add few-shot example for salary comparisons",
    "Include salary range in schema prompt"
  ]
}
```

### Workflows and Sequencing

**Enhanced Query Flow (with Ragas)**:
```
[Epic 1: Query Flow] → Results from DB
                          ↓
                    [ragas_service.evaluate()]
                          ↓
                    Calculate 3 metrics (500-800ms)
                          ↓
                    [Save to query_logs table]
                          ↓
                    [Add ragas_scores to QueryResponse]
                          ↓
                    [Frontend: RagasScoreDisplay]
                          ↓
                    [User sees scores below results]
```

## Non-Functional Requirements

### Performance
**Target**: Ragas evaluation adds < 1 second to total response time (maintains < 5s total from Epic 1)

**Ragas Overhead Breakdown**:
- Faithfulness calculation: 200-300ms
- Answer Relevance calculation: 150-250ms
- Context Precision calculation: 150-250ms
- Database logging: 20-50ms
- **Total**: 500-850ms additional latency

**Optimization**: Run Ragas evaluation asynchronously AFTER returning results to user (optional future enhancement)

### Security
No new security requirements. Ragas operates on data already validated by Epic 1 security layers.

### Reliability/Availability
**Graceful Degradation**: If Ragas fails, return results WITHOUT scores (don't block user)
```python
try:
    scores = await ragas_service.evaluate(...)
except Exception as e:
    logger.error(f"Ragas evaluation failed: {e}")
    scores = None  # Return None, display results anyway
```

### Observability
**New Log Events**:
```python
logger.info("ragas_evaluation_complete",
    faithfulness=scores.faithfulness,
    answer_relevance=scores.answer_relevance,
    context_precision=scores.context_precision,
    evaluation_time_ms=elapsed
)
```

## Dependencies and Integrations

### Python Dependencies (ADD to requirements.txt)
```
ragas==0.1.0              # Evaluation framework
langchain==0.1.0          # Required by Ragas
openai==1.10.0            # Already in Epic 1 (reuse for embeddings)
```

### Epic 1 Dependencies
- `query_service.py` - Must call ragas_service after SQL execution
- `QueryResponse` model - Must be extended with ragas_scores field
- `db/session.py` - Must support query_logs table creation
- Frontend App.jsx - Must render RagasScoreDisplay component

### External Services
- **OpenAI Embeddings API** - Used by Ragas for semantic similarity (text-embedding-ada-002)
- **PostgreSQL** - query_logs table for persistence

## Acceptance Criteria (Authoritative)

**AC1**: Ragas framework successfully initializes with embeddings model
- **Test**: Import ragas library, initialize evaluator → No errors

**AC2**: System calculates Faithfulness, Answer Relevance, Context Precision for every query
- **Test**: Execute query → Response includes `ragas_scores` with 3 metrics (0.0-1.0 range)

**AC3**: Frontend displays Ragas scores with color-coded badges
- **Test**: Execute query → See 3 score badges (green if >0.8, yellow 0.7-0.8, red <0.7)

**AC4**: All queries logged to query_logs table with scores
- **Test**: Execute 5 queries → SELECT * FROM query_logs shows 5 records

**AC5**: Analysis report identifies weak queries (scores < 0.7)
- **Test**: GET /api/reports/analysis → Response includes weak_queries list

**AC6**: System generates actionable recommendations
- **Test**: Analysis report includes specific suggestions (e.g., "Add few-shot example for...")

**AC7**: Ragas evaluation doesn't break query flow if it fails
- **Test**: Mock Ragas failure → Query still returns results, scores = null

**AC8**: Total response time remains < 5 seconds with Ragas enabled
- **Test**: Execute 10 queries → P95 latency < 5s

## Traceability Mapping

| AC | PRD Requirement | Spec Section | Component | Test Approach |
|----|----------------|--------------|-----------|---------------|
| **AC1** | FR007 (Ragas framework) | Dependencies → Python | `ragas_service.py` | Unit test: Initialize Ragas → no errors |
| **AC2** | FR007 (3 metrics) | Data Models → RagasScores | `ragas_service.py` | Integration: Query → verify 3 scores present |
| **AC3** | FR008 (Display scores) | Services → RagasScoreDisplay | `RagasScoreDisplay.jsx` | Manual UI: Execute query → see badges |
| **AC4** | FR009 (Log queries) | Data Models → query_logs | `models.py` | DB query: Check logs table after queries |
| **AC5** | FR014 (Comparative reports) | APIs → /api/reports/analysis | `report_service.py` | API test: GET analysis → verify weak_queries |
| **AC6** | FR015 (Recommendations) | APIs → AnalysisReport | `report_service.py` | API test: Verify recommendations list |
| **AC7** | NFR - Reliability | Reliability → Graceful Degradation | `query_service.py` | Mock Ragas failure → verify fallback |
| **AC8** | NFR002 (Performance) | Performance → < 5s total | All components | Load test: 10 queries with Ragas enabled |

### Story → Acceptance Criteria Mapping

| Story | Primary AC(s) Covered | Notes | Dependencies |
|-------|----------------------|-------|--------------|
| **Story 2.1** (Ragas Integration) | AC1 | Install Ragas, initialize evaluator | Epic 1 complete |
| **Story 2.2** (Core Metrics) | AC2, AC7 | Implement 3 metrics + error handling | Story 2.1 |
| **Story 2.3** (Frontend Display) | AC3 | Score badges UI | Story 2.2 |
| **Story 2.4** (Reports) | AC4, AC5, AC6 | Logging + analysis + recommendations | Story 2.2 |

## Risks, Assumptions, Open Questions

### Risks

**RISK-1: Ragas Performance Overhead**
- **Description**: Evaluation adds > 1s latency, breaking 5s performance target
- **Probability**: Medium (Ragas can be slow with large result sets)
- **Impact**: High (fails NFR002)
- **Mitigation**:
  - Limit evaluation to first 10 result rows
  - Run Ragas async AFTER returning results (don't block response)
  - Cache Ragas results for identical queries

**RISK-2: Ragas Library Compatibility**
- **Description**: Ragas version conflicts with existing dependencies (OpenAI SDK, LangChain)
- **Probability**: Low (Ragas well-maintained)
- **Impact**: Medium (can't install Ragas)
- **Mitigation**: Pin exact versions in requirements.txt, test in isolated venv first

**RISK-3: Embeddings API Costs**
- **Description**: Ragas uses OpenAI embeddings API (text-embedding-ada-002) for each query → costs add up
- **Probability**: Low (demo has limited queries)
- **Impact**: Low ($0.01 per 1000 queries)
- **Mitigation**: Use paid OpenAI tier, monitor costs

### Assumptions

**ASSUMPTION-1: Ragas Works with NL→SQL Use Case**
- **Assumption**: Ragas (designed for RAG) adapts to NL→SQL evaluation
- **Validation**: Research confirms Ragas works for any LLM output evaluation
- **If False**: Implement custom metrics instead (schema validation, SQL syntax check)

**ASSUMPTION-2: Epic 1 Complete Before Epic 2 Starts**
- **Assumption**: All Epic 1 stories done, query flow working end-to-end
- **Validation**: Explicit dependency in PRD
- **If False**: Cannot integrate Ragas without working query system

### Open Questions

**QUESTION-1: Ragas Metric Weights**
- **Question**: Should all 3 metrics be weighted equally, or prioritize Faithfulness?
- **Options**: (A) Equal weight, (B) Faithfulness 50%, others 25% each
- **Decision Needed By**: Story 2.2
- **Recommendation**: Equal weight for MVP, allow customization later

**QUESTION-2: Report Generation Trigger**
- **Question**: When to generate analysis report? (On-demand, scheduled, after N queries)
- **Options**: (A) Manual API call, (B) After every 10 queries, (C) End of demo session
- **Decision Needed By**: Story 2.4
- **Recommendation**: Manual API call for demo flexibility

## Test Strategy Summary

### Test Levels

**Unit Tests** (Python):
- `ragas_service.py`: Mock Ragas library, test metric calculation logic
- `report_service.py`: Test analysis algorithm, recommendation generation
- **Framework**: pytest with mocked Ragas

**Integration Tests**:
- Test full query flow WITH Ragas enabled
- Test /api/reports/analysis endpoint
- Test query_logs table persistence

**Performance Tests**:
- Measure Ragas overhead (target < 1s)
- Load test: 20 queries with Ragas → verify P95 < 5s

**Failure Tests**:
- Mock Ragas exception → verify graceful degradation (AC7)
- Test with empty result sets → verify metrics still calculate

### Success Metrics

Epic 2 is **complete** when:
- ✅ All 8 acceptance criteria pass
- ✅ Ragas scores display correctly for all 4 mandatory queries
- ✅ Analysis report generates with recommendations
- ✅ Performance target met (< 5s with Ragas)
- ✅ No breaking changes to Epic 1 functionality

---

## Post-Review Follow-ups

**Story 2.1 Review Findings** (2025-10-02):
- **[Medium Priority]** ~~Implement `evaluate()` function for Story 2.2~~ - ✅ Resolved: Infrastructure implemented in Story 2.2
- **[Low Priority]** Add type hints to `initialize_ragas()` for better IDE support (backend/app/services/ragas_service.py:16)
- **[Low Priority]** Document Ragas dependency installation time in deployment guide (3-5 min resolution on Windows)

**Story 2.2 Review Findings** (2025-10-02):
- **[Medium Priority]** Implement actual Ragas metric calculation in `evaluate()` - Infrastructure complete but returns placeholder 0.0 scores. Real Ragas library calls needed for AC1 value. Create Story 2.2.1 or complete before Epic 2 sign-off. (backend/app/services/ragas_service.py:56-73)
- **[Low Priority]** Add specific type hint `Dict[str, float] | None` for evaluate() return value (backend/app/services/ragas_service.py:37)
- **[Low Priority]** Add performance test with real Ragas overhead measurement - verify 500-850ms target from RISK-1
- **[Low Priority]** Update test assertions when real Ragas implemented - replace hardcoded 0.0 score expectations

---

**Epic 2 Tech Spec Status**: ✅ **Complete - Ready for Implementation**
