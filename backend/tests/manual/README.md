# Manual Testing Harness

This directory contains manual test scripts for hypothesis verification and debugging.

## RAGAS Local Testing

**Purpose:** Test RAGAS faithfulness locally without deploying to Railway

**File:** `test_ragas_local.py`

### Prerequisites

1. **Python environment set up:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **OpenAI API key configured:**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   # OR add to backend/.env file
   ```

### Running the Test

```bash
cd backend
python -m tests.manual.test_ragas_local
```

### What It Tests

1. **Test 1: Current Implementation**
   - Uses exact same data structure as production
   - Tests if faithfulness returns 0.0 locally
   - **If it FAILS locally:** We can test fixes safely
   - **If it PASSES locally:** Problem is environment-specific

2. **Test 2: Hypothesis #1 (Format Mismatch)**
   - Placeholder for testing matching answer/context formats
   - Requires code modification to run

3. **Test 3: Hypothesis #2 (LLM Configuration)**
   - Placeholder for testing explicit LLM setup
   - Requires code modification to run

### Expected Output

```
🧪 RAGAS LOCAL TESTING HARNESS 🧪

✅ OPENAI_API_KEY: ********************xyz

Initializing RAGAS...
✅ RAGAS initialized

TEST 1: Current Implementation (Production Format)
Query: Show me all employees in Engineering
Results: 2 records

Evaluating...

RESULTS:
  Faithfulness: 0.0 or >0.0
  Answer Relevance: ~0.85-0.90
  Context Utilization: ~0.95-1.0

✅ SUCCESS or 🔴 FAIL
```

### Next Steps Based on Results

**If Test 1 FAILS (faithfulness = 0.0):**
- ✅ Issue reproduces locally
- ✅ Can test hypotheses without deploying
- Proceed with hypothesis verification

**If Test 1 PASSES (faithfulness > 0.0):**
- ⚠️ Issue is environment-specific
- Compare Railway vs local:
  - Environment variables
  - Package versions (`pip freeze`)
  - Python version
  - Docker vs native execution

## Troubleshooting

**Error: "OPENAI_API_KEY not set"**
- Solution: `export OPENAI_API_KEY="sk-..."`

**Error: "No module named 'ragas'"**
- Solution: `pip install -r requirements.txt`

**Error: "ImportError: cannot import name 'evaluate'"**
- Solution: Check ragas version matches requirements.txt

## Adding New Tests

To test a hypothesis:

1. Create a new async function `test_hypothesis_N()`
2. Call it from `main()`
3. Document what you're testing and why
4. Return True/False for pass/fail
