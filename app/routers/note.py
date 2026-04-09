from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone

from app.core.dependencies import get_current_user
from app.database import get_db
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    owned = db.query(Note).filter(
        Note.owner_id == current_user.id,
        Note.deleted_at.is_(None)
    ).all()
    
    shared = db.query(Note).join(
        NoteShare, NoteShare.note_id == Note.id
    ).filter(
        NoteShare.shared_with == current_user.id,
        Note.deleted_at.is_(None)
    ).all()
    
    return owned + shared

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
    
    if not is_owner or not is_shared:
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