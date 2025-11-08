# Notes API

A simple CRUD application for Notetaking. It is used for experimenting with different technologies often related to APIs.

## Tech Stack

- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Relational database
- **SQLAlchemy** - ORM with modern query syntax
- **Pydantic** - Data validation and settings management
- **Pytest** - Testing framework
- **Docker** - Containerization
- **GitHub Actions** - A simple CI

## Features

- Full CRUD operations for notes
- API versioning (`/v1/`)
- Health check endpoints
- Error handling
- Request validation
- Pagination support
- Database connection pooling

## Quick Start

### Prerequisites

- Python 3.13+
- PostgreSQL (or use Docker Compose)
- `uv` package manager

### Installation

1. Clone the repository
2. Install dependencies:

   ```bash
   uv sync
   ```

3. Set up environment variables:

   ```bash
   cp .env.example .env
   ```

4. Run with Docker Compose:

   ```bash
   docker-compose up
   ```

   Or run locally:

   ```bash
   uv run uvicorn app.main:app --reload
   ```

### API Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /health/detailed` - Detailed health check with database
- `GET /docs` - Interactive API documentation

**Version 1 Endpoints:**

- `GET /v1/notes/` - List notes (with pagination)
- `GET /v1/notes/{id}` - Get note by ID
- `POST /v1/notes/` - Create note
- `PUT /v1/notes/{id}` - Update note (full)
- `PATCH /v1/notes/{id}` - Update note (partial)
- `DELETE /v1/notes/{id}` - Delete note

## Project Structure

```
app/
├── api/           # API routes and endpoints
│   ├── v1/       # Version 1 API
│   ├── health.py # Health check endpoints
│   └── root.py   # Root endpoint
├── config/       # Configuration (database, settings)
├── core/         # Core constants
├── repositories/ # Data access layer
├── schemas/      # Pydantic models
└── main.py       # Application entry point

tests/
├── integration/  # Integration tests
└── unit/         # Unit tests
```

## Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test types
uv run pytest -m unit
uv run pytest -m integration
```
