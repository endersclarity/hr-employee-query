# Proposed Source Tree

```
hr-nl-query-app/
├── README.md                      # Setup, deployment, usage instructions
├── docker-compose.yml             # Local development orchestration
├── .gitignore                     # Git ignore rules
├── .env.example                   # Example environment variables
│
├── docs/                          # All documentation
│   ├── project-assignment.md
│   ├── brainstorming-session-results-2025-10-01.md
│   ├── PRD.md
│   ├── epic-stories.md
│   ├── solution-architecture.md   # This document
│   ├── tech-spec-epic-1.md        # To be generated
│   ├── tech-spec-epic-2.md        # To be generated
│   └── project-report.md          # Final deliverable
│
├── frontend/                      # React application
│   ├── Dockerfile                 # Production build
│   ├── Dockerfile.dev             # Development build
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── index.html
│   ├── public/
│   └── src/
│       ├── App.jsx                # Main app component
│       ├── main.jsx               # Entry point
│       ├── components/
│       │   ├── QueryInterface.jsx
│       │   ├── ResultsTable.jsx
│       │   ├── RagasScoreDisplay.jsx
│       │   └── ErrorDisplay.jsx
│       ├── services/
│       │   └── api.js             # Axios API client
│       └── styles/
│           └── index.css          # Tailwind imports
│
├── backend/                       # FastAPI application
│   ├── Dockerfile                 # Production image
│   ├── Dockerfile.dev             # Development image
│   ├── requirements.txt           # Python dependencies
│   ├── alembic.ini                # Migration config
│   ├── alembic/                   # Migration scripts
│   │   └── versions/
│   └── app/
│       ├── __init__.py
│       ├── main.py                # FastAPI app initialization
│       ├── config.py              # Settings (Pydantic BaseSettings)
│       ├── api/
│       │   ├── __init__.py
│       │   ├── routes.py          # API endpoints
│       │   └── models.py          # Pydantic request/response models
│       ├── services/
│       │   ├── __init__.py
│       │   ├── query_service.py   # Main orchestrator
│       │   ├── llm_service.py     # OpenAI integration
│       │   ├── ragas_service.py   # Evaluation
│       │   └── validation_service.py  # Security
│       ├── db/
│       │   ├── __init__.py
│       │   ├── models.py          # SQLAlchemy ORM models
│       │   ├── session.py         # DB connection
│       │   └── seed.py            # Mock data generator
│       └── utils/
│           ├── __init__.py
│           └── logger.py          # Structured logging
│
├── scripts/                       # Utility scripts
│   ├── start.sh                   # Production startup (migrations + seed + server)
│   └── seed_db.py                 # Standalone seed script
│
└── tests/                         # Tests (future)
    ├── frontend/
    └── backend/
```

**Total Files:** ~40 files (manageable for solo developer)

---
