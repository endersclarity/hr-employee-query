"""FastAPI application for HR Employee Query System."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from dotenv import load_dotenv

from app.middleware.request_id import RequestIDMiddleware
from app.api.routes import router
from app.utils.logger import structlog
from app.services.llm_service import validate_api_key
from app.services.ragas_service import initialize_ragas

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager for startup/shutdown logic."""
    # Startup: Validate OpenAI API key
    if not os.getenv("SKIP_API_KEY_VALIDATION"):
        await validate_api_key()
    # Initialize Ragas framework
    await initialize_ragas()
    yield
    # Shutdown: Cleanup logic (if needed in future)


# Initialize FastAPI application with lifespan
app = FastAPI(
    title="HR Query API",
    version="1.0.0",
    description="Natural Language to SQL query system for HR employee records",
    lifespan=lifespan
)

# Add Request ID middleware (must be first for proper tracking)
app.add_middleware(RequestIDMiddleware)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=os.getenv("ALLOWED_HEADERS", "Content-Type,Authorization").split(","),
)

# Include API routes
app.include_router(router)

# Configure static file serving for production (Railway-compatible paths)
BASE_DIR = Path(__file__).resolve().parent.parent  # Points to /app in container
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIST / "assets")), name="assets")


# Global exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions with structured error responses."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "error_type": "HTTP_ERROR"
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with structured error responses."""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "error_type": "SERVER_ERROR"
        }
    )


@app.get("/")
async def serve_react_root():
    """Serve React application root."""
    index_path = FRONTEND_DIST / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not built")
    return FileResponse(str(index_path))


@app.get("/{full_path:path}")
async def serve_react(full_path: str):
    """Serve React application for all other routes (SPA fallback)."""
    # Skip API routes
    if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
        raise HTTPException(status_code=404, detail="Not found")

    index_path = FRONTEND_DIST / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Frontend not built")
    return FileResponse(str(index_path))
