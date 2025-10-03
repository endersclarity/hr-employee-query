<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# Comprehensive Research Report: Ragas Evaluation Framework for LLM-Generated SQL Queries

## Executive Summary

The research reveals that **Ragas is a mature, production-ready framework** for evaluating LLM-generated SQL queries, with the caveat that **baseline score expectations need recalibration**. Instead of the traditional 0.0-1.0 range, Ragas scores typically cluster between **0.6-1.0 due to OpenAI embedding limitations**. For natural language to SQL applications, security must be **multi-layered**: database-level permissions, prompt engineering safeguards, and query validation systems working in concert.[^1][^2][^3]

## Quick Start Guide

### Installation and Basic Setup

```bash
# Basic installation
pip install ragas

# For latest features
pip install git+https://github.com/explodinggradients/ragas.git

# Required dependencies for SQL evaluation
pip install langchain-openai datasets openai
```

**Essential Dependencies for Text-to-SQL:**

- `ragas`: Core evaluation framework[^4]
- `langchain-openai`: LLM integration[^5]
- `datasets`: Data handling for evaluation sets[^6]
- OpenAI/Anthropic API keys for LLM-based metrics[^7]


### Basic Implementation Example

```python
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import Faithfulness, ResponseRelevancy, LLMContextPrecisionWithoutReference

# Initialize metrics
faithfulness = Faithfulness(llm=evaluator_llm)
answer_relevance = ResponseRelevancy(llm=evaluator_llm, embeddings=evaluator_embeddings)
context_precision = LLMContextPrecisionWithoutReference(llm=evaluator_llm)

# Evaluate SQL query result
sample = SingleTurnSample(
    user_input="List employees hired in the last 6 months",
    response="SELECT employee_id, first_name, last_name, hire_date FROM employees WHERE hire_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)",
    retrieved_contexts=["Database schema: employees table with columns employee_id, first_name, last_name, hire_date"]
)

# Get scores
faithfulness_score = await faithfulness.single_turn_ascore(sample)
relevance_score = await answer_relevance.single_turn_ascore(sample)
precision_score = await context_precision.single_turn_ascore(sample)
```


## Metrics Deep Dive

### 1. Faithfulness: SQL Result Consistency

**What it measures:** Whether SQL query results are factually consistent with the database schema and constraints.[^8][^7]

**How it works:**

1. Extract all claims/statements from the SQL query result
2. Verify each claim against the database schema context
3. Calculate: `Supported Statements / Total Statements`[^7]

**SQL-specific interpretation:**

- **1.0**: All returned data matches schema definitions and constraints
- **0.8-0.9**: Minor inconsistencies (e.g., data type mismatches)
- **0.6-0.7**: Some fields don't align with schema expectations
- **Below 0.6**: Significant schema violations or hallucinated data[^2]


### 2. Answer Relevance: Intent Alignment

**What it measures:** How well the SQL query results align with the user's natural language intent.[^8]

**How it works:**

1. Generate 3 artificial questions from the SQL result
2. Calculate cosine similarity with original natural language query
3. Average the similarity scores[^8]

**SQL-specific challenges:**

- OpenAI embeddings have a **floor of ~0.6 similarity**, making scores cluster between 0.6-1.0[^2]
- "Non-committal" responses are forced to 0.0, creating score bimodality[^2]
- Better for relative comparisons than absolute thresholds


### 3. Context Precision: Relevant Field Selection

**What it measures:** Whether only necessary database fields and tables are included in the SQL query and results.[^9]

**How it works:**

1. Evaluate each retrieved database element (table, column, join) for relevance
2. Calculate precision at each rank: `Relevant Elements at Rank K / Total Elements at Rank K`
3. Average across all ranks[^9]

**SQL-specific application:**

- Penalizes SELECT * queries when specific fields are requested
- Rewards appropriate JOIN selection and WHERE clause filtering
- Identifies over-retrieval of unnecessary database elements


## Baseline Expectations and Score Interpretation

### Recalibrated Scoring Framework

Based on research findings, traditional 0.0-1.0 interpretation doesn't apply to Ragas. Here's the **realistic baseline framework**:[^2]


| Score Range | Performance Level | SQL Query Quality |
| :-- | :-- | :-- |
| **0.9-1.0** | Excellent | Production-ready, accurate schema adherence |
| **0.8-0.9** | Good | Minor refinements needed, generally reliable |
| **0.7-0.8** | Acceptable | Functional but needs optimization |
| **0.6-0.7** | Poor | Significant issues, requires debugging |
| **Below 0.6** | Critical | Major problems, query may be unusable |

### Realistic Expectations by Query Type

**Simple SELECT queries:** Expect 0.85-0.95 across all metrics[^10]
**JOIN queries:** Faithfulness 0.8-0.9, Context Precision 0.7-0.85[^11]
**Complex aggregations:** All metrics typically 0.7-0.8 due to complexity[^10]
**Multi-table analytics:** Context Precision often 0.65-0.75 due to over-retrieval[^12]

## Implementation Examples

### Complete Evaluation Pipeline

```python
import asyncio
from ragas.metrics import Faithfulness, ResponseRelevancy, LLMContextPrecisionWithoutReference
from ragas import evaluate
from datasets import Dataset

# HR Database Schema Context
hr_schema_context = """
Database: hr_employees
Table: employees
- employee_id (INT, PRIMARY KEY)
- first_name (VARCHAR(50))
- last_name (VARCHAR(50))
- department (VARCHAR(100))
- role (VARCHAR(100))
- employment_status (ENUM: 'active', 'on_leave', 'terminated')
- hire_date (DATE)
- leave_type (ENUM: 'parental', 'medical', 'vacation', NULL)
- salary_local (DECIMAL(10,2))
- salary_usd (DECIMAL(10,2))
- manager_name (VARCHAR(100))
"""

# Test Dataset
evaluation_data = {
    "question": [
        "List employees hired in the last 6 months",
        "Show employees in Engineering with salary greater than 120K",
        "List employees on parental leave"
    ],
    "answer": [
        "SELECT employee_id, first_name, last_name, hire_date FROM employees WHERE hire_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)",
        "SELECT employee_id, first_name, last_name, salary_usd FROM employees WHERE department = 'Engineering' AND salary_usd > 120000",
        "SELECT employee_id, first_name, last_name, leave_type FROM employees WHERE leave_type = 'parental'"
    ],
    "contexts": [
        [hr_schema_context],
        [hr_schema_context], 
        [hr_schema_context]
    ]
}

# Convert to Dataset
eval_dataset = Dataset.from_dict(evaluation_data)

# Run evaluation
results = evaluate(
    dataset=eval_dataset,
    metrics=[
        Faithfulness(),
        ResponseRelevancy(), 
        LLMContextPrecisionWithoutReference()
    ],
    llm=ChatOpenAI(model="gpt-4"),
    embeddings=OpenAIEmbeddings()
)

print(f"Average Faithfulness: {results['faithfulness']:.3f}")
print(f"Average Answer Relevancy: {results['answer_relevancy']:.3f}")
print(f"Average Context Precision: {results['context_precision']:.3f}")
```


## Optimization Techniques

### 1. Improving Faithfulness Scores

**Schema-aware prompting:**

```python
schema_prompt = f"""
You are a SQL expert. Generate queries that strictly adhere to this schema:
{hr_schema_context}

CRITICAL RULES:
- Only use existing tables and columns
- Respect data types and constraints
- Use appropriate SQL syntax for the database system
"""
```

**Few-shot examples with schema validation:**

```python
few_shot_examples = [
    {
        "query": "employees hired recently",
        "sql": "SELECT employee_id, first_name, last_name, hire_date FROM employees WHERE hire_date >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)",
        "explanation": "Uses valid date functions and existing columns"
    }
]
```


### 2. Improving Answer Relevance

**Intent clarification in prompts:**

```python
relevance_prompt = """
Before generating SQL, restate what the user is asking for:
- What specific data do they need?
- What conditions should filter the results?  
- How should results be ordered or grouped?

Then generate SQL that precisely answers their question.
"""
```


### 3. Improving Context Precision

**Minimal field selection:**

```python
precision_prompt = """
FIELD SELECTION RULES:
- Only SELECT columns that directly answer the user's question
- Avoid SELECT * unless specifically requested
- Include foreign key columns only when needed for JOINs
- Order results logically (e.g., by date, name, or relevance)
"""
```


## Natural Language to SQL: Security and Prompt Engineering

### System Prompt Template (Production-Ready)

```python
def create_secure_nl_to_sql_prompt(schema: str) -> str:
    return f"""
You are a SQL query generator for an HR database system.

DATABASE SCHEMA:
{schema}

SECURITY CONSTRAINTS:
- ONLY generate SELECT statements
- NEVER use DELETE, DROP, ALTER, TRUNCATE, INSERT, UPDATE, or any DDL/DML commands
- NEVER access tables not defined in the schema above
- NEVER generate queries that could modify data or schema
- If asked for destructive operations, respond: "I can only generate read-only SELECT queries"

QUERY GUIDELINES:
1. Use proper SQL syntax for MySQL/PostgreSQL
2. Include appropriate WHERE clauses to filter results
3. Use JOINs when data spans multiple tables
4. Add ORDER BY clauses for better user experience
5. Limit result sets with LIMIT when appropriate

VALIDATION RULES:
- Verify all column names exist in schema
- Verify all table names exist in schema
- Use parameterized query patterns when possible
- Include comments explaining complex logic

If the request cannot be answered with the available schema, explain what information is missing.
"""
```


### Input Sanitization Pipeline

```python
import re
from typing import List, Dict

class SQLSecurityFilter:
    def __init__(self):
        self.dangerous_keywords = [
            'DELETE', 'DROP', 'ALTER', 'TRUNCATE', 'INSERT', 'UPDATE',
            'CREATE', 'GRANT', 'REVOKE', 'EXECUTE', 'CALL', 'MERGE'
        ]
        
        self.injection_patterns = [
            r';\s*(DELETE|DROP|ALTER|TRUNCATE)',
            r'UNION\s+SELECT.*FROM',
            r'OR\s+1\s*=\s*1',
            r'--\s*$',
            r'/\*.*\*/',
        ]
    
    def sanitize_input(self, user_query: str) -> str:
        # Remove SQL comments
        query = re.sub(r'--.*$', '', user_query, flags=re.MULTILINE)
        query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
        
        # Normalize whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        # Check for dangerous keywords
        for keyword in self.dangerous_keywords:
            if re.search(rf'\b{keyword}\b', query, re.IGNORECASE):
                raise SecurityError(f"Prohibited SQL keyword detected: {keyword}")
        
        # Check for injection patterns
        for pattern in self.injection_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise SecurityError(f"Potential SQL injection pattern detected")
                
        return query
    
    def validate_generated_sql(self, sql: str) -> bool:
        # Ensure query starts with SELECT
        sql_trimmed = sql.strip().upper()
        if not sql_trimmed.startswith('SELECT'):
            return False
            
        # Check for prohibited operations
        for keyword in self.dangerous_keywords:
            if keyword in sql_trimmed:
                return False
                
        return True

class SecurityError(Exception):
    pass
```


### Database Security Best Practices

```python
# Database connection with minimal privileges
import pymysql

def create_readonly_connection():
    return pymysql.connect(
        host='localhost',
        user='hr_readonly',  # User with only SELECT permissions
        password='secure_password',
        database='hr_db',
        autocommit=False,  # Prevent accidental commits
        read_timeout=30,   # Timeout for long queries
        charset='utf8mb4'
    )

def execute_safe_query(sql: str, connection) -> List[Dict]:
    """Execute SQL with safety checks"""
    security_filter = SQLSecurityFilter()
    
    # Validate SQL is safe
    if not security_filter.validate_generated_sql(sql):
        raise SecurityError("Generated SQL failed security validation")
    
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(sql)
        results = cursor.fetchall()
        
        # Limit result set size
        if len(results) > 1000:
            results = results[:1000]
            print("Warning: Results truncated to 1000 rows")
            
        return results
```


### Few-Shot Prompt Template

```python
def create_few_shot_prompt(schema: str) -> str:
    return f"""
{create_secure_nl_to_sql_prompt(schema)}

EXAMPLES:

Query: "Show me all employees in the Engineering department"
SQL: SELECT employee_id, first_name, last_name, role FROM employees WHERE department = 'Engineering';

Query: "List employees hired in 2024"  
SQL: SELECT employee_id, first_name, last_name, hire_date FROM employees WHERE YEAR(hire_date) = 2024 ORDER BY hire_date DESC;

Query: "Find employees managed by John Smith"
SQL: SELECT employee_id, first_name, last_name, department, role FROM employees WHERE manager_name = 'John Smith' ORDER BY last_name;

Query: "Show active employees with salaries above 100k"
SQL: SELECT employee_id, first_name, last_name, salary_usd FROM employees WHERE employment_status = 'active' AND salary_usd > 100000 ORDER BY salary_usd DESC;

Now generate a SQL query for the following request:
"""
```


## Common Pitfalls and Solutions

### 1. Low Faithfulness Scores

**Common Causes:**

- Schema inconsistencies in context vs actual database[^2]
- Hallucinated column names or table relationships
- Incorrect data type assumptions

**Solutions:**

- Always include up-to-date schema in context
- Use schema validation before query execution
- Provide sample data rows to clarify field contents[^10]


### 2. Biased Answer Relevance Scores

**Common Causes:**

- OpenAI embedding similarity floor of ~0.6[^2]
- "Non-committal" responses forced to 0.0[^2]
- Semantic mismatch between query and intent

**Solutions:**

- Use relative scoring rather than absolute thresholds
- Combine with human evaluation for edge cases
- Consider alternative embedding models for better score distribution


### 3. Poor Context Precision

**Common Causes:**

- Over-broad SELECT statements (SELECT *)
- Unnecessary table JOINs
- Missing WHERE clause filtering

**Solutions:**

- Explicitly prompt for minimal field selection
- Use schema-aware prompting to guide table selection
- Include query optimization instructions in prompts


## Security Checklist for Production

### Database Level

- [ ] **Read-only database user** with SELECT permissions only[^1]
- [ ] **Row-level security** implemented for multi-tenant data[^1]
- [ ] **Connection pooling** with query timeouts[^1]
- [ ] **Query result limits** to prevent resource exhaustion
- [ ] **Separate database** or replica for LLM queries


### Application Level

- [ ] **Input sanitization** filtering dangerous SQL keywords[^3]
- [ ] **SQL query validation** before execution[^3]
- [ ] **Whitelist approach** allowing only SELECT statements[^1]
- [ ] **Rate limiting** to prevent query flooding attacks[^13]
- [ ] **Audit logging** of all generated queries and results


### Prompt Engineering

- [ ] **Schema injection** in system messages, not user input[^14]
- [ ] **Clear delimiters** between instructions and user data[^3]
- [ ] **Few-shot examples** demonstrating safe query patterns[^15]
- [ ] **Explicit security constraints** in system prompts[^16]
- [ ] **Error handling** for invalid or dangerous requests[^3]


## Conclusion

Ragas provides a robust framework for evaluating LLM-generated SQL queries, but success requires **recalibrated expectations** (0.6-1.0 scoring range) and **multi-layered security**. The combination of database-level permissions, prompt engineering safeguards, and query validation creates a production-ready system capable of safely converting natural language to SQL while maintaining security and accuracy standards.

**Key Takeaways:**

1. **Baseline scores cluster 0.6-1.0** due to embedding limitations - adjust expectations accordingly[^2]
2. **Security requires multiple layers** - no single defense is sufficient[^3]
3. **Few-shot prompting significantly improves accuracy** and reduces hallucination[^15][^10]
4. **Schema-aware prompting is essential** for high faithfulness scores[^14]
5. **Regular evaluation and monitoring** catch issues before they reach production[^8]
<span style="display:none">[^100][^101][^102][^103][^104][^105][^106][^107][^108][^109][^17][^18][^19][^20][^21][^22][^23][^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^40][^41][^42][^43][^44][^45][^46][^47][^48][^49][^50][^51][^52][^53][^54][^55][^56][^57][^58][^59][^60][^61][^62][^63][^64][^65][^66][^67][^68][^69][^70][^71][^72][^73][^74][^75][^76][^77][^78][^79][^80][^81][^82][^83][^84][^85][^86][^87][^88][^89][^90][^91][^92][^93][^94][^95][^96][^97][^98][^99]</span>

<div align="center">⁂</div>

[^1]: https://www.reddit.com/r/MachineLearning/comments/1ff1y95/d_how_to_prevent_sql_injection_in_llm_based_text/

[^2]: https://tech.beatrust.com/entry/2024/05/02/RAG_Evaluation:_Assessing_the_Usefulness_of_Ragas

[^3]: https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html

[^4]: https://docs.ragas.io/en/v0.1.21/getstarted/install.html

[^5]: https://langfuse.com/guides/cookbook/evaluation_of_rag_with_ragas

[^6]: https://decodingml.substack.com/p/how-to-evaluate-your-rag-using-ragas

[^7]: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/

[^8]: https://agenta.ai/blog/how-to-evaluate-rag-metrics-evals-and-best-practices

[^9]: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_precision/

[^10]: https://www.databricks.com/blog/improving-text2sql-performance-ease-databricks

[^11]: https://jasonhaley.com/2024/07/06/study-notes-text-to-sql-code-sample/

[^12]: https://www.projectpro.io/article/ragas-score-llm/1156

[^13]: https://labelyourdata.com/articles/llm-fine-tuning/prompt-injection

[^14]: https://www.locusive.com/resources/3-best-practices-for-using-ai-to-query-your-database

[^15]: https://surajsharma.net/blog/few-shot-learning-with-prompts

[^16]: https://www.linkedin.com/posts/neerajshri_genai-azureai-awsai-activity-7242587252709584897-Id7E

[^17]: https://arxiv.org/html/2504.20119v2

[^18]: https://docs.ragas.io/en/stable/getstarted/install/

[^19]: https://milvus.io/ai-quick-reference/what-are-some-known-metrics-or-scores-such-as-faithfulness-scores-from-tools-like-ragas-that-aim-to-quantify-how-well-an-answer-sticks-to-the-provided-documents

[^20]: https://docs.ragas.io/en/stable/howtos/applications/text2sql/

[^21]: https://husnyjeffrey.com/how-to-set-up-ragas-and-run-your-first-llm-evaluation-test/

[^22]: https://docs.ragas.io/en/latest/getstarted/evals/

[^23]: https://pypi.org/project/ragas/0.0.7/

[^24]: https://tech.beatrust.com/entry/2024/05/02/RAG_Evaluation_:_Computational_Metrics_in_RAG_and_Calculation_Methods_in_Ragas

[^25]: https://github.com/explodinggradients/ragas

[^26]: https://docs.ragas.io/en/stable/getstarted/

[^27]: https://www.reddit.com/r/LangChain/comments/1bijg75/why_is_everyone_using_ragas_for_rag_evaluation/

[^28]: https://docs.ragas.io/en/stable/

[^29]: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/

[^30]: https://docs.ragas.io/en/latest/howtos/applications/benchmark_llm/

[^31]: https://pypi.org/project/ragas/

[^32]: https://docs.ragas.io/en/stable/concepts/metrics/overview/

[^33]: https://redis.io/blog/get-better-rag-responses-with-ragas/

[^34]: https://arxiv.org/abs/2410.01066

[^35]: https://medium.aiplanet.com/evaluate-rag-pipeline-using-ragas-fbdd8dd466c1

[^36]: https://shyenatechyarns.com/wp-content/uploads/2024/03/Generative-AI-SQL-Query-Generation-from-Natural-Language.pdf

[^37]: https://docs.ragas.io/en/latest/howtos/applications/evaluate-and-improve-rag/

[^38]: https://aclanthology.org/2024.eacl-demo.16/

[^39]: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/factual_correctness/

[^40]: https://pathway.com/blog/evaluating-rag

[^41]: https://arxiv.org/html/2408.03562v1

[^42]: https://blog.n8n.io/evaluating-rag-aka-optimizing-the-optimization/

[^43]: https://raga.ai/research

[^44]: https://pmc.ncbi.nlm.nih.gov/articles/PMC4057639/

[^45]: https://www.reddit.com/r/LangChain/comments/1dbmqii/i_spent_700_on_evaluating_100_rag_qa_set_using/

[^46]: https://arxiv.org/pdf/2404.19232.pdf

[^47]: https://www.chatbees.ai/blog/rag-evaluation

[^48]: https://blogs.oracle.com/ai-and-datascience/post/prompt-engineering-natural-language-sql-llama2

[^49]: https://aclanthology.org/2025.coling-main.24.pdf

[^50]: https://protectai.com/blog/gpt-4-1-vulnerability-assessment

[^51]: https://www.linkedin.com/pulse/guide-prompt-engineering-translating-natural-language-j-sheik-dawood-ekeic

[^52]: https://www.selectstar.com/resources/text-to-sql-llm

[^53]: https://www.pullrequest.com/blog/integrating-generative-ai-into-your-application-a-security-perspective/

[^54]: https://arxiv.org/html/2410.06011v1

[^55]: https://www.reddit.com/r/LocalLLaMA/comments/15142dc/llm_generating_sql_based_on_detailed_schema/

[^56]: https://www.vldb.org/pvldb/vol18/p5466-luo.pdf

[^57]: https://www.k2view.com/blog/llm-text-to-sql/

[^58]: https://cdn.openai.com/papers/gpt-4-system-card.pdf

[^59]: https://stackoverflow.blog/2024/11/07/no-code-only-natural-language-q-and-a-on-prompt-engineering-with-professor-greg-benson/

[^60]: https://arxiv.org/html/2411.00073v1

[^61]: https://community.openai.com/t/securing-natural-language-to-sql-best-practices-against-injection-attacks/562964

[^62]: https://community.openai.com/t/nl-to-sql-query-creation-using-gpt-40-mini-model/1114154

[^63]: https://ezinsights.ai/schema-aware-text-to-sql/

[^64]: https://simonw.substack.com/p/the-gpt-4-barrier-has-finally-been

[^65]: https://www.uber.com/blog/query-gpt/

[^66]: https://openreview.net/forum?id=gT8JSEFqaS

[^67]: https://arxiv.org/html/2401.02115v1

[^68]: https://arxiv.org/abs/2401.02115

[^69]: https://cookbook.openai.com/examples/evaluation/how_to_evaluate_llms_for_sql_generation

[^70]: https://syssec.dpss.inesc-id.pt/papers/pedro_icse25.pdf

[^71]: https://arxiv.org/html/2410.09174v1

[^72]: https://www.reddit.com/r/LLMDevs/comments/1i15nxt/prompt_injection_validation_for_texttosql_llm/

[^73]: https://www.invicti.com/blog/web-security/sql-injection-cheat-sheet/

[^74]: https://discuss.google.dev/t/nlp2sql-using-dynamic-rag-based-few-shot-examples/166479

[^75]: https://cloud.google.com/blog/products/databases/techniques-for-improving-text-to-sql

[^76]: https://learnprompting.org/docs/prompt_hacking/injection

[^77]: https://umu.diva-portal.org/smash/get/diva2:1878340/FULLTEXT01.pdf

[^78]: https://stackoverflow.com/questions/29494429/whitelisting-user-input-instead-of-using-prepared-statement-to-prevent-sql-injec

[^79]: https://hiddenlayer.com/innovation-hub/evaluating-prompt-injection-datasets/

[^80]: https://arxiv.org/html/2502.14913v1

[^81]: https://python.langchain.com/docs/tutorials/sql_qa/

[^82]: https://blog.langchain.com/evaluating-rag-pipelines-with-ragas-langsmith/

[^83]: https://popsql.com/blog/chatgpt-for-sql

[^84]: https://arxiv.org/pdf/2308.01990.pdf

[^85]: https://community.openai.com/t/help-needed-refactoring-sql-agent-code-for-schema-validation-in-multi-agent-workflow/1098591

[^86]: https://www.reddit.com/r/Anthropic/comments/1iur307/coming_from_openai_mostly_new_to_anthropic_i_want/

[^87]: https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html

[^88]: https://towardsdatascience.com/evaluating-rag-applications-with-ragas-81d67b0ee31a/

[^89]: https://www.blazesql.com/blog/using-chatgpt-to-write-sql

[^90]: https://developer.couchbase.com/tutorial-evaluate-rag-responses-using-ragas/

[^91]: https://hiddenlayer.com/innovation-hub/prompt-injection-attacks-on-llms/

[^92]: https://community.openai.com/t/correct-way-to-submit-the-db-schema-with-each-prompt/765679

[^93]: https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/traditional/

[^94]: https://neuraltrust.ai/blog/code-injection-in-llms

[^95]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10172229/

[^96]: https://witness.ai/prompt-injection/

[^97]: https://www.linkedin.com/posts/alexsalazar_how-to-build-sql-tools-for-ai-agents-activity-7355986726428844033--Hsa

[^98]: https://www.offsec.com/blog/how-to-prevent-prompt-injection/

[^99]: https://www.wiz.io/academy/llm-security

[^100]: https://github.com/explodinggradients/ragas/issues/1241

[^101]: https://www.ibm.com/think/insights/prevent-prompt-injection

[^102]: https://www.checkpoint.com/cyber-hub/what-is-llm-security/llm-security-best-practices/

[^103]: https://repub.eur.nl/pub/50913/891207_DEEG-Dorothy-Joan-Hardy.pdf

[^104]: https://engineering.uipath.com/beyond-basic-nl-to-sql-building-production-ready-ai-search-with-enterprise-security-7c86f1a53fb3

[^105]: https://www.science.gov/topicpages/d/detection+limit+values

[^106]: https://www.oligo.security/academy/llm-security-in-2025-risks-examples-and-best-practices

[^107]: https://developer.nvidia.com/blog/securing-llm-systems-against-prompt-injection/

[^108]: https://www.reddit.com/r/LLMDevs/comments/1jai1n6/llms_for_sql_generation_whats_productionready_in/

[^109]: https://ppl-ai-code-interpreter-files.s3.amazonaws.com/web/direct-files/ef74caf8e81ddad14ffba9106d443d65/1ebd12bc-c5de-4c14-9aeb-fd62b6f08bb7/7f6b1505.json

