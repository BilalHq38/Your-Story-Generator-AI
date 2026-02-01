"""Vercel serverless function entry point."""

import sys
from pathlib import Path

# Ensure the repository root is on sys.path so `import Backend.*` works.
# Vercel deploys with a working directory like `/var/task`.
repo_root = Path(__file__).resolve().parents[1]
if str(repo_root) not in sys.path:
	sys.path.insert(0, str(repo_root))

from Backend.main import app

# Vercel expects a variable named 'app'
# This is the ASGI application that Vercel will invoke
