"""Vercel entrypoint. Vercel loads the FastAPI `app` from this file.

Local runs use: uvicorn app.main:app --port 8000
"""
from app.main import app  # noqa: F401
