from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
import uuid

from app.db import models


def create_match(
    db: Session,
    user_a_id: str,
    user_b_id: str,
    status: str = "pending"
) -> models.Match:
    """Create a new match"""
    # Ensure consistent ordering (smaller UUID first)
    if str(user_a_id) > str(user_b_id):
        user_a_id, user_b_id = user_b_id, user_a_id

    match = models.Match(
        user_a=user_a_id,
        user_b=user_b_id,
        status=status
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def get_match_by_users(
    db: Session,
    user_a_id: str,
    user_b_id: str
) -> Optional[models.Match]:
    """Get match between two users"""
    return (
        db.query(models.Match)
        .filter(
            or_(
                and_(models.Match.user_a == user_a_id, models.Match.user_b == user_b_id),
                and_(models.Match.user_a == user_b_id, models.Match.user_b == user_a_id)
            )
        )
        .first()
    )


def get_match_by_id(db: Session, match_id: str) -> Optional[models.Match]:
    """Get match by ID"""
    return (
        db.query(models.Match)
        .options(
            joinedload(models.Match.user_a_rel).joinedload(models.User.profile),
            joinedload(models.Match.user_b_rel).joinedload(models.User.profile),
            joinedload(models.Match.payment)
        )
        .filter(models.Match.id == match_id)
        .first()
    )


def get_user_matches(db: Session, user_id: str) -> List[models.Match]:
    """Get all matches for a user"""
    return (
        db.query(models.Match)
        .options(
            joinedload(models.Match.user_a_rel).joinedload(models.User.profile),
            joinedload(models.Match.user_b_rel).joinedload(models.User.profile),
            joinedload(models.Match.payment)
        )
        .filter(
            or_(
                models.Match.user_a == user_id,
                models.Match.user_b == user_id
            )
        )
        .order_by(models.Match.created_at.desc())
        .all()
    )


def update_match_status(
    db: Session,
    match_id: str,
    status: str
) -> Optional[models.Match]:
    """Update match status"""
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if match:
        match.status = status
        db.commit()
        db.refresh(match)
    return match


def get_matches_for_admin(
    db: Session,
    status: Optional[str] = None,
    page: int = 0,
    limit: int = 50
) -> List[models.Match]:
    """Get matches for admin with optional status filter"""
    query = (
        db.query(models.Match)
        .options(
            joinedload(models.Match.user_a_rel).joinedload(models.User.profile),
            joinedload(models.Match.user_b_rel).joinedload(models.User.profile),
            joinedload(models.Match.payment)
        )
    )

    if status:
        query = query.filter(models.Match.status == status)

    return query.order_by(models.Match.created_at.desc()).offset(page * limit).limit(limit).all()


def user_can_access_match(match: models.Match, user_id: str) -> bool:
    """Check if user can access match details"""
    return str(match.user_a) == str(user_id) or str(match.user_b) == str(user_id)


def get_other_user(match: models.Match, user_id: str) -> Optional[models.User]:
    """Get the other user in a match"""
    if str(match.user_a) == str(user_id):
        return match.user_b_rel
    elif str(match.user_b) == str(user_id):
        return match.user_a_rel
    return None