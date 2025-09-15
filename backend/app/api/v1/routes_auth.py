from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_db, get_current_user
from app.core.security import create_jwt
from app.db import models, schemas
from app.db.crud import user as crud_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/sync-kakao", response_model=schemas.AuthResponse)
def sync_kakao(body: schemas.SyncKakaoRequest, db: Session = Depends(get_db)):
    """Sync Kakao user and return JWT token"""
    try:
        # Check if user exists
        user = crud_user.get_user_by_kakao_id(db, body.kakaoUserId)

        if not user:
            # Create new user
            user = crud_user.create_user(db, body.kakaoUserId)

            # Create default profile and preferences
            nickname = body.nickname or "사용자"
            crud_user.create_default_profile(db, str(user.id), nickname)
            crud_user.create_default_preferences(db, str(user.id))

        # Generate JWT token
        token = create_jwt(str(user.id), user.role)

        return schemas.AuthResponse(
            jwt=token,
            user=schemas.User(
                id=user.id,
                kakao_user_id=user.kakao_user_id,
                phone_verified=user.phone_verified,
                role=user.role,
                banned=user.banned,
                created_at=user.created_at
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync Kakao user: {str(e)}"
        )


@router.get("/me", response_model=schemas.MeResponse)
def get_me(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user with profile and preferences"""
    user_data = crud_user.get_user_with_profile_and_preferences(db, str(current_user.id))

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    profile_data = None
    if user_data.profile:
        profile_data = schemas.Profile(
            user_id=user_data.profile.user_id,
            nickname=user_data.profile.nickname,
            gender=user_data.profile.gender,
            birth_year=user_data.profile.birth_year,
            height=user_data.profile.height,
            region=user_data.profile.region,
            job=user_data.profile.job,
            intro=user_data.profile.intro,
            photos=user_data.profile.photos,
            visible=user_data.profile.visible
        )

    preferences_data = None
    if user_data.preferences:
        preferences_data = schemas.Preferences(
            user_id=user_data.preferences.user_id,
            target_gender=user_data.preferences.target_gender,
            age_min=user_data.preferences.age_min,
            age_max=user_data.preferences.age_max,
            regions=user_data.preferences.regions,
            keywords=user_data.preferences.keywords,
            blocks=user_data.preferences.blocks
        )

    return schemas.MeResponse(
        user=schemas.User(
            id=user_data.id,
            kakao_user_id=user_data.kakao_user_id,
            phone_verified=user_data.phone_verified,
            role=user_data.role,
            banned=user_data.banned,
            created_at=user_data.created_at
        ),
        profile=profile_data,
        preferences=preferences_data
    )