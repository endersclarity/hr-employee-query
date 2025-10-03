"""Pytest configuration for backend tests."""

import os

# Set environment variables at import time (before any app imports)
os.environ["DATABASE_URL"] = "postgresql://postgres:postgres@localhost:5432/hr_db"
os.environ["SKIP_API_KEY_VALIDATION"] = "true"  # Skip OpenAI validation in tests

import pytest
