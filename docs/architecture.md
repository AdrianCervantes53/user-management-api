# Architecture

## Overview

A multi-user REST API for collaborative note management. Users can own notes, share them with other users under specific roles (`viewer` / `editor`), and soft-delete them without losing audit history. Built to reflect production-grade design decisions rather than tutorial-level code.

---

## Stack

| Technology | Role |
|------------|------|
| **Python 3.11** + **FastAPI** | Async-ready web framework with automatic OpenAPI docs |
| **PostgreSQL 15** | Relational database with UUID PKs and enforced constraints |
| **SQLAlchemy 2.0** | ORM with explicit session management and typed queries |
| **Alembic** | Schema migrations decoupled from application startup |
| **JWT** (python-jose) | Stateless authentication via signed tokens |
| **bcrypt** | Adaptive password hashing |
| **Pydantic v2** | Request/response validation with strict typing |
| **Docker + Docker Compose** | Containerized services for reproducible environments |
| **pytest + httpx** | Isolated test suite with per-test transaction rollback |

---

## Three-layer architecture

The codebase is organized into three distinct layers, each with a single responsibility:

```
Request → Router → Service → Database
                ↑
           Dependency
         (auth / db session)
```

**Routers** (`app/routers/`) contain only endpoint definitions — HTTP method, path, dependency injection, and a single service call. 2–4 lines per endpoint. No business logic.

**Services** (`app/services/`) contain all business logic and database operations: validation rules, access control checks, query construction, and error handling. Services receive plain Python objects (SQLAlchemy sessions, Pydantic models, UUIDs) — no FastAPI types.

**Dependencies** (`app/dependencies/`) are FastAPI `Depends()` functions that resolve shared concerns before the handler runs: opening a DB session (`get_db`) and identifying the current user from the JWT (`get_current_user`). Keeping them separate from services makes each independently testable.

---

## Project structure

```
app/
├── main.py                   # Entry point, router registration
├── database.py               # Engine + session factory
├── core/
│   ├── config.py             # Pydantic Settings (env vars)
│   └── security.py           # JWT + bcrypt (pure crypto, no FastAPI deps)
├── dependencies/
│   ├── auth.py               # get_current_user
│   └── db.py                 # get_db
├── services/
│   ├── auth_service.py       # Login logic
│   ├── user_service.py       # User CRUD
│   ├── note_service.py       # Note CRUD + query logic
│   └── note_share_service.py # Note sharing logic
├── models/                   # SQLAlchemy ORM models (User, Note, NoteShare)
├── schemas/                  # Pydantic request/response schemas
└── routers/                  # Endpoints grouped by resource

tests/
├── conftest.py               # Fixtures: DB setup, test client, auth helpers
├── test_auth.py
├── test_notes.py
└── test_note_share.py

alembic/                      # Migration scripts
docs/
├── api.md                    # Full endpoint reference
└── architecture.md           # This file
```

---

## Authentication flow

```
POST /auth/login
  │
  ├─ auth_service.login()
  │    ├─ Query User by email
  │    ├─ bcrypt.verify(plain_password, hashed_password)
  │    └─ security.create_access_token({"sub": str(user.id)})
  │
  └─ Returns: { access_token, token_type }

Protected request
  │
  ├─ get_current_user (dependency)
  │    ├─ Extract Bearer token from Authorization header
  │    ├─ security.decode_token(token) → payload
  │    └─ Query User by payload["sub"] → current_user
  │
  └─ current_user injected into handler
```

Cryptographic operations (hashing, token creation, decoding) live in `core/security.py` with zero FastAPI imports. This makes the crypto layer independently testable and keeps it decoupled from HTTP concerns.

---

## Database schema

### `users`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID (PK) | Auto-generated |
| `username` | VARCHAR(50) | Unique |
| `email` | VARCHAR(100) | Unique |
| `password` | VARCHAR | bcrypt hash |
| `is_active` | BOOLEAN | Default `true` |
| `created_at` | TIMESTAMP | Set at insert |

### `notes`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID (PK) | Auto-generated |
| `owner_id` | UUID (FK) | → `users.id` ON DELETE CASCADE |
| `title` | VARCHAR | — |
| `content` | TEXT | — |
| `deleted_at` | TIMESTAMP | `NULL` = active (soft delete) |
| `created_at` | TIMESTAMP | Set by DB (`now()`) |
| `updated_at` | TIMESTAMP | Set by DB (`now()`), updated on write |

### `note_shares`

| Column | Type | Notes |
|--------|------|-------|
| `id` | UUID (PK) | Auto-generated |
| `note_id` | UUID (FK) | → `notes.id` ON DELETE CASCADE |
| `shared_with` | UUID (FK) | → `users.id` ON DELETE CASCADE |
| `role` | VARCHAR | `'viewer'` or `'editor'` |
| `created_at` | TIMESTAMP | Set by DB (`now()`) |
| — | UNIQUE | `(note_id, shared_with)` |

---

## Role model

Roles are **scoped per note**, not global to a user. The same user can be an `editor` on one note and a `viewer` on another. The `role` field lives exclusively in `note_shares` — there is no global role on the `User` model.

Access control is enforced at the service layer by querying `NoteShare` for the specific `(note_id, user_id)` pair before any write operation:

```python
# update_note — note_service.py
is_owner = note.owner_id == current_user.id
is_editor = db.query(NoteShare).filter(
    NoteShare.note_id == note_id,
    NoteShare.shared_with == current_user.id,
    NoteShare.role == "editor"
).first()

if not is_owner and not is_editor:
    raise HTTPException(403, "Not allowed to edit this note")
```

| Action | Owner | Editor | Viewer |
|--------|-------|--------|--------|
| Read note | ✅ | ✅ | ✅ |
| Update note | ✅ | ✅ | ❌ |
| Delete note | ✅ | ❌ | ❌ |
| Share note | ✅ | ❌ | ❌ |

---

## Test strategy

Each test runs inside a PostgreSQL transaction that is rolled back at teardown, leaving no persistent state between tests. The test client uses `app.dependency_overrides[get_db]` to inject the test session, so the full application stack is exercised — no mocks.

```
pytest fixture hierarchy:

setup_database (session-scoped)   ← creates all tables once
    └── db (function-scoped)      ← transaction per test, rolled back after
         └── client               ← TestClient with get_db overridden
              ├── registered_user
              ├── auth_headers
              ├── another_user_token
              └── editor_user_token
```
