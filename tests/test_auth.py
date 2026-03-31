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