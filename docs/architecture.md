# Architecture

## Overview
API RESTful para gestión de usuarios y notas, construida con FastAPI (Python). Utiliza PostgreSQL como base de datos con SQLAlchemy como ORM y Alembic para migraciones. La autenticación se maneja con JWT.

## Stack
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL con SQLAlchemy
- **Migrations**: Alembic
- **Authentication**: JWT (OAuth2)
- **Containerization**: Docker

## Structure
```
app/
├── main.py           # Entry point
├── database.py       # DB configuration
├── core/
│   ├── config.py    # Settings
│   ├── security.py  # Password hashing, JWT
│   └── dependencies.py  # Auth dependencies
├── models/          # SQLAlchemy models
├── routers/         # API endpoints
├── schemas/         # Pydantic schemas
└── services/        # Business logic
```

## Diagram
```
   [Client]
      |
      v
[FastAPI Backend]
      |
      v
[PostgreSQL]
```

## Security
- Password hashing: bcrypt
- Token: JWT with SECRET_KEY
- OAuth2 Password flow
