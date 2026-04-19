# API Reference

Full interactive docs available at `http://localhost:8000/docs` when the server is running.

---

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header:
```
Authorization: Bearer <access_token>
```

---

### `POST /auth/login`

Authenticate with email and password. Returns a JWT.

**Content-Type:** `application/x-www-form-urlencoded`

| Field | Type | Description |
|-------|------|-------------|
| `username` | string | User's email address |
| `password` | string | User's password |

**Response `200`**
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer"
}
```

**Errors:** `401` Invalid credentials.

---

## Users

### `POST /users/`

Register a new user. No authentication required.

**Request body**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

| Field | Constraints |
|-------|-------------|
| `password` | 8–64 characters |
| `email` | Must be unique |
| `username` | Must be unique |

**Response `201`**
```json
{
  "id": "uuid",
  "username": "johndoe",
  "email": "john@example.com",
  "is_active": true,
  "created_at": "2026-04-18T00:00:00"
}
```

**Errors:** `409` Email already registered.

---

### `GET /users/`

List all registered users. Requires authentication.

**Response `200`** — Array of user objects (same schema as above).

---

### `GET /users/me`

Returns the profile of the currently authenticated user.

**Response `200`** — User object.

---

### `GET /users/by-id/{user_id}`

Get a user by their UUID. No authentication required.

**Response `200`** — User object.  
**Errors:** `404` User not found.

---

## Notes

### `POST /notes/`

Create a note owned by the authenticated user.

**Request body**
```json
{
  "title": "My note",
  "content": "Note content here"
}
```

**Response `201`**
```json
{
  "id": "uuid",
  "title": "My note",
  "content": "Note content here",
  "owner_id": "uuid",
  "created_at": "2026-04-18T00:00:00",
  "updated_at": "2026-04-18T00:00:00"
}
```

---

### `GET /notes/`

Returns all notes accessible to the authenticated user: notes they own and notes shared with them. Supports filtering and pagination.

**Query parameters**

| Param | Type | Description |
|-------|------|-------------|
| `search` | string | Filter by title (case-insensitive, partial match) |
| `role` | `owner` \| `shared` | Filter by ownership. Omit to return both. |
| `from_date` | `YYYY-MM-DD` | Include notes created on or after this date |
| `to_date` | `YYYY-MM-DD` | Include notes created on or before this date |
| `skip` | int ≥ 0 | Pagination offset (default: `0`) |
| `limit` | 1–100 | Max results to return (default: `20`) |

**Response `200`** — Array of note objects.  
**Errors:** `422` Invalid `role` value (only `owner` or `shared` accepted).

---

### `GET /notes/{note_id}`

Get a specific note by ID. Accessible to the owner or any user the note has been shared with.

**Response `200`** — Note object.  
**Errors:** `403` Not allowed to access this note. `404` Note not found.

---

### `PUT /notes/{note_id}`

Update the title and/or content of a note. Allowed if the authenticated user is:
- the **owner** of the note, or
- has a `NoteShare` entry for this note with `role = "editor"`.

**Request body** (all fields optional)
```json
{
  "title": "Updated title",
  "content": "Updated content"
}
```

**Response `200`** — Updated note object.  
**Errors:** `403` Not allowed to edit this note. `404` Note not found or already deleted.

---

### `DELETE /notes/{note_id}`

Soft-deletes a note. Only the owner can delete. The note is not physically removed — a `deleted_at` timestamp is set and the note is excluded from all queries.

**Response `204`** No content.  
**Errors:** `403` Only the owner can delete this note. `404` Note not found.

---

## Note sharing

### `POST /notes/{note_id}/share`

Share a note with another user. Only the note owner can share it.

**Request body**
```json
{
  "shared_with": "uuid",
  "role": "viewer"
}
```

| Field | Values | Description |
|-------|--------|-------------|
| `shared_with` | UUID | ID of the user to share with |
| `role` | `viewer` \| `editor` | `viewer` can read; `editor` can read and update |

**Response `201`**
```json
{
  "id": "uuid",
  "note_id": "uuid",
  "shared_with": "uuid",
  "role": "viewer",
  "created_at": "2026-04-18T00:00:00"
}
```

**Errors:**
- `400` Cannot share a note with yourself.
- `403` Only the note owner can share it.
- `404` Note not found or already deleted. Target user not found.
- `409` Note already shared with this user.

---

## Role model

Roles are **scoped per note**, not global to a user. The same user can be an `editor` on one note and a `viewer` on another. There is no concept of a "global editor" — permissions are always evaluated against the `note_shares` table for the specific note being accessed.

| Role | Read note | Update note | Delete note | Share note |
|------|-----------|-------------|-------------|------------|
| Owner | ✅ | ✅ | ✅ | ✅ |
| Editor | ✅ | ✅ | ❌ | ❌ |
| Viewer | ✅ | ❌ | ❌ | ❌ |
