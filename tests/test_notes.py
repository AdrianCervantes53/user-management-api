def get_token(client, email, password):
    response = client.post("/auth/login", data={
        "username": email,
        "password": password
    })
    return response.json()["access_token"]


def test_notes_isolation(client):
    # Crear usuario 1
    client.post("/users/", json={
        "username": "user1",
        "email": "user1@email.com",
        "password": "12345678"
    })

    token1 = get_token(client, "user1@email.com", "12345678")

    # Crear usuario 2
    client.post("/users/", json={
        "username": "user2",
        "email": "user2@email.com",
        "password": "12345678"
    })

    token2 = get_token(client, "user2@email.com", "12345678")

    # Usuario 1 crea nota
    client.post("/notes/", json={
        "title": "Nota 1",
        "content": "Contenido"
    }, headers={"Authorization": f"Bearer {token1}"})

    # Usuario 2 obtiene notas → debe estar vacío
    response = client.get("/notes/", headers={
        "Authorization": f"Bearer {token2}"
    })

    assert response.status_code == 200
    assert response.json() == []