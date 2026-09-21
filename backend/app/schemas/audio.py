from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.audio import SourceType


class AudioFileResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    stored_filename: str
    file_path: str
    file_type: str
    file_size_bytes: int
    duration_seconds: Optional[int]
    source_type: SourceType
    created_at: datetime

    class Config:
        from_attributes = True


class AudioUploadResponse(BaseModel):
    id: int
    original_filename: str
    file_type: str
    file_size_bytes: int
    source_type: SourceType
    message: str
