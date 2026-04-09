from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models import User, Note, NoteShare
from app.schemas import NoteShareCreate, NoteShareResponse

router = APIRouter(prefix="/notes", tags=["Note Shares"])

@router.post("/{note_id}/share", response_class=NoteShareResponse, status_code=status.HTTP_201_CREATED)
def share_note(
    note_id: UUID,
    payload: NoteShareCreate,
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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only the owner can share this note")
    
    if payload.shared_with == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot share note with yourself")
    
    target_user = db.query(User).filter(
        User.id == payload.shared_with,
    ).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")
    
    existing_share = db.query(NoteShare).filter(
        NoteShare.note_id == note_id,
        NoteShare.share_with == payload.shared_with
    ).first()
    
    if existing_share:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Note already shared with this user")
    
    share = NoteShare(
        note_id = note_id,
        shared_with = payload.shared_with,
        role = payload.role,
    )
    db.add(share)
    db.commit()
    db.refresh(share)
    
    return share