from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from uuid import UUID

from app.models import User, Note, NoteShare
from app.schemas import NoteShareCreate


def share_note(db: Session, note_id: UUID, payload: NoteShareCreate, current_user: User) -> NoteShare:
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.deleted_at.is_(None)
    ).first()

    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    if note.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can share this note")

    if payload.shared_with == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot share note with yourself")

    target_user = db.query(User).filter(User.id == payload.shared_with).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user not found")

    existing_share = db.query(NoteShare).filter(
        NoteShare.note_id == note_id,
        NoteShare.shared_with == payload.shared_with
    ).first()

    if existing_share:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Note already shared with this user")

    share = NoteShare(note_id=note_id, shared_with=payload.shared_with, role=payload.role)
    db.add(share)
    db.commit()
    db.refresh(share)
    return share