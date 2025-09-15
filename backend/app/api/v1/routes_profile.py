from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.db import models, schemas
from app.db.crud import user as crud_user

router = APIRouter(tags=["profile"])


@router.put("/profile", response_model=schemas.Profile)
def update_profile(
    profile_data: schemas.ProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        # Validate gender
        if profile_data.gender not in ['M', 'F']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gender must be 'M' or 'F'"
            )

        # Validate birth year
        current_year = 2024
        if profile_data.birth_year < 1950 or profile_data.birth_year > current_year - 18:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid birth year"
            )

        # Update profile
        profile = crud_user.update_profile(db, str(current_user.id), profile_data)

        return schemas.Profile(
            user_id=profile.user_id,
            nickname=profile.nickname,
            gender=profile.gender,
            birth_year=profile.birth_year,
            height=profile.height,
            region=profile.region,
            job=profile.job,
            intro=profile.intro,
            photos=profile.photos,
            visible=profile.visible
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update profile: {str(e)}"
        )


@router.put("/preferences", response_model=schemas.Preferences)
def update_preferences(
    preferences_data: schemas.PreferencesUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences"""
    try:
        # Validate target gender
        if preferences_data.target_gender not in ['M', 'F']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Target gender must be 'M' or 'F'"
            )

        # Validate age range
        if preferences_data.age_min < 18 or preferences_data.age_max > 80:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Age range must be between 18 and 80"
            )

        if preferences_data.age_min > preferences_data.age_max:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Minimum age cannot be greater than maximum age"
            )

        # Update preferences
        preferences = crud_user.update_preferences(db, str(current_user.id), preferences_data)

        return schemas.Preferences(
            user_id=preferences.user_id,
            target_gender=preferences.target_gender,
            age_min=preferences.age_min,
            age_max=preferences.age_max,
            regions=preferences.regions,
            keywords=preferences.keywords,
            blocks=preferences.blocks
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )