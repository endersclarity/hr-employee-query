# Natural Language HR Employee Records Query Application - Epic Breakdown

**Author:** Kaelen
**Date:** 2025-10-01
**Project Level:** Level 2 (Small complete system)
**Target Scale:** 12 stories across 2 epics

---

## Epic Overview

This project consists of two primary epics that together deliver a complete NL-to-SQL query application with evaluation capabilities:

**Epic 1: Core NL-to-SQL Query Application** - Foundation of the system including frontend, backend, database, LLM integration, and security. Delivers the primary user-facing functionality.

**Epic 2: Ragas Evaluation & Reporting** - Quality assurance layer that evaluates query accuracy and provides insights for improvement. Differentiates this demo with production-quality evaluation.

---

## Epic Details

### Epic 1: Core NL-to-SQL Query Application

**Epic Goal:** Build a secure, functional web application that converts natural language queries to SQL and returns employee data results.

**Story Count:** 8 stories

**Stories:**

1. **Story 1.1: Project Foundation & Environment Setup**
   - Set up React + FastAPI project structure
   - Configure Docker and docker-compose
   - Establish development environment
   - Set up version control and basic CI/CD
   - **Acceptance Criteria:** `docker-compose up` successfully starts frontend and backend

2. **Story 1.2: Database Schema & Mock Data**
   - Create employees table with 11 required fields
   - Design mock dataset aligned with 4 example queries
   - Ensure "John Doe" exists as manager, employees in Engineering >120K, recent hires, parental leave cases
   - Implement database initialization scripts
   - **Acceptance Criteria:** Database contains 50+ employee records covering all query scenarios

3. **Story 1.3: React Frontend UI**
   - Create simple interface with text input, submit button, and results table
   - Implement loading indicators and error display
   - Add basic styling for clean presentation
   - **Acceptance Criteria:** UI renders correctly, handles user input, displays placeholder results

4. **Story 1.4: FastAPI Backend & REST API**
   - Create FastAPI application structure
   - Implement POST /query endpoint accepting natural language input
   - Return JSON responses with results and metadata
   - Add CORS configuration for frontend integration
   - **Acceptance Criteria:** API endpoint accepts requests and returns structured JSON

5. **Story 1.5: LLM Integration for NL→SQL**
   - Integrate OpenAI or Anthropic SDK
   - Implement schema-aware system prompt with employee table schema
   - Add few-shot examples for reliable query generation
   - Handle LLM API errors and timeouts
   - **Acceptance Criteria:** LLM successfully converts all 4 example queries to valid SQL

6. **Story 1.6: SQL Validation & Security Layer**
   - Implement SQL query validator (whitelist SELECT only)
   - Add input sanitization to detect malicious patterns
   - Block DELETE/DROP/UPDATE/INSERT/ALTER commands
   - Create read-only database connection
   - **Acceptance Criteria:** Malicious queries rejected, only SELECT queries execute

7. **Story 1.7: SQL Execution & Results Processing**
   - Execute validated SQL against employee database
   - Handle SQL errors gracefully
   - Transform results to JSON format
   - Implement result set limiting (max 1000 rows)
   - **Acceptance Criteria:** Queries execute successfully, results returned in expected format

8. **Story 1.8: Frontend-Backend Integration**
   - Connect React frontend to FastAPI backend
   - Display query results in table format
   - Show generated SQL query (optional toggle)
   - Implement error handling and user feedback
   - **Acceptance Criteria:** End-to-end flow works for all 4 example queries

---

### Epic 2: Ragas Evaluation & Reporting

**Epic Goal:** Implement comprehensive evaluation framework to assess query quality and provide actionable insights.

**Story Count:** 4 stories

**Stories:**

1. **Story 2.1: Ragas Framework Integration**
   - Install and configure Ragas Python library
   - Set up evaluator LLM and embeddings
   - Create evaluation pipeline infrastructure
   - **Acceptance Criteria:** Ragas successfully initializes, can run basic evaluations

2. **Story 2.2: Implement Core Ragas Metrics**
   - Implement Faithfulness metric (schema consistency check)
   - Implement Answer Relevance metric (intent alignment)
   - Implement Context Precision metric (relevant field selection)
   - Configure metrics for NL-to-SQL context
   - **Acceptance Criteria:** All 3 metrics calculate scores (0.6-1.0 range) for sample queries

3. **Story 2.3: Display Evaluation Scores in Frontend**
   - Add Ragas scores display below results table
   - Show Faithfulness, Answer Relevance, Context Precision
   - Implement score interpretation (color coding: green >0.8, yellow 0.7-0.8, red <0.7)
   - Add expandable details for metric explanations
   - **Acceptance Criteria:** Scores visible and color-coded appropriately

4. **Story 2.4: Comparative Reports & Recommendations**
   - Log all queries with timestamps and Ragas scores
   - Generate comparative analysis across multiple queries
   - Identify weak spots (low-scoring queries)
   - Generate actionable recommendations (improve prompting, add few-shot examples, etc.)
   - Create report export functionality
   - **Acceptance Criteria:** Report shows score trends, identifies issues, provides specific improvement suggestions

---

## Story Dependencies

**Sequential Dependencies:**
- Story 1.2 must complete before 1.7 (need database for SQL execution)
- Story 1.5 must complete before 1.6 (need SQL generation before validation)
- Story 1.8 depends on 1.3, 1.4, 1.7 (integration requires all components)
- Epic 2 stories depend on Epic 1 completion (need working queries to evaluate)

**Parallel Work Opportunities:**
- Stories 1.2, 1.3, 1.4 can be developed in parallel
- Stories 2.1, 2.2 can start once basic query flow works (after 1.7)
- Frontend and backend work can proceed independently until integration (1.8)

---

## Estimated Timeline

**Epic 1:** 5-7 days (assuming full-time work)
**Epic 2:** 2-3 days
**Total:** 7-10 days of development + testing/refinement

---

_This epic structure provides clear development phases while maintaining flexibility for iterative refinement._
