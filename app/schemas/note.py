from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class NoteCreate(BaseModel):
    title: str
    content: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "My first note",
                "content": "This is the content of my note."
            }
        }
    )


class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Updated title",
                "content": "Updated content."
            }
        }
    )


class NoteResponse(BaseModel):
    id: UUID
    title: str
    content: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
