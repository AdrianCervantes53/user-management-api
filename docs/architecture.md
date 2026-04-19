# Architecture

## Overview
A multi-user REST API for secure note management with authentication, role-based access control, and note sharing between users. Built as a portfolio project to demonstrate real-world backend design decisions using **FastAPI** and **PostgreSQL**.


## Stack

- **Python 3.11** + **FastAPI** 
- **PostgreSQL 15**
- **SQLAlchemy 2.0**
- **Alembic**
- **JWT**
- **bcrypt**
- **Pydantic v2**
- **Docker + Docker Compose**
- **pytest + httpx**

## Project Structure

app/
├── main.py              # Entry point, router registration
├── database.py          # Engine + session factory
├── core/
│   ├── config.py        # Pydantic Settings (env vars)
│   └── security.py      # JWT + bcrypt (pure crypto, no FastAPI deps)
├── dependencies/
│   ├── auth.py          # get_current_user
│   └── db.py            # get_db
├── services/
│   ├── auth_service.py
│   ├── user_service.py
│   ├── note_service.py
│   └── note_share_service.py
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic schemas
└── routers/             # Endpoints grouped by resource

tests/
├── conftest.py          # Fixtures: DB, client, auth helpers
├── test_auth.py
├── test_notes.py
└── test_note_share.py

## Database Schema

### users
| Column     | Type      | Notes                    |
|------------|-----------|--------------------------|
| id         | UUID (PK) |                          |
| username   | VARCHAR   | unique                   |
| email      | VARCHAR   | unique                   |
| password   | VARCHAR   | bcrypt hash              |
| created_at | TIMESTAMP |                          |

### notes
| Column     | Type      | Notes                    |
|------------|-----------|--------------------------|
| id         | UUID (PK) |                          |
| owner_id   | UUID (FK) | → users.id               |
| title      | VARCHAR   |                          |
| content    | TEXT      |                          |
| created_at | TIMESTAMP |                          |
| deleted_at | TIMESTAMP | NULL = active (soft del) |

### note_shares
| Column         | Type      | Notes                        |
|----------------|-----------|------------------------------|
| id             | UUID (PK) |                              |
| note_id        | UUID (FK) | → notes.id                   |
| shared_with    | UUID (FK) | → users.id                   |
| role           | VARCHAR   | 'viewer' / 'editor'          |
| created_at     | TIMESTAMP |                              |
|                |           | UNIQUE(note_id, shared_with) |
