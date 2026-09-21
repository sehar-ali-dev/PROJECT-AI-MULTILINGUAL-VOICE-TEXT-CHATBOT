from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.audio import AudioFileResponse, AudioUploadResponse
from app.services.audio_service import save_uploaded_audio, save_recorded_audio
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/upload", response_model=AudioUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload an audio file."""
    try:
        audio_file = save_uploaded_audio(file, current_user.id)
        return AudioUploadResponse(
            id=audio_file.id,
            original_filename=audio_file.original_filename,
            file_type=audio_file.file_type,
            file_size_bytes=audio_file.file_size_bytes,
            source_type=audio_file.source_type,
            message="Audio file uploaded successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload audio: {str(e)}"
        )


@router.post("/record", response_model=AudioUploadResponse, status_code=status.HTTP_201_CREATED)
async def record_audio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save a recorded audio file from microphone."""
    try:
        file_data = await file.read()
        audio_file = save_recorded_audio(file_data, current_user.id, file.filename or "recording.webm")
        return AudioUploadResponse(
            id=audio_file.id,
            original_filename=audio_file.original_filename,
            file_type=audio_file.file_type,
            file_size_bytes=audio_file.file_size_bytes,
            source_type=audio_file.source_type,
            message="Recording saved successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save recording: {str(e)}"
        )


@router.get("/files", response_model=list[AudioFileResponse])
async def list_audio_files(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all audio files for the current user."""
    from app.models.audio import AudioFile
    
    audio_files = db.query(AudioFile).filter(AudioFile.user_id == current_user.id).order_by(AudioFile.created_at.desc()).all()
    return audio_files


@router.get("/files/{audio_id}", response_model=AudioFileResponse)
async def get_audio_file(
    audio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific audio file by ID."""
    from app.models.audio import AudioFile
    
    audio_file = db.query(AudioFile).filter(
        AudioFile.id == audio_id,
        AudioFile.user_id == current_user.id
    ).first()
    
    if not audio_file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audio file not found"
        )
    
    return audio_file
