import json
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.audio import AudioFile
from app.models.transcription import Transcription, TranscriptionStatus
from app.schemas.transcription import TranscriptionResponse, AudioMetadata
from app.db.database import SessionLocal
from app.core.config import settings
from app.services.mock_ai import MockSpeechToTextProvider


async def transcribe_audio(audio_id: int, user_id: int, source_language: Optional[str] = None) -> TranscriptionResponse:
    """Transcribe audio file using STT provider and save to database."""
    db = SessionLocal()
    try:
        # Retrieve audio file
        audio_file = db.query(AudioFile).filter(
            AudioFile.id == audio_id,
            AudioFile.user_id == user_id
        ).first()
        
        if not audio_file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Audio file not found"
            )
        
        # Create transcription record with PENDING status
        transcription = Transcription(
            audio_id=audio_id,
            user_id=user_id,
            source_language=source_language,
            status=TranscriptionStatus.PROCESSING
        )
        db.add(transcription)
        db.commit()
        db.refresh(transcription)
        
        # Perform STT using provider
        try:
            if settings.USE_MOCK_AI:
                provider = MockSpeechToTextProvider()
                result = await provider.transcribe(audio_file.file_path, source_language)
                
                # Update transcription with results
                transcription.ai_transcription = result["text"]
                transcription.source_language = result.get("language", source_language)
                transcription.confidence_score = result.get("confidence")
                transcription.provider_metadata = json.dumps(result)
                transcription.status = TranscriptionStatus.COMPLETED
            else:
                # Future: Integrate real STT provider (OpenAI Whisper, etc.)
                raise HTTPException(
                    status_code=status.HTTP_501_NOT_IMPLEMENTED,
                    detail="Real STT provider not yet implemented. Set USE_MOCK_AI=True in .env"
                )
            
            db.commit()
            db.refresh(transcription)
            
        except Exception as e:
            # Mark as failed if STT processing fails
            transcription.status = TranscriptionStatus.FAILED
            transcription.provider_metadata = json.dumps({"error": str(e)})
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"STT processing failed: {str(e)}"
            )
        
        return TranscriptionResponse(
            id=transcription.id,
            audio_id=transcription.audio_id,
            user_id=transcription.user_id,
            source_language=transcription.source_language,
            ai_transcription=transcription.ai_transcription,
            confidence_score=transcription.confidence_score,
            provider_metadata=transcription.provider_metadata,
            status=transcription.status,
            created_at=transcription.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Transcription service error: {str(e)}"
        )
    finally:
        db.close()


def get_transcription(transcription_id: int, user_id: int) -> TranscriptionResponse:
    """Get a specific transcription by ID with audio metadata."""
    db = SessionLocal()
    try:
        # Join with AudioFile to get metadata
        transcription = db.query(Transcription).join(
            AudioFile, Transcription.audio_id == AudioFile.id
        ).filter(
            Transcription.id == transcription_id,
            Transcription.user_id == user_id
        ).first()
        
        if not transcription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcription not found"
            )
        
        # Build audio metadata
        audio_metadata = None
        if transcription.audio_file:
            audio_metadata = AudioMetadata(
                id=transcription.audio_file.id,
                original_filename=transcription.audio_file.original_filename,
                file_type=transcription.audio_file.file_type,
                file_size_bytes=transcription.audio_file.file_size_bytes,
                source_type=transcription.audio_file.source_type.value,
                file_path=transcription.audio_file.file_path,
                duration_seconds=transcription.audio_file.duration_seconds
            )
        
        return TranscriptionResponse(
            id=transcription.id,
            audio_id=transcription.audio_id,
            user_id=transcription.user_id,
            source_language=transcription.source_language,
            ai_transcription=transcription.ai_transcription,
            confidence_score=transcription.confidence_score,
            provider_metadata=transcription.provider_metadata,
            status=transcription.status,
            created_at=transcription.created_at,
            audio_metadata=audio_metadata
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve transcription: {str(e)}"
        )
    finally:
        db.close()
