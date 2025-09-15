from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.db import models, schemas
from app.db.crud import recommendation as crud_recommendation

router = APIRouter(tags=["recommendations"])


@router.get("/recommendations", response_model=List[schemas.RecommendationItem])
def get_recommendations(
    week: str = Query(..., description="Week in format YYYY-Www (e.g., 2024-W37)"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recommendations for current user for a specific week"""
    try:
        # Validate week format (basic validation)
        if not week or len(week) < 8 or 'W' not in week:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid week format. Use YYYY-Www format (e.g., 2024-W37)"
            )

        recommendations = crud_recommendation.get_recommendations(
            db, str(current_user.id), week
        )

        result = []
        for rec in recommendations:
            if rec.target_user and rec.target_user.profile:
                target_profile = rec.target_user.profile

                # Apply visibility settings
                visible_profile = schemas.Profile(
                    user_id=target_profile.user_id,
                    nickname=target_profile.nickname,
                    gender=target_profile.gender,
                    birth_year=target_profile.birth_year if target_profile.visible.get('age', True) else None,
                    height=target_profile.height if target_profile.visible.get('height', True) else None,
                    region=target_profile.region if target_profile.visible.get('region', True) else None,
                    job=target_profile.job if target_profile.visible.get('job', True) else None,
                    intro=target_profile.intro if target_profile.visible.get('intro', True) else None,
                    photos=target_profile.photos,  # Photos are always visible for recommendations
                    visible=target_profile.visible
                )

                result.append(schemas.RecommendationItem(
                    id=rec.id,
                    target_user_id=rec.target_user_id,
                    batch_week=rec.batch_week,
                    score=rec.score,
                    sent_at=rec.sent_at,
                    responded=rec.responded,
                    target_profile=visible_profile
                ))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get recommendations: {str(e)}"
        )