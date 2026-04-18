from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from typing import Optional

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models import User
from app.schemas import NoteCreate, NoteUpdate, NoteResponse
from app.services import note_service

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.post(
    "/",
    response_model=NoteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a note",
    description="Creates a new note owned by the authenticated user.",
)
def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return note_service.create_note(db, current_user.id, note_data)


@router.get(
    "/",
    response_model=list[NoteResponse],
    summary="List my notes",
    description="Returns all notes accessible to the authenticated user (owned and shared). Supports filtering by title, role, and date range, with pagination.",
)
def get_my_notes(
    search: Optional[str] = Query(None, description="Filtrar por título"),
    role: Optional[str] = Query(None, pattern="^(owner|shared)$", description="owner | shared"),
    from_date: Optional[date] = Query(None, description="Notas desde esta fecha (YYYY-MM-DD)"),
    to_date: Optional[date] = Query(None, description="Notas hasta esta fecha (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return note_service.get_my_notes(db, current_user, search, role, from_date, to_date, skip, limit)


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Get a note",
    description="Returns a single note by ID. Accessible if the user is the owner or the note has been shared with them.",
)
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return note_service.get_note_by_id(db, note_id, current_user)


@router.put(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Update a note",
    description="Updates the title and/or content of a note. Only the owner or a user with the 'editor' role can perform this action.",
)
def update_note(
    note_id: UUID,
    note_data: NoteUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return note_service.update_note(db, note_id, note_data, current_user)


@router.delete(
    "/{note_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a note",
    description="Soft-deletes a note by ID. Only the owner can perform this action.",
)
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note_service.delete_note(db, note_id, current_user)
