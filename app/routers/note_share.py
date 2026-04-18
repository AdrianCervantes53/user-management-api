from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.dependencies.auth import get_current_user
from app.dependencies.db import get_db
from app.models import User
from app.schemas import NoteShareCreate, NoteShareResponse
from app.services import note_share_service

router = APIRouter(prefix="/notes", tags=["Note Shares"])


@router.post(
    "/{note_id}/share",
    response_model=NoteShareResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Share a note",
    description="Shares a note with another user. Only the note owner can share it. The target user can be assigned 'viewer' or 'editor' role.",
)
def share_note(
    note_id: UUID,
    payload: NoteShareCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return note_share_service.share_note(db, note_id, payload, current_user)
