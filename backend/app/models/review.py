from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum
from app.db.database import Base


class ReviewStatus(str, Enum):
    REVIEWED = "reviewed"
    COMPLETED = "completed"


class HumanReview(Base):
    __tablename__ = "human_reviews"

    id = Column(Integer, primary_key=True, index=True)
    transcription_id = Column(Integer, ForeignKey("transcriptions.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    corrected_text = Column(Text, nullable=True)
    review_notes = Column(Text, nullable=True)
    status = Column(SQLEnum(ReviewStatus), default=ReviewStatus.REVIEWED, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    transcription = relationship("Transcription", backref="human_review")
    user = relationship("User", backref="reviews")
