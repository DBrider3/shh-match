from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from datetime import datetime
import uuid
import random
import string

from app.db import models


def generate_payment_code(user_id: str) -> str:
    """Generate unique payment code"""
    user_suffix = str(user_id)[-4:]  # Last 4 characters of user ID
    random_part = ''.join(random.choices(string.digits, k=3))
    return f"KM-{user_suffix}-{random_part}"


def create_payment(
    db: Session,
    match_id: str,
    amount: int = 10000,  # Default amount in KRW
    method: str = "transfer"
) -> models.Payment:
    """Create a new payment"""
    # Get match to determine user for code generation
    match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not match:
        raise ValueError("Match not found")

    code = generate_payment_code(match.user_a)

    payment = models.Payment(
        match_id=match_id,
        method=method,
        amount=amount,
        code=code
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def get_payment_by_id(db: Session, payment_id: str) -> Optional[models.Payment]:
    """Get payment by ID"""
    return (
        db.query(models.Payment)
        .options(joinedload(models.Payment.match))
        .filter(models.Payment.id == payment_id)
        .first()
    )


def get_payment_by_match_id(db: Session, match_id: str) -> Optional[models.Payment]:
    """Get payment by match ID"""
    return (
        db.query(models.Payment)
        .filter(models.Payment.match_id == match_id)
        .first()
    )


def verify_payment(
    db: Session,
    payment_id: str,
    depositor_name: Optional[str] = None,
    memo: Optional[str] = None
) -> Optional[models.Payment]:
    """Verify payment (mark as verified)"""
    payment = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if payment:
        payment.verified_at = datetime.utcnow()
        if depositor_name:
            payment.depositor_name = depositor_name
        if memo:
            payment.memo = memo
        db.commit()
        db.refresh(payment)
    return payment


def get_payments_for_admin(
    db: Session,
    status: Optional[str] = None,
    page: int = 0,
    limit: int = 50
) -> List[models.Payment]:
    """Get payments for admin with optional status filter"""
    query = (
        db.query(models.Payment)
        .options(joinedload(models.Payment.match))
        .join(models.Match, models.Payment.match_id == models.Match.id)
    )

    if status == "verified":
        query = query.filter(models.Payment.verified_at.isnot(None))
    elif status == "pending":
        query = query.filter(models.Payment.verified_at.is_(None))

    return query.order_by(models.Payment.id.desc()).offset(page * limit).limit(limit).all()


def user_can_access_payment(payment: models.Payment, user_id: str) -> bool:
    """Check if user can access payment details"""
    if not payment.match:
        return False
    return (
        str(payment.match.user_a) == str(user_id) or
        str(payment.match.user_b) == str(user_id)
    )