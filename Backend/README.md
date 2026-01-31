# Story Teller API

An AI-powered "Choose Your Own Adventure" story API built with FastAPI, LangChain, and Google Gemini.

## Features

- 🎭 **Interactive Stories** - Create branching narrative adventures
- 🤖 **AI-Powered Generation** - Uses Google Gemini to generate story content
- 🌳 **Tree Structure** - Stories are organized as navigable decision trees
- ⚡ **Async Processing** - Background job queue for story generation
- 📊 **Full CRUD** - Complete API for stories, nodes, and jobs
- 🔒 **Production Ready** - Logging, error handling, health checks

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL (or SQLite for development)
- Google Gemini API key

### Installation

1. **Clone and navigate to the backend:**
   ```bash
   cd Backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

6. **Start the server:**
   ```bash
   uvicorn main:app --reload
   ```

7. **Open the API docs:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Configuration

Create a `.env` file with these settings:

```env
# Environment
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# Security
SECRET_KEY=your-super-secret-key-change-in-production
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/storyteller
# Or for SQLite development:
# DATABASE_URL=sqlite:///./story_teller.db

# AI
GEMINI_API_KEY=your-gemini-api-key
```

## API Endpoints

### Stories

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/stories/` | Create a new story |
| `GET` | `/api/v1/stories/` | List all stories (paginated) |
| `GET` | `/api/v1/stories/{id}` | Get story with tree structure |
| `GET` | `/api/v1/stories/session/{session_id}` | Get story by session |
| `PATCH` | `/api/v1/stories/{id}` | Update story metadata |
| `DELETE` | `/api/v1/stories/{id}` | Delete a story |

### Story Nodes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/stories/{id}/nodes` | Add a node to a story |
| `GET` | `/api/v1/stories/{id}/nodes` | List all nodes |
| `GET` | `/api/v1/stories/{id}/nodes/{node_id}` | Get node with children |
| `PATCH` | `/api/v1/stories/{id}/nodes/{node_id}` | Update a node |
| `DELETE` | `/api/v1/stories/{id}/nodes/{node_id}` | Delete a node |

### Jobs (AI Generation)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/jobs/` | Start a generation job |
| `GET` | `/api/v1/jobs/` | List all jobs |
| `GET` | `/api/v1/jobs/{job_id}` | Get job details |
| `GET` | `/api/v1/jobs/{job_id}/status` | Poll job status |
| `POST` | `/api/v1/jobs/{job_id}/cancel` | Cancel a pending job |
| `DELETE` | `/api/v1/jobs/{job_id}` | Delete a completed job |

### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Full health check |
| `GET` | `/health/ready` | Readiness probe |
| `GET` | `/health/live` | Liveness probe |

## Project Structure

```
Backend/
├── alembic/                 # Database migrations
│   ├── versions/            # Migration files
│   └── env.py               # Alembic configuration
├── core/                    # Core business logic
│   ├── config.py            # Settings management
│   ├── exceptions.py        # Custom exceptions
│   ├── logging.py           # Logging configuration
│   ├── prompts.py           # AI prompt templates
│   └── story_generator.py   # AI story generation
├── db/                      # Database layer
│   └── database.py          # SQLAlchemy setup
├── models/                  # SQLAlchemy ORM models
│   ├── job.py               # Job model
│   └── story.py             # Story & StoryNode models
├── routers/                 # API endpoints
│   ├── jobs.py              # Job endpoints
│   └── story.py             # Story endpoints
├── schema/                  # Pydantic schemas
│   ├── job.py               # Job request/response schemas
│   └── story.py             # Story request/response schemas
├── tests/                   # Test suite
│   ├── conftest.py          # Test fixtures
│   ├── test_health.py       # Health endpoint tests
│   └── test_stories.py      # Story endpoint tests
├── .env                     # Environment variables (not in git)
├── .gitignore               # Git ignore rules
├── alembic.ini              # Alembic configuration
├── main.py                  # FastAPI application
├── pyproject.toml           # Project dependencies
└── README.md                # This file
```

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_stories.py -v
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type check
mypy .
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Deployment

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install .

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Checklist

- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Use a strong `SECRET_KEY`
- [ ] Configure proper `ALLOWED_ORIGINS`
- [ ] Use PostgreSQL (not SQLite)
- [ ] Run migrations with `alembic upgrade head`
- [ ] Set up proper logging aggregation
- [ ] Configure health check endpoints in load balancer

## License

MIT License - see LICENSE file for details.
