# user-management-api

A multi-user REST API for secure note management with authentication, role-based access control, and note sharing between users. Built as a portfolio project to demonstrate real-world backend design decisions using **FastAPI** and **PostgreSQL**.

---

## Why this project exists

Most tutorial APIs stop at "create a user and return a token." This one goes further: it models a collaborative system where users own resources, can share them with others under specific roles, and those resources can be soft-deleted without losing audit history. The goal was to make decisions that reflect production thinking, not just working code.

---

## Stack

- **Python 3.11** + **FastAPI** — async-ready framework with automatic OpenAPI documentation
- **PostgreSQL 15** — relational database with UUID primary keys and enforced constraints
- **SQLAlchemy 2.0** — ORM with explicit session management and typed queries
- **Alembic** — schema migrations decoupled from application startup
- **JWT** (python-jose) — stateless authentication via signed tokens
- **bcrypt** — password hashing with adaptive cost factor
- **Pydantic v2** — request/response validation with strict typing
- **Docker + Docker Compose** — containerized services for reproducible environments
- **pytest + httpx** — isolated test suite with per-test transaction rollback

---

## Design decisions

**Separation between `security.py` and `dependencies.py`.** Cryptographic operations (hashing, token creation, token decoding) live in `security.py` with no FastAPI dependencies. Orchestration logic — reading the token from the request, querying the database, raising HTTP errors — lives in `dependencies.py`. This makes the crypto layer independently testable and keeps concerns clearly separated.

**UUID primary keys.** Both `User` and `Note` models use UUIDs instead of sequential integers. This prevents ID enumeration attacks and avoids exposing record counts to clients.

**Soft delete via `deleted_at`.** Notes are never physically removed from the database. Instead, a `deleted_at` timestamp is set, and all queries filter on `Note.deleted_at.is_(None)`. This preserves the ability to audit deletions, recover records if needed, and avoid broken foreign key references in `NoteShare`.

**Conflict handling at two layers.** The `NoteShare` model enforces a `UNIQUE(note_id, shared_with)` constraint at the database level, but the application also checks for duplicates before attempting the insert and returns a `409 Conflict` response explicitly. This prevents SQLAlchemy integrity errors from leaking into the response and gives the client a meaningful error before hitting the database.

**Role expressed as a Pydantic `Literal`.** The `role` field in note sharing accepts only `'viewer'` or `'editor'`. This is enforced at the schema level via `Literal['viewer', 'editor']`, which means invalid values are rejected before they reach any business logic or database layer.

**Union query for owned + shared notes.** `GET /notes/` returns both notes the user owns and notes shared with them, without duplicates, using a SQLAlchemy `union()` query instead of two separate requests joined in Python. This keeps the logic in the database where it belongs.

**Test isolation via transaction rollback.** Each test runs inside a database transaction that is rolled back at the end, leaving no state between tests. The test client uses `app.dependency_overrides[get_db]` to inject the test session, so tests exercise the actual application stack rather than mocks.

---

## Getting started

### With Docker (recommended)

```bash
git clone https://github.com/AdrianCervantes53/user-management-api.git
cd user-management-api

cp .env.example .env
# Edit .env with your values

docker compose up --build
docker compose exec backend alembic upgrade head
```

The API will be available at `http://localhost:8000`.

### Without Docker

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env with your values

alembic upgrade head
uvicorn app.main:app --reload
```

---

## API reference

Interactive documentation is available at `http://localhost:8000/docs` once the server is running.

### Auth

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/auth/login` | Login with email + password, returns JWT | No |

### Users

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/users/` | Register a new user | No |
| GET | `/users/` | List all users | Yes |
| GET | `/users/me` | Get authenticated user profile | Yes |
| GET | `/users/by-id/{user_id}` | Get user by ID | No |

### Notes

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/notes/` | Create a note | Yes |
| GET | `/notes/` | List owned and shared notes (paginated, filterable) | Yes |
| GET | `/notes/{note_id}` | Get a specific note | Yes |
| DELETE | `/notes/{note_id}` | Soft-delete a note | Yes |
| POST | `/notes/{note_id}/share` | Share a note with another user | Yes |

### Quick example

```bash
# Register
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "adrian", "email": "adrian@example.com", "password": "secret123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -F "username=adrian@example.com" \
  -F "password=secret123"

# Use the token
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer <token>"

# Share a note
curl -X POST http://localhost:8000/notes/<note_id>/share \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"shared_with": "<user_id>", "role": "viewer"}'
```

---

## Running tests

Tests use a separate PostgreSQL database and roll back each transaction after every test.

```bash
# Create the test database
psql -U postgres -c "CREATE DATABASE users_db_test;"

# Add to .env
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/users_db_test

# Run
pytest tests/ -v
```

Test coverage includes: auth flows (register, login, duplicates, wrong password), note CRUD and isolation, access control enforcement (403 on unauthorized access), shared access by role, soft delete behavior, pagination and search filters, and note-share edge cases (duplicate shares, self-share, invalid role, deleted note).

---

## Project structure

```
├── app/
│   ├── main.py              # Application entry point and router registration
│   ├── database.py          # SQLAlchemy engine and session factory
│   ├── core/
│   │   ├── config.py        # Environment variable loading
│   │   ├── security.py      # JWT creation/decoding and password hashing
│   │   └── dependencies.py  # FastAPI dependencies (get_db, get_current_user)
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   └── routers/             # Endpoint handlers grouped by resource
├── tests/
│   ├── conftest.py          # Fixtures: DB setup, test client, auth helpers
│   ├── test_auth.py
│   ├── test_notes.py
│   └── test_note_share.py
├── alembic/                 # Migration scripts
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Status and roadmap

Implemented: JWT authentication, user registration, full note CRUD, soft delete, pagination and search filters, note sharing with viewer/editor roles, access control enforcement, and a full pytest test suite with transaction-level isolation.

In progress: `PUT /notes/{note_id}` (edit note content), `PUT /users/me` (update profile).

Planned: rate limiting with Redis, CI/CD with GitHub Actions, deployment to Railway or Render, and refresh token support.
