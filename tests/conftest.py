import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base
from app.dependencies.db import get_db

from app.core.config import settings

engine = create_engine(settings.TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    if not settings.TEST_DATABASE_URL:
        raise ValueError("TEST_DATABASE_URL no está configurada en .env")
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    
@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    # Rollback
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    
@pytest.fixture
def registered_user(client):
    user_data = {
        "username": "testuser",
        "email": "test@email.com",
        "password": "12345678"
    }
    client.post("/users/", json=user_data)
    return user_data

@pytest.fixture
def auth_token(client, registered_user):
    response = client.post("/auth/login", data={
        "username": registered_user["email"],
        "password": registered_user["password"]
    })
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def another_user_token(client):
    user_data = {
        "username": "anotheruser",
        "email": "anotheruser@email.com",
        "password": "12345678"
    }
    client.post("/users/", json=user_data)
    response = client.post("/auth/login", data={
        "username": user_data["email"],
        "password": user_data["password"]
    })
    return {"Authorization": f"Bearer {response.json()['access_token']}"}