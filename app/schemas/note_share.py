from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Literal

class NoteShareCreate(BaseModel):
    shared_with: UUID
    role: Literal['editor', 'viewer']
    
    
class NoteShareResponse(BaseModel):
    id: UUID
    note_id: UUID
    shared_with: UUID
    role: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes = True)