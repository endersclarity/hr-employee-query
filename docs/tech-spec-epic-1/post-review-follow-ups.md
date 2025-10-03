# Post-Review Follow-ups

These action items emerged from the Story 1.1 Senior Developer Review (2025-10-02):

### High Priority (Blocks Downstream Stories)

1. **Backend Module Structure Incomplete** (Story 1.1)
   - **Issue**: Missing api/, services/, db/, utils/ subdirectories with __init__.py files
   - **Impact**: Blocks Stories 1.4, 1.5, 1.6, 1.7 which assume modular structure exists
   - **Action**: Create placeholder directories before proceeding with Story 1.2
   - **Ref**: backend/app/, tech-spec lines 186-204

2. **Environment Variable Parsing Security** (Story 1.1)
   - **Issue**: validate-env.sh uses unsafe `export $(cat .env ...)` pattern vulnerable to command injection
   - **Impact**: Security risk if .env contains malicious values
   - **Action**: Replace with `set -a; source <(grep -v '^#' .env); set +a` pattern
   - **Ref**: scripts/validate-env.sh:7-9

3. **React Version Mismatch** (Story 1.1)
   - **Issue**: React 19.1.1 installed but tech spec requires 18.3.1 (line 51)
   - **Impact**: Potential breaking changes affecting Story 1.3 and 1.8 integrations
   - **Action**: Either downgrade to 18.3.1 OR update tech spec with ADR justifying React 19
   - **Ref**: frontend/package.json:13-14, tech-spec-epic-1.md:51

### Medium Priority (Improves Quality)

4. **Health Check Database Connectivity** (Story 1.1)
   - **Issue**: /api/health returns static response, doesn't test actual DB connection
   - **Action**: Add SQLAlchemy connection test (can be deferred to Story 1.4)
   - **Ref**: backend/app/main.py:25-32, tech-spec-epic-1.md:249-267

5. **docker-compose.override.yml.example Outdated** (Story 1.1)
   - **Issue**: Example references port 8000 but production uses port 9000
   - **Action**: Update port references in override example
   - **Ref**: docker-compose.override.yml.example:13-16

6. **Frontend Placeholder** (Story 1.1)
   - **Issue**: App.jsx still has Vite default boilerplate
   - **Action**: Replace with branded placeholder for Story 1.3 prep
   - **Ref**: frontend/src/App.jsx:1-35

### Low Priority (Future Enhancement)

7. **.dockerignore Optimization** (Story 1.1)
   - **Action**: Create .dockerignore for frontend and backend to reduce build context
   - **Ref**: Best practices gap identified in review

8. **API Key Validation** (Story 1.1)
   - **Action**: Add format validation in validate-env.sh (check for sk- prefix)
   - **Ref**: scripts/validate-env.sh, .env.example

9. **Node.js Version Documentation** (Story 1.1)
   - **Action**: Resolve discrepancy between Dockerfile (Node 18) and tech spec (Node 20)
   - **Ref**: frontend/Dockerfile:1, story-1.1.md:243

---

## Story 1.6 Review Follow-ups (2025-10-02)

### Medium Priority

10. **Harden Table Name Validation** (Story 1.6)
    - **Issue**: Current substring check `'employees' in sql.lower()` could allow `employees_backup` or `fake_employees`
    - **Impact**: Weakens defense-in-depth, though low probability (LLM unlikely to hallucinate table names)
    - **Action**: Use sqlparse to extract table names and validate exact match against whitelist
    - **Suggested Code**:
      ```python
      from sqlparse.sql import IdentifierList, Identifier
      tables = []
      for token in stmt.tokens:
          if isinstance(token, Identifier):
              tables.append(token.get_real_name())
          elif isinstance(token, IdentifierList):
              tables.extend([id.get_real_name() for id in token.get_identifiers()])
      if tables and 'employees' not in [t.lower() for t in tables]:
          raise ValueError("Only 'employees' table permitted")
      ```
    - **Ref**: backend/app/services/validation_service.py:101-108

### Low Priority

11. **Fix Deprecated datetime.utcnow()** (Story 1.6)
    - **Issue**: Uses deprecated `datetime.utcnow()` instead of `datetime.now(datetime.UTC)`
    - **Action**: One-line fix in health endpoint
    - **Ref**: backend/app/api/routes.py:107

12. **Add Explicit Type Hints** (Story 1.6)
    - **Action**: Add `-> bool:` return type annotation to `validate_sql()` for consistency
    - **Ref**: backend/app/services/validation_service.py:41

13. **Standardize Error Messages** (Story 1.6)
    - **Action**: Use "allowed" or "permitted" consistently (currently mixed)
    - **Ref**: backend/app/services/validation_service.py:82, 98
