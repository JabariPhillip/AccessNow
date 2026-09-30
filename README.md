# AccessNow — FastAPI + SQLAlchemy Mockup

This version wires the AccessNow web prototype to a real FastAPI backend and SQLAlchemy database.

## Stack
- FastAPI
- SQLAlchemy 2.x
- SQLite by default
- PostgreSQL supported through `DATABASE_URL`
- Pydantic
- Vanilla HTML/CSS/JavaScript frontend

## Run locally

### 1. Create a virtual environment
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Seed the fictional demo data
```bash
python seed.py
```

### 4. Start FastAPI
```bash
uvicorn app.main:app --reload
```

Open:
- http://127.0.0.1:8000 — AccessNow web app
- http://127.0.0.1:8000/docs — interactive API documentation
- http://127.0.0.1:8000/api/health — health check

## PostgreSQL

Set `DATABASE_URL` before starting the server, for example:

```text
postgresql+psycopg://accessnow:password@localhost:5432/accessnow
```

Then run `python seed.py` against that database.

## API endpoints

- `GET /api/venues`
- `GET /api/venues/{id}`
- `GET /api/venues/{id}/route`
- `POST /api/venues/{id}/reviews`
- `GET /api/users/{id}`
- `GET /api/users/{id}/saved`
- `POST /api/saved`
- `DELETE /api/saved/{id}`

The current demo intentionally uses a fictional user with ID 1. Authentication/JWT is not included yet.
