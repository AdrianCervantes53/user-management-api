def test_note_sharing(client, auth_headers, another_user_token):
    # Usuario 1 crea nota
    response = client.post("/notes/", json={
        "title": "Nota 1",
        "content": "Contenido"
    }, headers=auth_headers)
    note_id = response.json()["id"]
    
    client.post(f"/notes/{note_id}/share", json={
        "shared_with": "",
        "role": "editor"
    }, headers=auth_headers)