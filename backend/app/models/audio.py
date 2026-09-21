from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from enum import Enum
from app.db.database import Base


class SourceType(str, Enum):
    UPLOAD = "upload"
    RECORD = "record"


class AudioFile(Base):
    __tablename__ = "audio_files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    original_filename = Column(String, nullable=False)
    stored_filename = Column(String, nullable=False, unique=True)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    duration_seconds = Column(Integer, nullable=True)
    source_type = Column(SQLEnum(SourceType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
