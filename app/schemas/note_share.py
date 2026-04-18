from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Literal

class NoteShareCreate(BaseModel):
    shared_with: UUID
    role: Literal['editor', 'viewer']
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "shared_with": "123e4567-e89b-12d3-a456-426614174000",
                "role": "viewer"
            }
        }
    )
    
class NoteShareResponse(BaseModel):
    id: UUID
    note_id: UUID
    shared_with: UUID
    role: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes = True)