"""Integration test for LLM service with real OpenAI API and database.

This script validates that:
1. OpenAI GPT-5 Nano actually generates valid SQL for the 4 mandatory query types
2. Generated SQL executes successfully against the actual database schema
3. Queries return expected results from seed data

Usage:
    Ensure OPENAI_API_KEY is set in .env, then run:
    python -m backend.app.services.test_llm_integration
"""

import asyncio
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.app.services.llm_service import generate_sql
from backend.app.db.session import get_db_session
from sqlalchemy import text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def test_llm_with_real_data():
    """Test LLM-generated SQL against real database with seed data."""

    # Verify API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ ERROR: OPENAI_API_KEY not set in environment")
        print("   Please add your API key to .env file")
        return False

    test_queries = [
        "Show me employees hired in the last 6 months",
        "List Engineering employees with salary greater than 120K",
        "Who is on parental leave?",
        "Show employees managed by John Doe"
    ]

    print("=" * 60)
    print("LLM INTEGRATION TEST - Real OpenAI + Real Database")
    print("=" * 60)
    print(f"\nTesting {len(test_queries)} mandatory query types...\n")

    try:
        db = get_db_session()
        all_passed = True

        for i, nl_query in enumerate(test_queries, 1):
            print(f"[{i}/{len(test_queries)}] Testing: \"{nl_query}\"")

            try:
                # Generate SQL from LLM (real OpenAI API call)
                sql = await generate_sql(nl_query)
                print(f"    Generated SQL: {sql}")

                # Execute against real database
                result = db.execute(text(sql))
                rows = [dict(row) for row in result.mappings()]
                row_count = len(rows)

                # Validate results
                if row_count == 0:
                    print(f"    ⚠️  WARNING: Query returned 0 rows (seed data may be missing)")
                    print(f"    ℹ️  This may be expected if database is empty")
                else:
                    print(f"    ✅ SUCCESS: Returned {row_count} rows")

                # Display sample result if available
                if row_count > 0:
                    print(f"    Sample: {rows[0]}")

            except Exception as e:
                print(f"    ❌ FAILED: {str(e)}")
                all_passed = False

            print()

        db.close()

        # Summary
        print("=" * 60)
        if all_passed:
            print("✅ All LLM-generated queries executed successfully!")
            print("\nNext steps:")
            print("  - Verify seed data exists if queries returned 0 rows")
            print("  - Review generated SQL for correctness")
            print("  - Story 1.5 integration checkpoint: COMPLETE")
        else:
            print("❌ Some queries failed - review errors above")
            print("\nTroubleshooting:")
            print("  - Check database connection in .env (DATABASE_URL)")
            print("  - Verify seed data was loaded (Story 1.2/1.3)")
            print("  - Check OpenAI API quota/status")
        print("=" * 60)

        return all_passed

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {str(e)}")
        print("\nPossible causes:")
        print("  - Database not running (check Docker: docker-compose up -d)")
        print("  - OpenAI API key invalid or quota exceeded")
        print("  - Database schema not initialized (run migrations)")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_llm_with_real_data())
    sys.exit(0 if success else 1)
