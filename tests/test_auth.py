def test_register_and_login(client):
    # Crear usuario
    response = client.post("/users/", json={
        "username": "testuser",
        "email": "test@email.com",
        "password": "12345678"
    })

    assert response.status_code == 201

    # Login
    response = client.post("/auth/login", data={
        "username": "test@email.com",
        "password": "12345678"
    })

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    
def test_register_duplicate_email(client):
    # Crear usuario
    response = client.post("/users/", json={
        "username": "testuser",
        "email": "test@email.com",
        "password": "12345678"
    })

    assert response.status_code == 201

    # Intentar crear otro usuario con el mismo email
    response = client.post("/users/", json={
        "username": "testuser2",
        "email": "test@email.com",
        "password": "87654321"
    })

    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"
    
def test_login_wrong_password(client):
    # Crear usuario
    response = client.post("/users/", json={
        "username": "testuser",
        "email": "test@email.com",
        "password": "12345678"
    })

    assert response.status_code == 201

    # Intentar login con contraseña incorrecta
    response = client.post("/auth/login", data={
        "username": "test@email.com",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
    
def test_login_nonexistent_email(client):
    # Intentar login con email que no existe
    response = client.post("/auth/login", data={
        "username": "nonexistent@email.com",
        "password": "12345678"
    })

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
    
def test_register_invalid_email(client):
    # Intentar crear usuario con email inválido
    response = client.post("/users/", json={
        "username": "testuser",
        "email": "invalid-email",
        "password": "12345678"
    })

    assert response.status_code == 422  # Unprocessable Entity