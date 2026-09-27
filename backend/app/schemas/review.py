from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.review import ReviewStatus


class ReviewCreate(BaseModel):
    transcription_id: int = Field(..., description="ID of the transcription being reviewed")
    corrected_text: str = Field(..., description="Human-corrected transcription text")
    review_notes: Optional[str] = Field(None, description="Optional review notes or comments")


class ReviewUpdate(BaseModel):
    corrected_text: Optional[str] = Field(None, description="Updated corrected transcription text")
    review_notes: Optional[str] = Field(None, description="Updated review notes")
    status: Optional[ReviewStatus] = Field(None, description="Updated review status")


class ReviewResponse(BaseModel):
    id: int
    transcription_id: int
    user_id: int
    corrected_text: Optional[str]
    review_notes: Optional[str]
    status: ReviewStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
