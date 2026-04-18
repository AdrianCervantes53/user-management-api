from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone, date
from typing import Optional

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models import User, Note, NoteShare
from app.schemas import NoteCreate, NoteResponse

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/", response_model=NoteResponse)
def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = Note(
        title=note_data.title,
        content=note_data.content,
        owner_id=current_user.id
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    return note

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
    def apply_common_filters(query, model):
        query = query.filter(model.deleted_at.is_(None))
        if search:
            query = query.filter(model.title.ilike(f"%{search}%"))
        if from_date:
            query = query.filter(model.created_at >= datetime.combine(from_date, datetime.min.time()))
        if to_date:
            query = query.filter(model.created_at <= datetime.combine(to_date, datetime.max.time()))
        return query
    
    if role == "owner":
        query = db.query(Note).filter(Note.owner_id == current_user.id)
        query = apply_common_filters(query, Note)
        return query.order_by(Note.created_at.desc()).offset(skip).limit(limit).all()

    if role == "shared":
        query = db.query(Note).join(NoteShare, NoteShare.note_id == Note.id).filter(
            NoteShare.shared_with == current_user.id
        )
        query = apply_common_filters(query, Note)
        return query.order_by(Note.created_at.desc()).offset(skip).limit(limit).all()

    # Sin filtro de rol: owned + shared sin duplicados
    owned_ids = db.query(Note.id).filter(Note.owner_id == current_user.id)
    shared_ids = db.query(Note.id).join(NoteShare, NoteShare.note_id == Note.id).filter(
        NoteShare.shared_with == current_user.id
    )

    query = db.query(Note).filter(Note.id.in_(owned_ids.union(shared_ids)))
    query = apply_common_filters(query, Note)
    return query.order_by(Note.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.deleted_at.is_(None)
    ).first()
    
    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    is_owner = note.owner_id == current_user.id
    is_shared = db.query(NoteShare).filter(
        NoteShare.note_id == note_id,
        NoteShare.shared_with == current_user.id
    ).first()
    
    if not is_owner and not is_shared:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to access this note")
    
    return note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.deleted_at.is_(None)
    ).first()

    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")
    
    if note.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can delete this note")

    note.deleted_at = datetime.now(timezone.utc)
    db.commit()