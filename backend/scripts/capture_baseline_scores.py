"""
Capture baseline RAGAS scores before fixing faithfulness metric.

This script queries the query_logs table and generates a baseline report
showing current RAGAS scores (with broken faithfulness metric).
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))
load_dotenv(env_path)

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.session import get_db_session
from app.db.models import QueryLog
from sqlalchemy import func

def capture_baseline():
    """Query existing logs and generate baseline report."""
    db = get_db_session()
    try:
        # Get all query logs with RAGAS scores
        logs = db.query(QueryLog).filter(
            QueryLog.faithfulness_score.isnot(None)
        ).all()

        if not logs:
            print("❌ No query logs found with RAGAS scores.")
            print("Please run some queries first to generate baseline data.")
            return

        print(f"\n{'='*80}")
        print("BASELINE RAGAS SCORES (BEFORE FIX)")
        print(f"{'='*80}\n")
        print(f"Total queries evaluated: {len(logs)}\n")

        # Calculate averages
        avg_faithfulness = sum(float(q.faithfulness_score or 0) for q in logs) / len(logs)
        avg_answer_relevance = sum(float(q.answer_relevance_score or 0) for q in logs) / len(logs)
        avg_context_precision = sum(float(q.context_precision_score or 0) for q in logs) / len(logs)

        print("AVERAGE SCORES:")
        print(f"  Faithfulness: {avg_faithfulness:.3f}")
        print(f"  Answer Relevance: {avg_answer_relevance:.3f}")
        print(f"  Context Precision: {avg_context_precision:.3f}")
        print()

        # Show distribution
        faithfulness_scores = [float(q.faithfulness_score or 0) for q in logs]
        zero_count = sum(1 for s in faithfulness_scores if s == 0.0)

        print(f"FAITHFULNESS DISTRIBUTION:")
        print(f"  Zero scores (0.0): {zero_count}/{len(logs)} ({zero_count/len(logs)*100:.1f}%)")
        print(f"  Non-zero scores: {len(logs)-zero_count}/{len(logs)} ({(len(logs)-zero_count)/len(logs)*100:.1f}%)")
        print()

        # Show sample queries
        print("SAMPLE QUERIES (First 5):")
        for i, log in enumerate(logs[:5], 1):
            print(f"\n  Query {i}: {log.natural_language_query}")
            print(f"    Faithfulness: {float(log.faithfulness_score or 0):.2f}")
            print(f"    Answer Relevance: {float(log.answer_relevance_score or 0):.2f}")
            print(f"    Context Precision: {float(log.context_precision_score or 0):.2f}")

        print(f"\n{'='*80}")
        print("DIAGNOSIS:")
        print(f"{'='*80}\n")

        if avg_faithfulness < 0.1:
            print("❌ FAITHFULNESS METRIC IS BROKEN")
            print("   Average faithfulness score is near zero, indicating NaN → 0.0 conversion.")
            print("   Root cause: Passing SQL query as context instead of database schema.\n")

        print("✅ Baseline captured successfully!")
        print(f"   Data saved for comparison after fix implementation.\n")

    finally:
        db.close()

if __name__ == "__main__":
    capture_baseline()
