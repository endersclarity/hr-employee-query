"""
Manual test script to verify RAGAS faithfulness locally.

This script tests the RAGAS evaluation service in isolation to help diagnose
why faithfulness returns NaN in production.

Usage:
    cd backend
    python -m tests.manual.test_ragas_local

Environment Requirements:
    - OPENAI_API_KEY must be set
    - ragas, datasets, langchain packages installed

Test Objectives:
    1. Verify if faithfulness issue reproduces locally
    2. Test Hypothesis #1: Format mismatch between answer and context
    3. Test Hypothesis #2: Missing LLM configuration
    4. Gather evidence for root cause analysis
"""

import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.services.ragas_service import evaluate, initialize_ragas


async def test_current_implementation():
    """Test with current production code (exact same data structure)."""
    print("\n" + "="*80)
    print("TEST 1: Current Implementation (Production Format)")
    print("="*80)

    nl_query = "Show me all employees in Engineering"
    sql = "SELECT * FROM employees WHERE department = 'Engineering'"

    # Mock results matching production format
    results = [
        {
            "employee_id": 1,
            "first_name": "Emma",
            "last_name": "Watson",
            "department": "Engineering",
            "role": "Senior Engineer",
            "employment_status": "Active",
            "hire_date": "2023-01-15",
            "salary_usd": 120000
        },
        {
            "employee_id": 2,
            "first_name": "John",
            "last_name": "Doe",
            "department": "Engineering",
            "role": "Staff Engineer",
            "employment_status": "Active",
            "hire_date": "2022-06-01",
            "salary_usd": 135000
        }
    ]

    print(f"\nQuery: {nl_query}")
    print(f"Results: {len(results)} records")
    print("\nEvaluating...")

    scores = await evaluate(nl_query, sql, results)

    if scores is None:
        print("\n[X] EVALUATION FAILED - returned None")
        print("Check logs above for errors")
        return False

    print("\n" + "-"*80)
    print("RESULTS:")
    print(f"  Faithfulness: {scores['faithfulness']}")
    print(f"  Answer Relevance: {scores['answer_relevance']}")
    print(f"  Context Utilization: {scores['context_utilization']}")
    print("-"*80)

    # Check success criteria
    if scores['faithfulness'] == 0.0:
        print("\n[FAIL] Faithfulness still returns 0.0 (issue REPRODUCES locally)")
        return False
    elif scores['faithfulness'] > 0.0:
        print(f"\n[SUCCESS] Faithfulness working! Score: {scores['faithfulness']}")
        print("   Issue does NOT reproduce locally - environment difference confirmed")
        return True

    return False


async def test_hypothesis_1_format_match():
    """
    Test Hypothesis #1: Format mismatch
    Make answer and context formats identical to see if faithfulness works.
    """
    print("\n" + "="*80)
    print("TEST 2: Hypothesis #1 - Matching Formats")
    print("="*80)
    print("Testing if making answer/context formats identical fixes faithfulness...")

    # This test would require modifying ragas_service.py
    # For now, document what needs to be tested
    print("\n[WARNING] This requires code modification to ragas_service.py")
    print("    Modify lines 106-132 to use matching formats")
    print("    Skipping for now - run after confirming Test 1 results")


async def test_hypothesis_2_llm_config():
    """
    Test Hypothesis #2: Missing LLM configuration
    Explicitly configure LLM for RAGAS metrics.
    """
    print("\n" + "="*80)
    print("TEST 3: Hypothesis #2 - Explicit LLM Configuration")
    print("="*80)
    print("Testing if explicitly configuring LLM fixes faithfulness...")

    print("\n[WARNING] This requires importing and configuring ChatOpenAI")
    print("    from langchain.chat_models import ChatOpenAI")
    print("    Skipping for now - will implement if Test 1 passes")


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("RAGAS LOCAL TESTING HARNESS")
    print("="*80)

    # Check prerequisites
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n[ERROR] OPENAI_API_KEY not set")
        print("   Set it in your environment or .env file")
        return 1

    print(f"\n[OK] OPENAI_API_KEY: {'*' * 20}{api_key[-4:]}")

    # Initialize RAGAS
    print("\nInitializing RAGAS...")
    try:
        result = await initialize_ragas()
        if result:
            print("[OK] RAGAS initialized")
        else:
            print("[WARNING] RAGAS initialization returned False")
    except Exception as e:
        print(f"[ERROR] RAGAS initialization failed: {e}")
        return 1

    # Run tests
    try:
        test1_passed = await test_current_implementation()

        # Only run additional tests if needed
        if not test1_passed:
            print("\n" + "="*80)
            print("Test 1 failed - faithfulness issue reproduces locally")
            print("This is GOOD for debugging - we can test fixes locally")
            print("="*80)

            # Placeholder for future tests
            await test_hypothesis_1_format_match()
            await test_hypothesis_2_llm_config()

        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print("\nNext Steps:")
        if test1_passed:
            print("  1. Issue does NOT reproduce locally")
            print("  2. Problem is environment-specific (Railway vs local)")
            print("  3. Compare Railway env vars, package versions, Python version")
        else:
            print("  1. Issue DOES reproduce locally")
            print("  2. Can test fixes safely without deploying to Railway")
            print("  3. Proceed with hypothesis testing locally")

        print("\n")
        return 0 if test1_passed else 1

    except Exception as e:
        print(f"\n[ERROR] TEST ERROR: {e}")
        import traceback
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
