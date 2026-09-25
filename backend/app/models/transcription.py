from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.database import Base


class TranscriptionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Transcription(Base):
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    audio_id = Column(Integer, ForeignKey("audio_files.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    source_language = Column(String, nullable=True)
    ai_transcription = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    provider_metadata = Column(Text, nullable=True)  # JSON string for provider-specific data
    status = Column(SQLEnum(TranscriptionStatus), default=TranscriptionStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationship to AudioFile
    audio_file = relationship("AudioFile", backref="transcriptions")
