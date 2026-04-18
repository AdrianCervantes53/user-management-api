from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone, date
from typing import Optional
from fastapi import HTTPException, status

from app.models import Note, NoteShare
from app.models.user import User
from app.schemas import NoteCreate, NoteUpdate


def create_note(db: Session, owner_id: UUID, note_data: NoteCreate) -> Note:
    note = Note(
        title=note_data.title,
        content=note_data.content,
        owner_id=owner_id
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_my_notes(
    db: Session,
    current_user: User,
    search: Optional[str] = None,
    role: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    skip: int = 0,
    limit: int = 20,
) -> list[Note]:
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

    owned_ids = db.query(Note.id).filter(Note.owner_id == current_user.id)
    shared_ids = db.query(Note.id).join(NoteShare, NoteShare.note_id == Note.id).filter(
        NoteShare.shared_with == current_user.id
    )
    query = db.query(Note).filter(Note.id.in_(owned_ids.union(shared_ids)))
    query = apply_common_filters(query, Note)
    return query.order_by(Note.created_at.desc()).offset(skip).limit(limit).all()


def get_note_by_id(db: Session, note_id: UUID, current_user: User) -> Note:
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


def update_note(db: Session, note_id: UUID, note_data: NoteUpdate, current_user: User) -> Note:
    note = db.query(Note).filter(
        Note.id == note_id,
        Note.deleted_at.is_(None)
    ).first()

    if not note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    is_owner = note.owner_id == current_user.id
    is_editor = db.query(NoteShare).filter(
        NoteShare.note_id == note_id,
        NoteShare.shared_with == current_user.id,
        NoteShare.role == "editor"
    ).first()

    if not is_owner and not is_editor:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to edit this note")

    if note_data.title is not None:
        note.title = note_data.title
    if note_data.content is not None:
        note.content = note_data.content

    note.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, note_id: UUID, current_user: User) -> None:
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
