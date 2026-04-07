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
    
def test_note_access_control(client):
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
    response = client.post("/notes/", json={
        "title": "Nota 1",
        "content": "Contenido"
    }, headers={"Authorization": f"Bearer {token1}"})
    note_id = response.json()["id"]
    
    # Usuario 2 intenta obtener nota de usuario 1 → debe fallar
    response = client.get(f"/notes/{note_id}", headers={"Authorization": f"Bearer {token2}"})
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"
    
    """
    # Usuario 2 intenta actualizar nota de usuario 1 → debe fallar
    response = client.put(f"/notes/{note_id}", json={
        "title": "Nota 1 editada",
        "content": "Contenido editado"
    }, headers={"Authorization": f"Bearer {token2}"})
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"
    """
    
    
    # Usuario 2 intenta eliminar nota de usuario 1 → debe fallar
    response = client.delete(f"/notes/{note_id}", headers={"Authorization": f"Bearer {token2}"})
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

