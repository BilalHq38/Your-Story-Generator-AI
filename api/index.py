"""Vercel serverless function entry point."""
import os
import sys
from pathlib import Path

# Add Backend to path so imports work correctly
current_dir = Path(__file__).parent.absolute()
backend_path = current_dir.parent / "Backend"
sys.path.insert(0, str(backend_path))

# Change working directory to Backend for .env loading
os.chdir(str(backend_path))

# Import the FastAPI app from Backend
from main import app

# Vercel expects the handler to be named 'app' or 'handler'
# The 'app' variable is already the FastAPI instance
handler = app
