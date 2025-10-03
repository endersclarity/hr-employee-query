# Brainstorming Session Results

**Session Date:** 2025-10-01
**Facilitator:** Business Analyst Mary
**Participant:** Kaelen

## Executive Summary

**Topic:** Natural Language HR Employee Records Query Application

**Session Goals:** Broad exploration across all areas - Technical Approaches, LLM Integration, Security, Ragas Evaluation, UX, and Feature Ideas

**Techniques Used:** Mind Mapping (partial session)

**Total Ideas Generated:** 1 core strategic insight

### Key Themes Identified:

- **Interview Demo Focus**: This is a job interview demonstration project, not production software
- **MVP Scope Clarity**: Clear acceptance criteria already defined in assignment document
- **Process > Perfection**: Demonstrating structured methodology (BMad) is as important as the technical implementation
- **Trust the Workflow**: Use BMad research, elicitation, and iteration to fill knowledge gaps (Ragas, NL→SQL prompt engineering)

## Technique Sessions

### Mind Mapping Session (15 min)

**Goal:** Map out all components and decisions for the NL-to-SQL HR application

**Key Insights:**
- Initial mapping explored technical components (Frontend, Backend, Database, LLM, Ragas, Security, Deployment, UX)
- Pivotal realization: This is an **interview demonstration**, not a production project
- Shifted focus from "perfect architecture" to "working demo that proves ability to ship"
- Recognized the actual requirements are clearly defined in the assignment document

**MVP Definition Captured (Initial):**
```
✓ React frontend: Input box + submit + table results
✓ FastAPI backend: REST API + OpenAI NL→SQL + execute queries + JSON response
✓ Database: employees table (11 fields) with mock data
✓ Must handle 4 example queries (6-month hires, Engineering >120K, parental leave, manager filter)
✓ Ragas evaluation: Faithfulness, Answer Relevance, Context Precision scores (0-1 scale)
✓ Deployment: Docker containers + docker-compose + cloud deployment + secret management
✓ Documentation: README + Project Report
```

### Pre-mortem Elicitation Session (10 min)

**Technique:** Pre-mortem Analysis to identify gaps and failure points

**Critical Additions Identified:**

**1. Mock Data Design Strategy**
- ✓ Mock data MUST align with example queries
- ✓ Ensure "John Doe" exists as manager_name
- ✓ Ensure employees hired within last 6 months exist
- ✓ Ensure Engineering department employees with salary_usd > 120000 exist
- ✓ Ensure employees with leave_type = "Parental Leave" exist
- ✓ Design test dataset intentionally for demo success

**2. Security & Validation Layer**
- ✓ SQL query validator (whitelist SELECT only, block DELETE/DROP/UPDATE/INSERT)
- ✓ Input sanitization against SQL injection via natural language
- ✓ Rate limiting on API endpoints
- ✓ API key management strategy documented in Project Report
- ✓ Error handling for malicious queries

**3. Ragas Success Criteria & Understanding**
- ✓ Research baseline: What are "good" Ragas scores? (>0.7? >0.8?)
- ✓ Understand how to interpret Faithfulness, Answer Relevance, Context Precision
- ✓ Document how to improve low scores (schema prompting, few-shot examples, etc.)
- ✓ Create actionable recommendations, not generic platitudes

**4. Testing & Validation Plan**
- ✓ Test all 4 example queries before demo day
- ✓ Identify and document 2-3 actual "weak spots" from testing
- ✓ Create comparative results table across queries
- ✓ Test edge cases (ambiguous queries, misspellings, date format variations)
- ✓ Validate Ragas scores make sense for each query type

**5. Demo Day Preparation**
- ✓ Create visual architecture diagram (NL query → LLM → SQL → DB → Results → Ragas)
- ✓ Rehearse explanation of Ragas metrics (why each matters)
- ✓ Rehearse NL→SQL prompt engineering choices
- ✓ Test cloud deployment 48+ hours before presentation
- ✓ Backup plan: Screenshots/video recording if live demo fails
- ✓ Practice answering: "How do you prevent SQL injection via natural language?"

**6. Enhanced Project Report Requirements**
- ✓ System flow diagram (visual)
- ✓ Prompt engineering rationale section
- ✓ Ragas metrics interpretation guide
- ✓ Known limitations & weaknesses section (honesty = credibility)
- ✓ Recommendations section with specific, actionable improvements

**Strategic Decision:** MVP expanded with critical gaps filled. Move to BMad workflow execution (research → planning → architecture → build)

## Immediate Next Steps

### #1 Priority: Deep Research on Ragas Evaluation Framework ✅ COMPLETED

- **Rationale:** Unfamiliar technology that's critical to requirements and differentiates this demo
- **Status:** COMPLETED via Perplexity deep research
- **Output:** `C:\Users\ender\.claude\projects\Amit\docs\Research\Comprehensive Research Report_ Ragas Evaluation Fr.md`
- **Key Findings:**
  - Ragas scores cluster 0.6-1.0 (not 0.0-1.0) due to OpenAI embedding limitations
  - Baseline expectations: 0.9-1.0 = Excellent, 0.8-0.9 = Good, 0.7-0.8 = Acceptable, 0.6-0.7 = Poor
  - Three core metrics: Faithfulness (schema consistency), Answer Relevance (intent alignment), Context Precision (field selection)
  - Production-ready Python implementation examples included
  - Schema-aware prompting and few-shot examples significantly improve scores

### #2 Priority: Research NL→SQL Prompt Engineering Patterns ✅ COMPLETED

- **Rationale:** Need reliable LLM-based query conversion without deep expertise
- **Status:** COMPLETED - included in same Perplexity research report
- **Output:** Same file as above (comprehensive coverage of both topics)
- **Key Findings:**
  - Multi-layered security required: database-level permissions + prompt engineering + query validation
  - System prompt template with explicit security constraints (SELECT only, no DDL/DML)
  - Input sanitization pipeline with dangerous keyword detection
  - Few-shot prompt examples for HR employee queries
  - Schema-aware prompting essential for high faithfulness scores
  - Read-only database user with query timeouts and result limits

### #3 Priority: Execute BMad Method Workflow (Phase 1-4)

- **Rationale:** Structured methodology compensates for knowledge gaps and provides documentation for project report
- **Next steps:**
  - Phase 1: Research (Ragas + NL→SQL) → Product brief
  - Phase 2: PRD with scale-adaptive planning
  - Phase 3: Architecture + Tech specs
  - Phase 4: Story-driven implementation
- **Resources needed:** BMad v6 workflows, elicitation techniques
- **Timeline:** Follow natural workflow progression

## Key Realization

**The assignment IS the product brief.** No need to over-brainstorm what's already clearly defined. Move to research and structured execution.

---

_Session facilitated using the BMAD CIS brainstorming framework_
