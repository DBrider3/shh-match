from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.db import models, schemas
from app.db.crud import match as crud_match

router = APIRouter(tags=["matches"])


@router.get("/matches", response_model=List[schemas.Match])
def get_matches(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all matches for current user"""
    try:
        matches = crud_match.get_user_matches(db, str(current_user.id))

        result = []
        for match in matches:
            result.append(schemas.Match(
                id=match.id,
                user_a=match.user_a,
                user_b=match.user_b,
                created_at=match.created_at,
                status=match.status
            ))

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get matches: {str(e)}"
        )


@router.get("/matches/{match_id}", response_model=schemas.MatchDetail)
def get_match_detail(
    match_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed match information"""
    try:
        match = crud_match.get_match_by_id(db, match_id)

        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )

        # Check if current user can access this match
        if not crud_match.user_can_access_match(match, str(current_user.id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        # Get the other user's profile
        other_user = crud_match.get_other_user(match, str(current_user.id))
        if not other_user or not other_user.profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Other user profile not found"
            )

        # Apply visibility settings to other user's profile
        other_profile = other_user.profile
        visible_profile = schemas.Profile(
            user_id=other_profile.user_id,
            nickname=other_profile.nickname,
            gender=other_profile.gender,
            birth_year=other_profile.birth_year if other_profile.visible.get('age', True) else None,
            height=other_profile.height if other_profile.visible.get('height', True) else None,
            region=other_profile.region if other_profile.visible.get('region', True) else None,
            job=other_profile.job if other_profile.visible.get('job', True) else None,
            intro=other_profile.intro if other_profile.visible.get('intro', True) else None,
            photos=other_profile.photos,  # Photos are visible in active matches
            visible=other_profile.visible
        )

        match_schema = schemas.Match(
            id=match.id,
            user_a=match.user_a,
            user_b=match.user_b,
            created_at=match.created_at,
            status=match.status
        )

        return schemas.MatchDetail(
            match=match_schema,
            other_profile=visible_profile
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get match detail: {str(e)}"
        )