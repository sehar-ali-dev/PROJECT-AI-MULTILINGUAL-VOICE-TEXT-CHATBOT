from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.transcription import TranscribeRequest, TranscriptionResponse
from app.services.transcription_service import transcribe_audio, get_transcription
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/transcribe", response_model=TranscriptionResponse, status_code=status.HTTP_201_CREATED)
async def transcribe(
    request: TranscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Transcribe an audio file using STT provider."""
    try:
        transcription = await transcribe_audio(
            audio_id=request.audio_id,
            user_id=current_user.id,
            source_language=request.source_language
        )
        return transcription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription failed: {str(e)}"
        )


@router.get("/transcriptions/{transcription_id}", response_model=TranscriptionResponse)
async def get_transcription_endpoint(
    transcription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific transcription by ID."""
    try:
        transcription = get_transcription(transcription_id, current_user.id)
        return transcription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transcription: {str(e)}"
        )


@router.get("/transcriptions", response_model=list[TranscriptionResponse])
async def list_transcriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all transcriptions for the current user."""
    from app.models.transcription import Transcription
    
    transcriptions = db.query(Transcription).filter(
        Transcription.user_id == current_user.id
    ).order_by(Transcription.created_at.desc()).all()
    
    return [
        TranscriptionResponse(
            id=t.id,
            audio_id=t.audio_id,
            user_id=t.user_id,
            source_language=t.source_language,
            ai_transcription=t.ai_transcription,
            confidence_score=t.confidence_score,
            provider_metadata=t.provider_metadata,
            status=t.status,
            created_at=t.created_at
        )
        for t in transcriptions
    ]
