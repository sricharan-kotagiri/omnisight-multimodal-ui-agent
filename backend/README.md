# OmniSight Backend

**Multimodal UI Self-Healing & RPA Agent — Python / FastAPI backend.**

## Overview

OmniSight is an intelligent browser automation system that detects website UI changes, understands the current interface using multimodal AI (Gemini), identifies alternative UI elements when automation fails, and safely recovers from those failures.

## Technology Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Web Framework | FastAPI 0.115 |
| Database | PostgreSQL 16 (asyncpg driver) |
| ORM | SQLAlchemy 2.0 (async) |
| Migrations | Alembic |
| Schemas | Pydantic v2 |
| Browser Automation | Playwright (Phase 3) |
| AI | Gemini 1.5 Flash (Phase 4) |
| Testing | Pytest + pytest-asyncio |
| Containerisation | Docker / Docker Compose |

## Architecture

```
backend/
  app/
    main.py              # FastAPI app factory + lifespan
    core/
      config.py          # Pydantic BaseSettings (env-driven)
      exceptions.py      # Custom exception hierarchy
      security.py        # URL validation, SSRF protection
    api/v1/
      router.py          # Aggregates all v1 routers
      tasks.py           # Task CRUD + execution endpoints
      healing.py         # Healing analysis endpoint (Phase 4 stub)
    models/              # SQLAlchemy 2.0 ORM models
    schemas/             # Pydantic v2 request/response schemas
    services/
      task_service.py    # DB operations for tasks / executions / logs
      execution_service.py # Execution lifecycle management
    automation/          # Playwright integration (Phase 3)
    ai/                  # Gemini client (Phase 4)
    healing/             # Self-healing engine (Phase 5)
    database/
      base.py            # Engine, session factory, Base, get_db
    utils/
      logger.py          # Structured logging (JSON in prod)
  tests/                 # Pytest test suite
```

## Quick Start

### Prerequisites

- Python 3.12+
- PostgreSQL 16 (or use Docker Compose)
- Git

### Local development (without Docker)

```bash
# 1. Clone and enter the project
cd backend

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and set DATABASE_URL, GEMINI_API_KEY, etc.

# 5. Run the server
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000.  
Swagger UI: http://localhost:8000/docs

### Docker Compose

```bash
# Copy and edit the env file first
cp .env.example .env

# Build and start both services
docker-compose up --build
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/tasks` | Create a task |
| `GET` | `/api/v1/tasks/{id}` | Get task details |
| `POST` | `/api/v1/tasks/{id}/execute` | Trigger execution |
| `GET` | `/api/v1/tasks/{id}/status` | Execution status |
| `GET` | `/api/v1/tasks/{id}/logs` | Execution logs |
| `GET` | `/api/v1/tasks/{id}/healing` | Healing history |
| `POST` | `/api/v1/healing/analyze` | Analyse UI failure (Phase 4 stub) |

## Environment Variables

See `.env.example` for all available configuration options.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `GEMINI_API_KEY` | *(required in Phase 4)* | Gemini API key |
| `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model to use |
| `APP_ENV` | `development` | `development` or `production` |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Allowed CORS origins |
| `MAX_HEALING_RETRIES` | `3` | Max self-healing retry attempts |
| `HEALING_CONFIDENCE_THRESHOLD` | `0.7` | Minimum AI confidence to act |
| `BROWSER_TIMEOUT_MS` | `30000` | Playwright operation timeout |
| `SECRET_KEY` | *(auto-generated)* | Override in production |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Database Schema

| Table | Description |
|---|---|
| `tasks` | User-submitted automation tasks |
| `executions` | Individual task execution runs |
| `execution_logs` | Structured log entries per execution |
| `healing_attempts` | Self-healing recovery records |
| `ai_analyses` | Full AI prompt/response audit trail |

## Testing

```bash
# Run all tests from the backend/ directory
cd backend
python -m pytest tests/ -v

# Run only API tests
python -m pytest tests/test_api/ -v
```

Tests use an in-memory SQLite database — no PostgreSQL instance required.

## Development Phases

| Phase | Status | Description |
|---|---|---|
| 1 | ✅ Architecture design | Repository inspection and design |
| 2 | ✅ **Current** | FastAPI foundation, models, schemas, DB layer |
| 3 | 🔜 Playwright | Browser automation engine |
| 4 | 🔜 Gemini AI | Multimodal AI integration |
| 5 | 🔜 Self-healing | Healing engine, validator, classifier |
| 6 | 🔜 DB integration | Alembic migrations, production hardening |
| 7 | 🔜 Security | Full security audit |
| 8 | 🔜 Testing | Comprehensive test coverage |
| 9 | 🔜 Frontend integration | Connect to React/Next.js frontend |
| 10 | 🔜 Deployment | Production Docker, CI/CD |

## Security Notes

- All target URLs are validated for SSRF (private IP ranges blocked before any browser request is made).
- No API keys are hardcoded — all secrets come from environment variables.
- AI responses are validated against a strict Pydantic schema before the application acts on them.
- Sensitive actions (financial, destructive) will require human approval (Phase 5+).
