from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.transcription import Transcription, TranscriptionStatus
from app.models.review import HumanReview, ReviewStatus
from app.schemas.review import ReviewResponse
from app.db.database import SessionLocal


def submit_review(transcription_id: int, user_id: int, corrected_text: str, review_notes: Optional[str] = None) -> ReviewResponse:
    """Submit or update a human review for a transcription.
    
    This function:
    - Validates that the transcription exists and belongs to the user
    - Ensures the original AI transcription is NOT modified
    - Creates or updates a HumanReview record
    - Updates transcription status to 'reviewed'
    
    Args:
        transcription_id: ID of the transcription being reviewed
        user_id: ID of the user submitting the review
        corrected_text: Human-corrected transcription text
        review_notes: Optional review notes or comments
        
    Returns:
        ReviewResponse with the saved review details
        
    Raises:
        HTTPException: If transcription not found or doesn't belong to user
    """
    db = SessionLocal()
    try:
        # Verify transcription exists and belongs to user
        transcription = db.query(Transcription).filter(
            Transcription.id == transcription_id,
            Transcription.user_id == user_id
        ).first()
        
        if not transcription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcription not found or access denied"
            )
        
        # Store original AI transcription for verification (never modify it)
        original_ai_text = transcription.ai_transcription
        
        # Check if review already exists
        existing_review = db.query(HumanReview).filter(
            HumanReview.transcription_id == transcription_id,
            HumanReview.user_id == user_id
        ).first()
        
        if existing_review:
            # Update existing review
            existing_review.corrected_text = corrected_text
            existing_review.review_notes = review_notes
            existing_review.status = ReviewStatus.REVIEWED
            db.commit()
            db.refresh(existing_review)
            review = existing_review
        else:
            # Create new review
            review = HumanReview(
                transcription_id=transcription_id,
                user_id=user_id,
                corrected_text=corrected_text,
                review_notes=review_notes,
                status=ReviewStatus.REVIEWED
            )
            db.add(review)
            db.commit()
            db.refresh(review)
        
        # Verify original AI transcription was not modified
        if transcription.ai_transcription != original_ai_text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Data integrity error: Original AI transcription was modified"
            )
        
        # Update transcription status to reviewed
        transcription.status = TranscriptionStatus.COMPLETED
        db.commit()
        
        return ReviewResponse(
            id=review.id,
            transcription_id=review.transcription_id,
            user_id=review.user_id,
            corrected_text=review.corrected_text,
            review_notes=review.review_notes,
            status=review.status,
            created_at=review.created_at,
            updated_at=review.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit review: {str(e)}"
        )
    finally:
        db.close()


def get_review_by_transcription(transcription_id: int, user_id: int) -> Optional[ReviewResponse]:
    """Retrieve existing human review for a transcription.
    
    Args:
        transcription_id: ID of the transcription
        user_id: ID of the user requesting the review
        
    Returns:
        ReviewResponse if review exists, None otherwise
        
    Raises:
        HTTPException: If transcription not found or doesn't belong to user
    """
    db = SessionLocal()
    try:
        # Verify transcription exists and belongs to user
        transcription = db.query(Transcription).filter(
            Transcription.id == transcription_id,
            Transcription.user_id == user_id
        ).first()
        
        if not transcription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transcription not found or access denied"
            )
        
        # Get review
        review = db.query(HumanReview).filter(
            HumanReview.transcription_id == transcription_id,
            HumanReview.user_id == user_id
        ).first()
        
        if not review:
            return None
        
        return ReviewResponse(
            id=review.id,
            transcription_id=review.transcription_id,
            user_id=review.user_id,
            corrected_text=review.corrected_text,
            review_notes=review.review_notes,
            status=review.status,
            created_at=review.created_at,
            updated_at=review.updated_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve review: {str(e)}"
        )
    finally:
        db.close()
