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
    
# --- GET /notes/ paginación y filtros ---

def test_pagination(client, auth_headers):
    for i in range(5):
        client.post("/notes/", json={"title": f"Nota {i}", "content": "Contenido"}, headers=auth_headers)

    response = client.get("/notes/?skip=0&limit=3", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 3

    response = client.get("/notes/?skip=3&limit=3", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_filter_by_search(client, auth_headers):
    client.post("/notes/", json={"title": "Nota de trabajo", "content": "Contenido"}, headers=auth_headers)
    client.post("/notes/", json={"title": "Nota personal", "content": "Contenido"}, headers=auth_headers)

    response = client.get("/notes/?search=trabajo", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert "trabajo" in data[0]["title"].lower()


def test_filter_by_role_owner(client, auth_headers, another_user_token):
    # Usuario 1 crea nota y la comparte con usuario 2
    response = client.post("/notes/", json={"title": "Nota propia", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]
    user2_id = client.get("/users/me", headers=another_user_token).json()["id"]
    client.post(f"/notes/{note_id}/share", json={"shared_with": user2_id, "role": "viewer"}, headers=auth_headers)

    # Usuario 2 filtra solo por owner → no debe ver la nota compartida
    response = client.get("/notes/?role=owner", headers=another_user_token)
    assert response.status_code == 200
    ids = [n["id"] for n in response.json()]
    assert note_id not in ids


def test_filter_by_role_shared(client, auth_headers, another_user_token):
    # Usuario 1 crea una nota propia y una compartida con usuario 2
    client.post("/notes/", json={"title": "Nota propia u2", "content": "Contenido"}, headers=another_user_token)

    response = client.post("/notes/", json={"title": "Nota compartida", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]
    user2_id = client.get("/users/me", headers=another_user_token).json()["id"]
    client.post(f"/notes/{note_id}/share", json={"shared_with": user2_id, "role": "viewer"}, headers=auth_headers)

    # Usuario 2 filtra solo por shared → solo ve la compartida, no la propia
    response = client.get("/notes/?role=shared", headers=another_user_token)
    assert response.status_code == 200
    ids = [n["id"] for n in response.json()]
    assert note_id in ids


def test_filter_invalid_role(client, auth_headers):
    response = client.get("/notes/?role=admin", headers=auth_headers)
    assert response.status_code == 422


def test_no_duplicate_notes(client, auth_headers, another_user_token):
    # Verifica que una nota compartida no aparezca duplicada en el listado
    response = client.post("/notes/", json={"title": "Sin duplicados", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]
    user2_id = client.get("/users/me", headers=another_user_token).json()["id"]
    client.post(f"/notes/{note_id}/share", json={"shared_with": user2_id, "role": "viewer"}, headers=auth_headers)

    response = client.get("/notes/", headers=auth_headers)
    ids = [n["id"] for n in response.json()]
    assert ids.count(note_id) == 1


# --- PUT /notes/{note_id} ---

def test_owner_can_update_note(client, auth_headers):
    response = client.post("/notes/", json={"title": "Original", "content": "Contenido original"}, headers=auth_headers)
    note_id = response.json()["id"]

    response = client.put(f"/notes/{note_id}", json={"title": "Actualizado", "content": "Contenido actualizado"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Actualizado"
    assert data["content"] == "Contenido actualizado"


def test_editor_can_update_any_note(client, auth_headers, editor_user_token):
    response = client.post("/notes/", json={"title": "Nota del owner", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    response = client.put(f"/notes/{note_id}", json={"title": "Editada por editor"}, headers=editor_user_token)
    assert response.status_code == 200
    assert response.json()["title"] == "Editada por editor"


def test_viewer_cannot_update_note(client, auth_headers, another_user_token):
    response = client.post("/notes/", json={"title": "Nota protegida", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    response = client.put(f"/notes/{note_id}", json={"title": "Intento de edición"}, headers=another_user_token)
    assert response.status_code == 403
    assert response.json()["detail"] == "Not allowed to edit this note"


def test_partial_update_only_title(client, auth_headers):
    response = client.post("/notes/", json={"title": "Título original", "content": "Contenido original"}, headers=auth_headers)
    note = response.json()
    note_id = note["id"]

    response = client.put(f"/notes/{note_id}", json={"title": "Nuevo título"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Nuevo título"
    assert data["content"] == "Contenido original"


def test_update_nonexistent_note(client, auth_headers):
    fake_id = "00000000-0000-0000-0000-000000000000"
    response = client.put(f"/notes/{fake_id}", json={"title": "No existe"}, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_update_deleted_note(client, auth_headers):
    response = client.post("/notes/", json={"title": "A borrar", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    client.delete(f"/notes/{note_id}", headers=auth_headers)

    response = client.put(f"/notes/{note_id}", json={"title": "Editando borrada"}, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"
