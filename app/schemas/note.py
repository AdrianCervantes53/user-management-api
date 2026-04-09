from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteResponse(BaseModel):
    id: UUID
    title: str
    content: str
    owner_id: UUID
    created_at: datetime

    model_config = ConfigDict(from_attributes = True)