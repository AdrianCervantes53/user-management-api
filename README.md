# User Management API

API multiusuario para gestión de notas seguras con control de acceso y compartición entre usuarios. Proyecto de portafolio enfocado en demostrar autenticación, autorización y modelado de datos relacional con **FastAPI** y **PostgreSQL**.

## Stack tecnológico

- **Python 3.11+** + **FastAPI**
- **PostgreSQL 15** como base de datos
- **SQLAlchemy 2.0** como ORM
- **Alembic** para migraciones
- **JWT** (python-jose) para autenticación
- **bcrypt** (passlib) para hashing de contraseñas
- **Pydantic v2** para validación de datos
- **Docker** + **Docker Compose** para containerización
- **Swagger UI** para documentación interactiva
- **pytest** + **httpx** para testing

## Requisitos previos

- [Docker](https://www.docker.com/) y Docker Compose
- O bien Python 3.11+ y PostgreSQL instalados localmente

## Instalación y uso

### Con Docker (recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/AdrianCervantes53/user-management-api.git
cd user-management-api

# 2. Crear el archivo de variables de entorno
cp .env.example .env
# Edita .env con tus valores

# 3. Levantar los servicios
docker compose up --build

# 4. Aplicar migraciones
docker compose exec backend alembic upgrade head
```

La API estará disponible en `http://localhost:8000`

### Sin Docker

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear el archivo .env
cp .env.example .env
# Edita .env con tus valores

# 4. Aplicar migraciones
alembic upgrade head

# 5. Levantar el servidor
uvicorn app.main:app --reload
```

## Documentación de la API

Una vez levantado el servidor, la documentación interactiva está disponible en:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## Endpoints

### Auth
| Método | Endpoint | Descripción | Auth requerida |
|--------|----------|-------------|----------------|
| POST | `/auth/login` | Login, devuelve JWT | No |

### Users
| Método | Endpoint | Descripción | Auth requerida |
|--------|----------|-------------|----------------|
| POST | `/users/` | Registro de nuevo usuario | No |
| GET | `/users/` | Listar todos los usuarios | Sí |
| GET | `/users/me` | Perfil del usuario autenticado | Sí |
| GET | `/users/by-id/{user_id}` | Buscar usuario por ID | No |

### Notes
| Método | Endpoint | Descripción | Auth requerida |
|--------|----------|-------------|----------------|
| POST | `/notes/` | Crear nota | Sí |
| GET | `/notes/` | Listar notas propias y compartidas (con paginación y filtros) | Sí |
| GET | `/notes/{note_id}` | Ver una nota específica | Sí |
| DELETE | `/notes/{note_id}` | Eliminar una nota (soft delete) | Sí |
| POST | `/notes/{note_id}/share` | Compartir nota con otro usuario | Sí |

## Uso básico

**1. Registrar un usuario:**
```bash
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "adrian", "email": "adrian@example.com", "password": "secreto123"}'
```

**2. Hacer login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -F "username=adrian@example.com" \
  -F "password=secreto123"
```

**3. Usar el token en endpoints protegidos:**
```bash
curl http://localhost:8000/users/me \
  -H "Authorization: Bearer <tu_token>"
```

**4. Compartir una nota:**
```bash
curl -X POST http://localhost:8000/notes/<note_id>/share \
  -H "Authorization: Bearer <tu_token>" \
  -H "Content-Type: application/json" \
  -d '{"shared_with": "<user_id>", "role": "viewer"}'
```

## Testing

Los tests usan una base de datos PostgreSQL separada para no afectar los datos de desarrollo. Cada test corre en su propia transacción que se revierte al finalizar.

**1. Crear la base de datos de pruebas en PostgreSQL:**
```sql
CREATE DATABASE users_db_test;
```

**2. Agregar la variable `TEST_DATABASE_URL` a tu `.env`:**
```env
TEST_DATABASE_URL=postgresql://usuario:password@localhost:5432/users_db_test
```

**3. Correr los tests:**
```bash
pytest tests/ -v
```

## Estado del proyecto

### Implementado
- [x] Autenticación con JWT y hashing de contraseñas con bcrypt
- [x] CRUD de notas por usuario autenticado
- [x] Compartición de notas entre usuarios (`POST /notes/{id}/share`)
- [x] Control de acceso por rol (owner / editor / viewer)
- [x] Soft delete en notas (`deleted_at`)
- [x] Auditoría de registros (`created_at`, `updated_at`)
- [x] Tests con `pytest` + `httpx` e isolation por transacción

### En desarrollo
- [ ] Paginación y filtros en listados
- [ ] `PUT /notes/{note_id}` — editar nota
- [ ] `PUT /users/me` — actualizar perfil

### Roadmap
- [ ] Rate limiting (con Redis)
- [ ] Deploy en Railway/Render
- [ ] CI/CD con GitHub Actions
- [ ] Refresh tokens

## Estructura del proyecto

```
├── app/
│   ├── main.py              # Entry point
│   ├── database.py          # Conexión a la BD
│   ├── core/
│   │   ├── config.py        # Variables de entorno
│   │   ├── security.py      # JWT y hashing
│   │   └── dependencies.py  # Dependency injection
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Schemas Pydantic
│   └── routers/             # Endpoints por recurso
├── tests/
│   ├── conftest.py          # Fixtures y configuración de pytest
│   └── ...                  # Archivos de test por recurso
├── alembic/                 # Migraciones de BD
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
