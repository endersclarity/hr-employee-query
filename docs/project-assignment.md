# Natural Language HR Employee Records Query Application

**Presentation Scheduled: October 12th, 2025**

## 1. Objective

Build a minimal full-stack application that enables users to enter natural language queries and retrieve employee records from a database. The application should highlight system design, coding ability, user experience, and evaluation rigor.

## 2. Requirements

### Frontend (React)
Develop a simple web interface with:
- Input box for natural language queries
- Submit button to send queries
- Results displayed in a tabular format

### Backend (Python, FastAPI)
- Expose a REST API that accepts natural language queries
- Integrate with OpenAI (or similar LLM) to convert natural language → SQL
- Execute generated SQL against a database with mock HR employee data
- Return results as JSON

### Database (Any Relational DB)
Implement a table `employees` with the following fields:
- `employee_id`
- `first_name`
- `last_name`
- `department`
- `role`
- `employment_status` (e.g., Active, Terminated, On Leave)
- `hire_date`
- `leave_type` (nullable)
- `salary_local`
- `salary_usd`
- `manager_name`

## 3. Example Use Cases

The application should handle queries such as:
- "List employees hired in the last 6 months."
- "Show employees in Engineering with salary greater than 120K."
- "List employees on parental leave."
- "Show employees managed by John Doe."

## 4. Deployment (Cloud-Agnostic)

- Deploy both frontend and backend in any major cloud provider (AWS, Azure, or GCP)
- Use cloud-native secret management to store API keys and database credentials securely

### Example Deployment Setup (for guidance, not mandatory)
- **Backend:** Deploy via AWS Elastic Beanstalk (or equivalent service such as Azure App Service, GCP Cloud Run)
- **Database:** Use a managed relational database service such as AWS RDS (or Azure SQL Database, GCP Cloud SQL)
- **Frontend:** Host locally or deploy on a free/static hosting service (e.g., Netlify, Vercel, GitHub Pages, or cloud-native static hosting)

## 5. Packaging

- Package both frontend and backend in Docker containers
- Provide a `docker-compose.yml` file to run the entire system locally

## 6. Deliverables

- Source code for frontend and backend
- Database schema (with mock dataset)
- Dockerfiles + docker-compose.yml
- README with setup, deployment, and usage instructions
- Create a Project Report with Architecture, Flow, Deployment instructions or anything relevant

## 7. Evaluation Using Ragas

Your solution must include an evaluation framework using Ragas.

### Metrics
- **Faithfulness:** Are the results factually consistent with the underlying database?
- **Answer Relevance:** Do the results align with the user's intent?
- **Context Precision:** Are only relevant fields included in the response?

### Expected Outcomes
- Clearly documented scores (0 → 1 scale)
- Comparative results across multiple queries
- Identification of weak spots (e.g., irrelevant records, missing filters)
- Recommendations for improving accuracy (e.g., schema-based prompting, few-shot examples, grammar constraints)
