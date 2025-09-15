from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.deps import get_db, get_current_user
from app.db import models, schemas
from app.db.crud import payment as crud_payment, match as crud_match

router = APIRouter(tags=["payments"])


@router.post("/payments/intent", response_model=schemas.Payment)
def create_payment_intent(
    payment_data: schemas.PaymentIntentRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create payment intent for a match"""
    try:
        match_id = str(payment_data.matchId)

        # Get match and verify access
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

        # Check if match is in pending status
        if match.status != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment can only be created for pending matches"
            )

        # Check if payment already exists
        existing_payment = crud_payment.get_payment_by_match_id(db, match_id)
        if existing_payment:
            return schemas.Payment(
                id=existing_payment.id,
                match_id=existing_payment.match_id,
                method=existing_payment.method,
                amount=existing_payment.amount,
                code=existing_payment.code,
                depositor_name=existing_payment.depositor_name,
                verified_at=existing_payment.verified_at,
                memo=existing_payment.memo
            )

        # Create new payment
        try:
            payment = crud_payment.create_payment(db, match_id)
        except IntegrityError:
            db.rollback()
            # Payment already exists (race condition)
            existing_payment = crud_payment.get_payment_by_match_id(db, match_id)
            if existing_payment:
                return schemas.Payment(
                    id=existing_payment.id,
                    match_id=existing_payment.match_id,
                    method=existing_payment.method,
                    amount=existing_payment.amount,
                    code=existing_payment.code,
                    depositor_name=existing_payment.depositor_name,
                    verified_at=existing_payment.verified_at,
                    memo=existing_payment.memo
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create payment"
                )

        return schemas.Payment(
            id=payment.id,
            match_id=payment.match_id,
            method=payment.method,
            amount=payment.amount,
            code=payment.code,
            depositor_name=payment.depositor_name,
            verified_at=payment.verified_at,
            memo=payment.memo
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment intent: {str(e)}"
        )


@router.get("/payments/{payment_id}", response_model=schemas.Payment)
def get_payment(
    payment_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get payment details"""
    try:
        payment = crud_payment.get_payment_by_id(db, payment_id)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        # Check if current user can access this payment
        if not crud_payment.user_can_access_payment(payment, str(current_user.id)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return schemas.Payment(
            id=payment.id,
            match_id=payment.match_id,
            method=payment.method,
            amount=payment.amount,
            code=payment.code,
            depositor_name=payment.depositor_name,
            verified_at=payment.verified_at,
            memo=payment.memo
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payment: {str(e)}"
        )