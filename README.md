# User Management API

REST API de gestión de usuarios con autenticación JWT y sistema de notas, construida con **FastAPI** y **PostgreSQL**. Proyecto de portafolio en desarrollo activo.

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
| GET | `/notes/` | Listar mis notas | Sí |
| GET | `/notes/{note_id}` | Ver una nota específica | Sí |
| DELETE | `/notes/{note_id}` | Eliminar una nota | Sí |

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

## Estado del proyecto

Este proyecto está en desarrollo activo. Features planeadas:

- [ ] Tests con `pytest` y `httpx`
- [ ] Sistema de roles (admin / user)
- [ ] Refresh tokens
- [ ] `PUT /notes/{note_id}` — editar notas
- [ ] `PUT /users/me` — actualizar perfil
- [ ] Paginación en listados
- [ ] CI/CD con GitHub Actions

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
├── alembic/                 # Migraciones de BD
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
