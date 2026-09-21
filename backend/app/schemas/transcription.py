from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.transcription import TranscriptionStatus


class TranscribeRequest(BaseModel):
    audio_id: int = Field(..., description="ID of the audio file to transcribe")
    source_language: Optional[str] = Field(None, description="Source language code (e.g., 'en', 'ur', 'hi')")


class TranscriptionCreate(BaseModel):
    audio_id: int
    user_id: int
    source_language: Optional[str] = None
    ai_transcription: Optional[str] = None
    confidence_score: Optional[float] = None
    provider_metadata: Optional[str] = None
    status: TranscriptionStatus = TranscriptionStatus.PENDING


class TranscriptionResponse(BaseModel):
    id: int
    audio_id: int
    user_id: int
    source_language: Optional[str]
    ai_transcription: Optional[str]
    confidence_score: Optional[float]
    provider_metadata: Optional[str]
    status: TranscriptionStatus
    created_at: datetime

    class Config:
        from_attributes = True
