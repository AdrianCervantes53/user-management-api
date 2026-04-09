from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models import User, Note
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
    notes = db.query(Note).filter(Note.owner_id == current_user.id).all()
    return notes

@router.get("/{note_id}", response_model=NoteResponse)
def get_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.owner_id == current_user.id
    ).first()
    
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    return note

@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.owner_id == current_user.id
    ).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    db.delete(note)
    db.commit()