from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.deps import get_db, get_current_user
from app.db import models, schemas
from app.db.crud import like as crud_like, match as crud_match

router = APIRouter(tags=["likes"])


@router.post("/likes", response_model=schemas.LikeResponse)
def create_like(
    like_data: schemas.LikeRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a like and check for mutual matching"""
    try:
        from_user_id = str(current_user.id)
        to_user_id = str(like_data.toUserId)

        # Validate that user is not liking themselves
        if from_user_id == to_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot like yourself"
            )

        # Check if target user exists
        target_user = db.query(models.User).filter(models.User.id == to_user_id).first()
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found"
            )

        if target_user.banned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot like banned user"
            )

        # Check if like already exists
        existing_like = crud_like.get_like(db, from_user_id, to_user_id, like_data.batchWeek)
        if existing_like:
            return schemas.LikeResponse(ok=True)  # Already liked

        # Create the like
        try:
            crud_like.create_like(db, from_user_id, to_user_id, like_data.batchWeek)
        except IntegrityError:
            db.rollback()
            # Like already exists (race condition)
            return schemas.LikeResponse(ok=True)

        # Check for mutual like
        if crud_like.check_mutual_like(db, from_user_id, to_user_id, like_data.batchWeek):
            # Check if match already exists
            existing_match = crud_match.get_match_by_users(db, from_user_id, to_user_id)
            if not existing_match:
                # Create new match with pending status
                crud_match.create_match(db, from_user_id, to_user_id, "pending")

        return schemas.LikeResponse(ok=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create like: {str(e)}"
        )