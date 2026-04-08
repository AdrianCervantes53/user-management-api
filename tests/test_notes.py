def get_token(client, email, password):
    response = client.post("/auth/login", data={
        "username": email,
        "password": password
    })
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_notes_isolation(client, auth_headers, another_user_token):
    client.post("/notes/", json={
        "title": "Nota 1",
        "content": "Contenido"
    }, headers=auth_headers)
    
    # Usuario 2 obtiene notas → debe estar vacío
    response = client.get("/notes/", headers=another_user_token)

    assert response.status_code == 200
    assert response.json() == []
    
def test_note_access_control(client, auth_headers, another_user_token):
    # Usuario 1 crea nota
    response = client.post("/notes/", json={
        "title": "Nota 1",
        "content": "Contenido"
    }, headers=auth_headers)
    note_id = response.json()["id"]
    
    # Usuario 2 intenta obtener nota de usuario 1 → debe fallar
    response = client.get(f"/notes/{note_id}", headers=another_user_token)
    
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
    response = client.delete(f"/notes/{note_id}", headers=another_user_token)
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

