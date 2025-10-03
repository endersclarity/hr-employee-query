# Evaluation Framework Integration

### Ragas Implementation

**What is Ragas?**
Ragas (Retrieval Augmented Generation Assessment) is a framework for evaluating LLM outputs. We use it to assess the quality of our NL→SQL system.

**Three Metrics:**

1. **Faithfulness (0.6-1.0 scale)**
   - *Question:* Is the SQL query faithful to the database schema?
   - *Checks:* Correct table name, valid columns, proper data types
   - *Target Score:* 0.9+ (Excellent)

2. **Answer Relevance (0.6-1.0 scale)**
   - *Question:* Do the results align with the user's intent?
   - *Checks:* Correct filters applied, appropriate columns returned
   - *Target Score:* 0.8+ (Good)

3. **Context Precision (0.6-1.0 scale)**
   - *Question:* Are only relevant fields included in the response?
   - *Checks:* No unnecessary columns, focused result set
   - *Target Score:* 0.8+ (Good)

**Integration Code:**

```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevance, context_precision

async def evaluate_query_results(
    query: str,
    generated_sql: str,
    results: list,
    schema: dict
) -> dict:
    """Calculate Ragas scores for query results."""

    # Prepare evaluation dataset
    eval_data = {
        'question': query,
        'answer': generated_sql,
        'contexts': [schema],  # Database schema as context
        'ground_truth': results  # Actual DB results
    }

    # Run Ragas evaluation
    scores = evaluate(
        dataset=[eval_data],
        metrics=[faithfulness, answer_relevance, context_precision]
    )

    return {
        'faithfulness': round(scores['faithfulness'][0], 2),
        'answer_relevance': round(scores['answer_relevance'][0], 2),
        'context_precision': round(scores['context_precision'][0], 2)
    }
```

**Score Interpretation (for UI display):**

```python
def get_score_color(score: float) -> str:
    """Return color code for score badge."""
    if score >= 0.9:
        return 'green'  # Excellent
    elif score >= 0.8:
        return 'yellow'  # Good
    elif score >= 0.7:
        return 'orange'  # Acceptable
    else:
        return 'red'  # Poor - needs improvement
```

---
