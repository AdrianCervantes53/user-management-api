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