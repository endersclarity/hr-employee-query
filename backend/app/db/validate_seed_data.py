"""
Validation script for seed data - ensures test scenarios are covered.
This is the integration checkpoint for Story 1.5 readiness.
"""
import os
import sys

# Add backend to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from sqlalchemy import text
from app.db.session import get_engine


def validate_test_queries():
    """
    Validate that seed data covers all mandatory test scenarios for Story 1.5.

    Test scenarios:
    1. Recent hires (last 6 months) - min 5 employees
    2. Engineering high earners (>120K USD) - min 3 employees
    3. Parental leave - min 2 employees
    4. John Doe reports - min 4 employees

    Returns:
        dict: Results for each test scenario with actual counts
    """
    print("=" * 60)
    print("INTEGRATION CHECKPOINT: Story 1.5 Seed Data Validation")
    print("=" * 60)

    engine = get_engine()

    with engine.connect() as conn:
        # Test all 4 mandatory query scenarios
        tests = [
            ("Recent hires (last 6 months)",
             "SELECT COUNT(*) FROM employees WHERE hire_date >= CURRENT_DATE - INTERVAL '6 months'",
             5,
             "Query: 'Show me employees hired in the last 6 months'"),
            ("Engineering high earners (>120K USD)",
             "SELECT COUNT(*) FROM employees WHERE department = 'Engineering' AND salary_usd > 120000",
             3,
             "Query: 'List Engineering employees with salary greater than 120K'"),
            ("Parental leave",
             "SELECT COUNT(*) FROM employees WHERE leave_type = 'Parental Leave'",
             2,
             "Query: 'Who is on parental leave?'"),
            ("John Doe reports",
             "SELECT COUNT(*) FROM employees WHERE manager_name = 'John Doe'",
             4,
             "Query: 'Show employees managed by John Doe'"),
        ]

        results = {}
        all_passed = True

        print("\nValidating test scenarios:\n")

        for name, query, min_count, example_query in tests:
            result = conn.execute(text(query))
            actual_count = result.scalar()

            passed = actual_count >= min_count
            status = "✓ PASS" if passed else "✗ FAIL"

            results[name] = {
                "expected_min": min_count,
                "actual": actual_count,
                "passed": passed,
                "example_query": example_query
            }

            print(f"{status} {name}")
            print(f"     Required: >= {min_count} | Actual: {actual_count}")
            print(f"     Example NL Query: {example_query}")
            print()

            if not passed:
                all_passed = False

        # Summary
        print("=" * 60)
        if all_passed:
            print("✅ CHECKPOINT PASSED: All test scenarios validated")
            print("✅ Seed data is ready for Story 1.5 (NL→SQL conversion)")
            print("\nActual counts for Story 1.5 testing:")
            for name, data in results.items():
                print(f"  • {name}: {data['actual']} records")
        else:
            print("❌ CHECKPOINT FAILED: Some test scenarios did not meet requirements")
            print("❌ Story 1.5 CANNOT start until seed data is fixed")
            sys.exit(1)

        print("=" * 60)

        return results


if __name__ == "__main__":
    try:
        results = validate_test_queries()
    except Exception as e:
        print(f"\n❌ Validation failed with error: {e}")
        sys.exit(1)
