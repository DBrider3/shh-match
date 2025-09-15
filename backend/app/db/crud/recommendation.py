from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, func
from datetime import datetime, timedelta
import uuid

from app.db import models


def get_recommendations(db: Session, user_id: str, week: str) -> List[models.Recommendation]:
    """Get recommendations for a user for a specific week"""
    return (
        db.query(models.Recommendation)
        .options(joinedload(models.Recommendation.target_user).joinedload(models.User.profile))
        .filter(
            and_(
                models.Recommendation.user_id == user_id,
                models.Recommendation.batch_week == week
            )
        )
        .order_by(models.Recommendation.score.desc())
        .all()
    )


def create_recommendation(
    db: Session,
    user_id: str,
    target_user_id: str,
    batch_week: str,
    score: float
) -> models.Recommendation:
    """Create a new recommendation"""
    recommendation = models.Recommendation(
        user_id=user_id,
        target_user_id=target_user_id,
        batch_week=batch_week,
        score=score,
        sent_at=datetime.utcnow()
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return recommendation


def log_exposure(
    db: Session,
    user_id: str,
    target_user_id: str,
    reason: str = "weekly_rec"
) -> models.ExposureLog:
    """Log user exposure to prevent duplicate recommendations"""
    exposure = models.ExposureLog(
        user_id=user_id,
        target_user_id=target_user_id,
        reason=reason
    )
    db.add(exposure)
    db.commit()
    db.refresh(exposure)
    return exposure


def get_recent_exposures(db: Session, user_id: str, weeks: int = 12) -> List[str]:
    """Get user IDs that were recently exposed to a user"""
    cutoff_date = datetime.utcnow() - timedelta(weeks=weeks)
    exposures = (
        db.query(models.ExposureLog.target_user_id)
        .filter(
            and_(
                models.ExposureLog.user_id == user_id,
                models.ExposureLog.seen_at >= cutoff_date
            )
        )
        .all()
    )
    return [str(exp.target_user_id) for exp in exposures]


def get_potential_matches(db: Session, user_id: str) -> List[models.User]:
    """Get potential matches for a user based on preferences"""
    user = db.query(models.User).options(
        joinedload(models.User.profile),
        joinedload(models.User.preferences)
    ).filter(models.User.id == user_id).first()

    if not user or not user.profile or not user.preferences:
        return []

    # Get user's preferences
    prefs = user.preferences
    profile = user.profile

    # Calculate current year for age filtering
    current_year = datetime.now().year

    # Base query for potential matches
    query = (
        db.query(models.User)
        .join(models.Profile, models.User.id == models.Profile.user_id)
        .join(models.Preferences, models.User.id == models.Preferences.user_id)
        .filter(
            # Not the same user
            models.User.id != user_id,
            # Not banned
            models.User.banned == False,
            # Gender match
            models.Profile.gender == prefs.target_gender,
            # Mutual age preference
            models.Profile.birth_year >= current_year - prefs.age_max,
            models.Profile.birth_year <= current_year - prefs.age_min,
            models.Preferences.age_min <= current_year - profile.birth_year,
            models.Preferences.age_max >= current_year - profile.birth_year,
            # Mutual gender preference
            models.Preferences.target_gender == profile.gender,
        )
    )

    # Region filter if specified
    if prefs.regions:
        query = query.filter(models.Profile.region.in_(prefs.regions))

    # Exclude blocked users
    if prefs.blocks:
        query = query.filter(~models.User.id.in_(prefs.blocks))

    return query.all()


def calculate_match_score(user: models.User, candidate: models.User) -> float:
    """Calculate compatibility score between two users"""
    score = 0.0

    if not user.profile or not candidate.profile:
        return score

    # Age compatibility (closer age = higher score)
    age_diff = abs(user.profile.birth_year - candidate.profile.birth_year)
    if age_diff <= 2:
        score += 3.0
    elif age_diff <= 5:
        score += 2.0
    elif age_diff <= 10:
        score += 1.0

    # Region match
    if user.profile.region and candidate.profile.region:
        if user.profile.region == candidate.profile.region:
            score += 2.0

    # Profile completeness bonus
    if candidate.profile.intro and len(candidate.profile.intro) > 20:
        score += 1.0
    if candidate.profile.photos and len(candidate.profile.photos) >= 2:
        score += 1.0

    # Base score for valid match
    score += 1.0

    return score