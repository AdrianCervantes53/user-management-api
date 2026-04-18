from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import date
from typing import Optional

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models import User
from app.schemas import NoteCreate, NoteResponse
from app.services import note_service

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return note_service.create_note(db, current_user.id, note_data)

@router.get("/", response_model=list[NoteResponse])
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

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return note_service.get_note_by_id(db, note_id, current_user)

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note_service.delete_note(db, note_id, current_user)