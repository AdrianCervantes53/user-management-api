def get_token(client, email, password):
    response = client.post("/auth/login", data={
        "username": email,
        "password": password
    })
    return {"Authorization": f"Bearer {response.json()['access_token']}"}

# --- GET /notes/ ---

def test_notes_isolation(client, auth_headers, another_user_token):
    client.post("/notes/", json={
        "title": "Nota 1",
        "content": "Contenido"
    }, headers=auth_headers)
    
    # Usuario 2 obtiene notas → debe estar vacío
    response = client.get("/notes/", headers=another_user_token)

    assert response.status_code == 200
    assert response.json() == []
    
def test_get_notes_includes_shared(client, auth_headers, another_user_token):
    # Usuario 1 crea una nota
    response = client.post("/notes/", json={"title": "Nota compartida", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    # Obtener el id del usuario 2
    user2_info = client.get("/users/me", headers=another_user_token).json()

    # Usuario 1 comparte la nota con usuario 2
    client.post(f"/notes/{note_id}/share", json={
        "shared_with": user2_info["id"],
        "role": "viewer"
    }, headers=auth_headers)

    # Usuario 2 debe ver la nota en su listado
    response = client.get("/notes/", headers=another_user_token)

    assert response.status_code == 200
    ids = [n["id"] for n in response.json()]
    assert note_id in ids
    
    
# --- GET /notes/{note_id} ---

def test_note_access_control(client, auth_headers, another_user_token):
    response = client.post("/notes/", json={"title": "Nota 1", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    # Usuario 2 sin acceso → 404
    response = client.get(f"/notes/{note_id}", headers=another_user_token)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not allowed to access this note"

    # Usuario 2 intenta eliminar → 404
    response = client.delete(f"/notes/{note_id}", headers=another_user_token)
    assert response.status_code == 403
    assert response.json()["detail"] == "Only the owner can delete this note"


def test_shared_user_can_access_note(client, auth_headers, another_user_token):
    response = client.post("/notes/", json={"title": "Nota compartida", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    user2_info = client.get("/users/me", headers=another_user_token).json()

    client.post(f"/notes/{note_id}/share", json={
        "shared_with": user2_info["id"],
        "role": "viewer"
    }, headers=auth_headers)

    response = client.get(f"/notes/{note_id}", headers=another_user_token)
    assert response.status_code == 200
    assert response.json()["id"] == note_id


# --- DELETE /notes/{note_id} (soft delete) ---

def test_soft_delete(client, auth_headers):
    response = client.post("/notes/", json={"title": "A borrar", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    response = client.delete(f"/notes/{note_id}", headers=auth_headers)
    assert response.status_code == 204

    # La nota ya no debe ser accesible
    response = client.get(f"/notes/{note_id}", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_soft_delete_hides_from_list(client, auth_headers):
    response = client.post("/notes/", json={"title": "A borrar", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    client.delete(f"/notes/{note_id}", headers=auth_headers)

    response = client.get("/notes/", headers=auth_headers)
    ids = [n["id"] for n in response.json()]
    assert note_id not in ids