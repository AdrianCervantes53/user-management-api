# API Reference

## Authentication

### Login
**Method**: POST
**URL**: /auth/login
**Content-Type**: application/x-www-form-urlencoded
**Request Body**:
```
username=string&password=string
```
**Response**: 
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

## Users

### Register User
**Method**: POST
**URL**: /users
**Auth Required**: No
**Request Body**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```
**Response**: 201 Created
```json
{
  "id": "uuid",
  "username": "string",
  "email": "string"
}
```

### Get All Users
**Method**: GET
**URL**: /users
**Auth Required**: Yes

### Get Current User
**Method**: GET
**URL**: /users/me
**Auth Required**: Yes

### Get User by ID
**Method**: GET
**URL**: /users/by-id/{user_id}
**Auth Required**: No

## Notes

### Create Note
**Method**: POST
**URL**: /notes
**Auth Required**: Yes
**Request Body**:
```json
{
  "title": "string",
  "content": "string"
}
```
**Response**: 
```json
{
  "id": "uuid",
  "title": "string",
  "content": "string",
  "owner_id": "uuid"
}
```

### Get My Notes
**Method**: GET
**URL**: /notes
**Auth Required**: Yes

### Get Note by ID
**Method**: GET
**URL**: /notes/{note_id}
**Auth Required**: Yes

### Delete Note
**Method**: DELETE
**URL**: /notes/{note_id}
**Auth Required**: Yes
**Response**: 204 No Content
