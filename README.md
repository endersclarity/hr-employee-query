# HR Employee Query System

Natural Language to SQL query application for HR employee records with LLM-powered query generation and Ragas evaluation.

## Overview

This application allows users to query employee data using natural language, which is converted to SQL using OpenAI's GPT-4o-mini model. The system includes multi-layered security to prevent SQL injection and uses the Ragas framework to evaluate query quality.

## Prerequisites

- **Docker** and **Docker Compose** (recommended)
- **Node.js** 18+ (for local frontend development)
- **Python** 3.11+ (for local backend development)
- **OpenAI API Key** (required for LLM functionality)

## Quick Start

### 1. Clone and Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-proj-your-key-here
```

### 2. Run with Docker Compose

```bash
# Start all services (frontend, backend, database)
docker-compose up

# Or run in detached mode
docker-compose up -d
```

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:9000
- **API Documentation**: http://localhost:9000/docs
- **Health Check**: http://localhost:9000/api/health

## Port Configuration

The application uses the following ports:

| Service    | Port | Purpose                    |
|------------|------|----------------------------|
| Frontend   | 5173 | React + Vite dev server    |
| Backend    | 9000 | FastAPI application        |
| PostgreSQL | 5432 | Database                   |

**Note**: The backend was changed from port 8000 to 9000 because Windows reserves many ports in the 8000-8480 range for system services, which can cause "bind: access forbidden" errors during Docker container startup. Port 9000 is outside the reserved ranges and works reliably on Windows systems.

### Port Conflicts

If any of these ports are already in use on your system:

1. Copy the override template:
   ```bash
   cp docker-compose.override.yml.example docker-compose.override.yml
   ```

2. Edit `docker-compose.override.yml` to use different ports:
   ```yaml
   services:
     frontend:
       ports:
         - "3000:5173"  # Use port 3000 instead of 5173
   ```

## Project Structure

```
.
├── frontend/          # React + Vite + Tailwind CSS
│   ├── src/
│   ├── package.json
│   └── Dockerfile
├── backend/           # FastAPI + Python
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── services/
│   │   ├── db/
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
├── docs/              # Project documentation
├── scripts/           # Utility scripts
│   └── validate-env.sh
├── docker-compose.yml
├── .env.example
└── README.md
```

## Development

### Validate Environment Variables

Before starting development, ensure all required environment variables are set:

```bash
./scripts/validate-env.sh
```

### Local Development (without Docker)

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

## Environment Variables

Required variables (must be set in `.env`):

- `OPENAI_API_KEY`: Your OpenAI API key for LLM functionality
- `DATABASE_URL`: PostgreSQL connection string

Optional variables:

- `PYTHON_ENV`: Environment mode (development/staging/production)
- `ALLOWED_ORIGINS`: CORS allowed origins (default: http://localhost:5173)
- `LOG_LEVEL`: Logging level (default: INFO)

## Technology Stack

- **Frontend**: React 18.3.1, Tailwind CSS 3.4.1, Vite 5.0.0
- **Backend**: FastAPI 0.109.0, Python 3.11+
- **Database**: PostgreSQL 15+
- **LLM**: OpenAI GPT-4o-mini
- **Evaluation**: Ragas framework
- **Deployment**: Docker, Railway (production)

## License

MIT

## Author

Kaelen - Job Interview Demonstration Project
