from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.services.review_service import submit_review, get_review_by_transcription
from app.api.dependencies import get_current_user

router = APIRouter()


@router.post("/transcriptions/{transcription_id}/review", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    transcription_id: int,
    request: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit a human review for a transcription."""
    try:
        # Verify transcription_id matches request
        if request.transcription_id != transcription_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transcription ID mismatch"
            )
        
        review = submit_review(
            transcription_id=transcription_id,
            user_id=current_user.id,
            corrected_text=request.corrected_text,
            review_notes=request.review_notes
        )
        return review
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create review: {str(e)}"
        )


@router.patch("/transcriptions/{transcription_id}/review", response_model=ReviewResponse)
async def update_review(
    transcription_id: int,
    request: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing human review for a transcription."""
    try:
        # For updates, we use submit_review which handles both create and update
        # We need to get the existing review first to preserve data
        existing_review = get_review_by_transcription(transcription_id, current_user.id)
        
        if not existing_review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found. Use POST to create a new review."
            )
        
        # Build corrected_text from existing if not provided
        corrected_text = request.corrected_text if request.corrected_text is not None else existing_review.corrected_text
        review_notes = request.review_notes if request.review_notes is not None else existing_review.review_notes
        
        review = submit_review(
            transcription_id=transcription_id,
            user_id=current_user.id,
            corrected_text=corrected_text,
            review_notes=review_notes
        )
        return review
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update review: {str(e)}"
        )


@router.get("/transcriptions/{transcription_id}/review", response_model=ReviewResponse)
async def get_review(
    transcription_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the human review for a specific transcription."""
    try:
        review = get_review_by_transcription(transcription_id, current_user.id)
        
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found for this transcription"
            )
        
        return review
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve review: {str(e)}"
        )
