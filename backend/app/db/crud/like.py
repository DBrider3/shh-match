from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
import uuid

from app.db import models


def create_like(
    db: Session,
    from_user_id: str,
    to_user_id: str,
    batch_week: str
) -> models.Like:
    """Create a new like"""
    like = models.Like(
        from_user=from_user_id,
        to_user=to_user_id,
        batch_week=batch_week
    )
    db.add(like)
    db.commit()
    db.refresh(like)
    return like


def get_like(
    db: Session,
    from_user_id: str,
    to_user_id: str,
    batch_week: str
) -> Optional[models.Like]:
    """Get existing like"""
    return (
        db.query(models.Like)
        .filter(
            and_(
                models.Like.from_user == from_user_id,
                models.Like.to_user == to_user_id,
                models.Like.batch_week == batch_week
            )
        )
        .first()
    )


def check_mutual_like(
    db: Session,
    user_a_id: str,
    user_b_id: str,
    batch_week: str
) -> bool:
    """Check if two users have mutual likes"""
    like_a_to_b = get_like(db, user_a_id, user_b_id, batch_week)
    like_b_to_a = get_like(db, user_b_id, user_a_id, batch_week)
    return like_a_to_b is not None and like_b_to_a is not None


def get_user_likes_sent(db: Session, user_id: str) -> List[models.Like]:
    """Get likes sent by a user"""
    return (
        db.query(models.Like)
        .filter(models.Like.from_user == user_id)
        .order_by(models.Like.created_at.desc())
        .all()
    )


def get_user_likes_received(db: Session, user_id: str) -> List[models.Like]:
    """Get likes received by a user"""
    return (
        db.query(models.Like)
        .filter(models.Like.to_user == user_id)
        .order_by(models.Like.created_at.desc())
        .all()
    )