import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status

from app.models.audio import AudioFile, SourceType
from app.db.database import SessionLocal


# Configuration
ALLOWED_EXTENSIONS = {'.wav', '.mp3', '.m4a', '.ogg', '.webm'}
MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB
UPLOAD_DIR = Path(__file__).parent.parent.parent.parent / "uploads" / "audio"


def ensure_upload_dir():
    """Ensure upload directory exists."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_audio_file(file: UploadFile) -> None:
    """Validate audio file type, size, and content."""
    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Check file size
    file.file.seek(0, os.SEEK_END)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty"
        )
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds maximum limit of {MAX_FILE_SIZE / (1024 * 1024)}MB"
        )


def generate_secure_filename(original_filename: str) -> str:
    """Generate secure UUID-based filename."""
    file_ext = Path(original_filename).suffix.lower()
    return f"{uuid.uuid4()}{file_ext}"


def save_uploaded_audio(file: UploadFile, user_id: int) -> AudioFile:
    """Save uploaded audio file and create database record."""
    ensure_upload_dir()
    validate_audio_file(file)
    
    # Generate secure filename
    stored_filename = generate_secure_filename(file.filename)
    file_path = UPLOAD_DIR / stored_filename
    
    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            file.file.seek(0)
            buffer.write(file.file.read())
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Get file size
    file_size = file_path.stat().st_size
    
    # Create database record
    db = SessionLocal()
    try:
        audio_file = AudioFile(
            user_id=user_id,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_type=Path(file.filename).suffix.lower(),
            file_size_bytes=file_size,
            source_type=SourceType.UPLOAD
        )
        db.add(audio_file)
        db.commit()
        db.refresh(audio_file)
        return audio_file
    except Exception as e:
        db.rollback()
        # Clean up file if database insert fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create database record: {str(e)}"
        )
    finally:
        db.close()


def save_recorded_audio(file_data: bytes, user_id: int, original_filename: str = "recording.webm") -> AudioFile:
    """Save recorded audio blob and create database record."""
    ensure_upload_dir()
    
    # Generate secure filename
    stored_filename = generate_secure_filename(original_filename)
    file_path = UPLOAD_DIR / stored_filename
    
    # Validate file size
    if len(file_data) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Recording is empty"
        )
    
    if len(file_data) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Recording size exceeds maximum limit of {MAX_FILE_SIZE / (1024 * 1024)}MB"
        )
    
    # Save file to disk
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save recording: {str(e)}"
        )
    
    # Get file size
    file_size = file_path.stat().st_size
    
    # Create database record
    db = SessionLocal()
    try:
        audio_file = AudioFile(
            user_id=user_id,
            original_filename=original_filename,
            stored_filename=stored_filename,
            file_path=str(file_path),
            file_type=Path(original_filename).suffix.lower(),
            file_size_bytes=file_size,
            source_type=SourceType.RECORD
        )
        db.add(audio_file)
        db.commit()
        db.refresh(audio_file)
        return audio_file
    except Exception as e:
        db.rollback()
        # Clean up file if database insert fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create database record: {str(e)}"
        )
    finally:
        db.close()
