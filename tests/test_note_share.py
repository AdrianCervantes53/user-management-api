def test_share_note_success(client, auth_headers, another_user_token):
    # Usuario 1 crea nota
    response = client.post("/notes/", json={
        "title": "Nota",
        "content": "Contenido"
    }, headers=auth_headers)
    note_id = response.json()["id"]
    
    user2_id = client.get("/users/me", headers=another_user_token).json()["id"]
    response = client.post(f"/notes/{note_id}/share", json={
        "shared_with": user2_id,
        "role": "viewer"
    }, headers=auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["note_id"] == note_id
    assert data["shared_with"] == user2_id
    assert data["role"] == "viewer"
    
def test_share_note_invalid_role(client, auth_headers, another_user_token):
    response = client.post("/notes/", json={"title": "Nota", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    user2_id = client.get("/users/me", headers=another_user_token).json()["id"]

    response = client.post(f"/notes/{note_id}/share", json={
        "shared_with": user2_id,
        "role": "owner"
    }, headers=auth_headers)

    assert response.status_code == 422


def test_share_note_not_owner(client, auth_headers, another_user_token):
    response = client.post("/notes/", json={"title": "Nota", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    response = client.post(f"/notes/{note_id}/share", json={
        "shared_with": client.get("/users/me", headers=auth_headers).json()["id"],
        "role": "viewer"
    }, headers=another_user_token)

    assert response.status_code == 403
    assert response.json()["detail"] == "Only the owner can share this note"


def test_share_note_with_yourself(client, auth_headers):
    response = client.post("/notes/", json={"title": "Nota", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    user_id = client.get("/users/me", headers=auth_headers).json()["id"]

    response = client.post(f"/notes/{note_id}/share", json={
        "shared_with": user_id,
        "role": "viewer"
    }, headers=auth_headers)

    assert response.status_code == 400
    assert response.json()["detail"] == "Cannot share note with yourself"


def test_share_note_nonexistent_user(client, auth_headers):
    response = client.post("/notes/", json={"title": "Nota", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    response = client.post(f"/notes/{note_id}/share", json={
        "shared_with": "00000000-0000-0000-0000-000000000000",
        "role": "viewer"
    }, headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Target user not found"


def test_share_note_duplicate(client, auth_headers, another_user_token):
    response = client.post("/notes/", json={"title": "Nota", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    user2_id = client.get("/users/me", headers=another_user_token).json()["id"]

    payload = {"shared_with": user2_id, "role": "viewer"}
    client.post(f"/notes/{note_id}/share", json=payload, headers=auth_headers)

    response = client.post(f"/notes/{note_id}/share", json=payload, headers=auth_headers)
    
    assert response.status_code == 409
    assert response.json()["detail"] == "Note already shared with this user"


def test_share_deleted_note(client, auth_headers, another_user_token):
    response = client.post("/notes/", json={"title": "Nota", "content": "Contenido"}, headers=auth_headers)
    note_id = response.json()["id"]

    client.delete(f"/notes/{note_id}", headers=auth_headers)

    user2_id = client.get("/users/me", headers=another_user_token).json()["id"]

    response = client.post(f"/notes/{note_id}/share", json={
        "shared_with": user2_id,
        "role": "viewer"
    }, headers=auth_headers)

    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"