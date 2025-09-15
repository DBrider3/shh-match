from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
import uuid

from app.db import models, schemas


def get_user_by_id(db: Session, user_id: str) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_kakao_id(db: Session, kakao_user_id: str) -> Optional[models.User]:
    """Get user by Kakao user ID"""
    return db.query(models.User).filter(models.User.kakao_user_id == kakao_user_id).first()


def create_user(db: Session, kakao_user_id: str) -> models.User:
    """Create a new user"""
    user = models.User(kakao_user_id=kakao_user_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_with_profile_and_preferences(db: Session, user_id: str) -> Optional[models.User]:
    """Get user with profile and preferences"""
    return (
        db.query(models.User)
        .options(joinedload(models.User.profile), joinedload(models.User.preferences))
        .filter(models.User.id == user_id)
        .first()
    )


def create_default_profile(db: Session, user_id: str, nickname: str = "사용자") -> models.Profile:
    """Create default profile for user"""
    profile = models.Profile(
        user_id=user_id,
        nickname=nickname,
        gender='M',  # Default, should be updated by user
        birth_year=1990,  # Default, should be updated by user
        photos=[],
        visible={"age": True, "height": False, "region": True, "job": True, "intro": True}
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def create_default_preferences(db: Session, user_id: str) -> models.Preferences:
    """Create default preferences for user"""
    preferences = models.Preferences(
        user_id=user_id,
        target_gender='F',  # Default, should be updated by user
        age_min=20,
        age_max=40
    )
    db.add(preferences)
    db.commit()
    db.refresh(preferences)
    return preferences


def update_profile(db: Session, user_id: str, profile_data: schemas.ProfileUpdate) -> models.Profile:
    """Update user profile"""
    profile = db.query(models.Profile).filter(models.Profile.user_id == user_id).first()
    if not profile:
        # Create new profile if doesn't exist
        profile = models.Profile(user_id=user_id)
        db.add(profile)

    for field, value in profile_data.dict(exclude_unset=True).items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


def update_preferences(db: Session, user_id: str, preferences_data: schemas.PreferencesUpdate) -> models.Preferences:
    """Update user preferences"""
    preferences = db.query(models.Preferences).filter(models.Preferences.user_id == user_id).first()
    if not preferences:
        # Create new preferences if doesn't exist
        preferences = models.Preferences(user_id=user_id)
        db.add(preferences)

    for field, value in preferences_data.dict(exclude_unset=True).items():
        setattr(preferences, field, value)

    db.commit()
    db.refresh(preferences)
    return preferences


def get_users_for_admin(db: Session, query: str = "", page: int = 0, limit: int = 50) -> List[models.User]:
    """Get users for admin with optional search"""
    users_query = db.query(models.User).options(joinedload(models.User.profile))

    if query:
        users_query = users_query.join(models.Profile, models.User.id == models.Profile.user_id, isouter=True).filter(
            models.Profile.nickname.ilike(f"%{query}%")
        )

    return users_query.offset(page * limit).limit(limit).all()