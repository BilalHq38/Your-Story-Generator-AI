"""Vercel serverless function entry point."""
import sys
from pathlib import Path

# Add Backend to path so imports work correctly
current_dir = Path(__file__).parent.absolute()
backend_path = current_dir.parent / "Backend"
sys.path.insert(0, str(backend_path))

# Import the FastAPI app from Backend
from main import app

# Vercel expects a variable named 'app'
# This is the ASGI application that Vercel will invoke
