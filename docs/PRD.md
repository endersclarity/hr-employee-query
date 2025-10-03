# Natural Language HR Employee Records Query Application Product Requirements Document (PRD)

**Author:** Kaelen
**Date:** 2025-10-01
**Project Level:** Level 2 (Small complete system)
**Project Type:** Web application (full-stack)
**Target Scale:** 8-12 stories across 1-2 epics

---

## Description, Context and Goals

**Natural Language HR Employee Records Query Application** is a full-stack web application that enables users to query HR employee records using natural language. The system converts natural language queries into SQL statements using LLM integration, executes them against an employee database, and returns results in a user-friendly tabular format. The application includes a Ragas evaluation framework to assess query accuracy, faithfulness, and relevance. Built as a job interview demonstration to showcase systematic development methodology, technical implementation skills, and ability to deliver complete working systems.

### Deployment Intent

Demo/POC for job interview presentation (October 12th, 2025), with production-quality architecture and security considerations. Deployable to cloud platforms (AWS/Azure/GCP) via Docker containers, suitable for live demonstration and code review.

### Context

This application addresses the growing need for intuitive database interfaces that don't require SQL expertise. Traditional database querying requires technical knowledge, creating barriers for HR professionals and business users. By leveraging LLMs to convert natural language to SQL, this system democratizes data access while maintaining security and accuracy through evaluation frameworks. The project serves dual purposes: solving a real-world usability problem while demonstrating technical competency in a job interview context.

### Goals

1. **Demonstrate End-to-End Delivery**: Build a complete working system from requirements through deployment, showcasing ability to ship functional software despite knowledge gaps in specific technologies (Ragas, NL→SQL patterns)

2. **Show Systematic Methodology**: Document the entire development process using BMad Method workflows, demonstrating structured thinking, risk identification (pre-mortem), research-driven learning, and systematic problem-solving

3. **Implement Production-Quality Patterns**: Deliver secure, evaluated, and well-architected code with multi-layered security (SQL injection prevention), LLM evaluation metrics (Ragas), and professional deployment practices (Docker, cloud-ready)

## Requirements

### Functional Requirements

**FR001**: Users shall enter natural language queries through a text input interface with a submit button

**FR002**: System shall convert natural language queries to valid SQL statements using LLM integration (OpenAI or Anthropic)

**FR003**: System shall execute generated SQL queries against the HR employee database

**FR004**: System shall display query results in a tabular format with appropriate column headers

**FR005**: System shall handle the following mandatory query types:
- Employees hired within a date range (e.g., "last 6 months")
- Employees filtered by department and salary criteria (e.g., "Engineering with salary > 120K")
- Employees filtered by leave type (e.g., "on parental leave")
- Employees filtered by manager name (e.g., "managed by John Doe")

**FR006**: System shall validate generated SQL queries before execution (whitelist SELECT statements only, block DELETE/DROP/UPDATE/INSERT)

**FR007**: System shall evaluate query results using Ragas framework metrics (Faithfulness, Answer Relevance, Context Precision)

**FR008**: System shall display Ragas evaluation scores alongside query results

**FR009**: System shall log all queries and their evaluation metrics for analysis

**FR010**: System shall provide error messages when queries cannot be processed or when malicious intent is detected

**FR011**: System shall support database schema inspection for the LLM prompt context

**FR012**: System shall maintain a read-only connection to the employee database to prevent data modification

**FR013**: Backend shall expose a REST API endpoint to accept natural language query requests and return JSON responses

**FR014**: System shall provide comparative evaluation reports across multiple queries, showing Ragas score trends and weak spots

**FR015**: System shall generate actionable recommendations for improving low-scoring queries (e.g., schema-based prompting suggestions, few-shot example needs)

### Non-Functional Requirements

**NFR001**: **Security** - System shall implement multi-layered security including database-level read-only permissions, prompt engineering safeguards, input sanitization, and SQL query validation to prevent injection attacks

**NFR002**: **Performance** - System shall respond to natural language queries within 5 seconds (including LLM processing, SQL execution, and Ragas evaluation)

**NFR003**: **Deployment** - System shall be containerized using Docker with docker-compose support for local execution and cloud-agnostic deployment to AWS, Azure, or GCP

**NFR004**: **Evaluation Quality** - System shall maintain Ragas scores of 0.7+ (Acceptable) for all mandatory query types, with target scores of 0.8+ (Good) for simple queries

**NFR005**: **Documentation** - System shall include comprehensive README, architecture diagrams, deployment instructions, and a Project Report documenting the development methodology

## User Journeys

**Primary User Journey: HR Professional Queries Employee Data**

1. **User** opens the application in web browser
2. **User** sees a clean interface with an input box and submit button
3. **User** enters natural language query: "Show me employees in Engineering with salary greater than 120K"
4. **User** clicks submit button
5. **System** displays loading indicator while processing
6. **System** converts query to SQL using LLM
7. **System** validates SQL (ensures SELECT only, no malicious operations)
8. **System** executes query against employee database
9. **System** evaluates results using Ragas (Faithfulness, Answer Relevance, Context Precision)
10. **System** displays results in a table with columns: employee_id, first_name, last_name, salary_usd
11. **System** displays Ragas scores below the table (e.g., Faithfulness: 0.92, Answer Relevance: 0.88, Context Precision: 0.85)
12. **User** reviews results and can enter another query

**Alternative Flow - Query Fails Validation:**
- At step 7, if malicious query detected (e.g., "DELETE all employees")
- **System** displays error: "Query validation failed. Only SELECT queries are permitted."
- **User** can modify and resubmit query

## UX Design Principles

1. **Simplicity First** - Minimal interface with single input field and submit button; no complex navigation or overwhelming options

2. **Immediate Feedback** - Clear loading indicators during processing, instant error messages for invalid queries, visible Ragas scores to build trust

3. **Transparency** - Display the generated SQL query (optional toggle) so users understand what's happening behind the scenes

4. **Error Recovery** - Helpful error messages that guide users toward valid queries rather than technical jargon

5. **Progressive Disclosure** - Start with basic results table, allow users to expand/view Ragas metrics details on demand

## Epics

**Epic 1: Core NL-to-SQL Query Application** (8 stories)
- Set up project structure and dependencies
- Implement React frontend with input/submit/table UI
- Create FastAPI backend with REST API endpoint
- Design and populate employee database with mock data
- Integrate LLM for NL→SQL conversion with schema-aware prompting
- Implement SQL query validation and security layer
- Execute SQL queries and return JSON results
- Display results in tabular format

**Epic 2: Ragas Evaluation & Reporting** (4 stories)
- Integrate Ragas framework into backend
- Implement Faithfulness, Answer Relevance, and Context Precision metrics
- Display Ragas scores in frontend
- Generate comparative evaluation reports and recommendations

_See `epic-stories.md` for detailed story breakdown with acceptance criteria and dependencies._

## Out of Scope

The following features are explicitly excluded from this MVP to maintain focus on core demonstration objectives:

**Advanced Features:**
- Multi-user authentication and authorization
- Query history persistence across sessions
- Saved queries or query templates
- Advanced data visualizations (charts, graphs)
- Query result export (CSV, Excel)
- Real-time query collaboration

**Production Enhancements:**
- Multi-tenant database architecture
- Horizontal scaling and load balancing
- Comprehensive audit logging and compliance
- Advanced rate limiting and DDoS protection
- Automated backup and disaster recovery

**Extended LLM Capabilities:**
- Multi-turn conversational query refinement
- Query auto-completion or suggestions
- Natural language query explanations
- Support for complex JOIN operations or aggregations beyond simple filters

**Database Extensions:**
- Write operations (INSERT, UPDATE, DELETE)
- Multiple database connections
- Support for non-HR database schemas
- Database schema migration tools

_These features may be considered for future iterations if the demo is well-received._

---

## Next Steps

### Phase 3: Solution Architecture & Design (NEXT)

**Required Actions:**
1. **Run solutioning workflow** with Architect agent
   - Input: This PRD + `epic-stories.md` + `docs/Research/Comprehensive Research Report_ Ragas Evaluation Fr.md`
   - Output: `solution-architecture.md` with system flow diagrams
   - Generate per-epic tech specs

2. **Key Architecture Decisions Needed:**
   - Database choice (PostgreSQL vs SQLite)
   - LLM provider (OpenAI vs Anthropic)
   - Cloud platform (AWS vs Azure vs GCP)
   - Container orchestration approach

### Phase 4: Implementation

**After Architecture Complete:**
1. Use Scrum Master agent to generate detailed stories with `story-context` (BMad v6 feature)
2. Begin development following epic sequence
3. Implement Epic 1 (Core Application) first
4. Add Epic 2 (Ragas Evaluation) second
5. Deploy and test end-to-end

### Demo Preparation

**Before October 12th Presentation:**
- Test all 4 mandatory query examples
- Create visual architecture diagram
- Rehearse Ragas metrics explanation
- Test cloud deployment 48+ hours early
- Prepare backup plan (screenshots/video)
- Practice answering: "How do you prevent SQL injection?"

## Document Status

- [x] Goals and context validated with stakeholders
- [x] All functional requirements reviewed
- [x] User journeys cover all major personas
- [x] Epic structure approved for phased delivery
- [x] Ready for architecture phase

_Note: See technical-decisions.md for captured technical context_

---

_This PRD adapts to project level Level 2 - providing appropriate detail without overburden._
