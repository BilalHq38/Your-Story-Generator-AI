"""Vercel serverless function entry point."""

import sys
from pathlib import Path

# Ensure both repo root AND Backend folder are on sys.path.
# This allows imports like `from Backend.main import app` AND
# Backend's internal imports like `from core.config import settings`.
repo_root = Path(__file__).resolve().parents[1]
backend_path = repo_root / "Backend"

for p in [str(repo_root), str(backend_path)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from Backend.main import app

# Vercel expects a variable named 'app'
# This is the ASGI application that Vercel will invoke
