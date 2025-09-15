from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.deps import get_db, admin_only
from app.db import models, schemas
from app.db.crud import (
    user as crud_user,
    payment as crud_payment,
    match as crud_match,
    recommendation as crud_recommendation
)
from app.services.recommendation_service import build_weekly_recommendations

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[schemas.AdminUser])
def get_users(
    query: str = Query("", description="Search query for user nickname"),
    page: int = Query(0, ge=0, description="Page number"),
    admin_user: models.User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """Get users for admin panel"""
    try:
        users = crud_user.get_users_for_admin(db, query, page)

        result = []
        for user in users:
            profile_data = None
            if user.profile:
                profile_data = schemas.Profile(
                    user_id=user.profile.user_id,
                    nickname=user.profile.nickname,
                    gender=user.profile.gender,
                    birth_year=user.profile.birth_year,
                    height=user.profile.height,
                    region=user.profile.region,
                    job=user.profile.job,
                    intro=user.profile.intro,
                    photos=user.profile.photos,
                    visible=user.profile.visible
                )

            result.append(schemas.AdminUser(
                id=user.id,
                kakao_user_id=user.kakao_user_id,
                phone_verified=user.phone_verified,
                role=user.role,
                banned=user.banned,
                created_at=user.created_at,
                profile=profile_data
            ))

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get users: {str(e)}"
        )


@router.get("/matches", response_model=List[schemas.AdminMatch])
def get_matches(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by match status"),
    page: int = Query(0, ge=0, description="Page number"),
    admin_user: models.User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """Get matches for admin panel"""
    try:
        matches = crud_match.get_matches_for_admin(db, status_filter, page)

        result = []
        for match in matches:
            user_a_profile = None
            if match.user_a_rel and match.user_a_rel.profile:
                user_a_profile = schemas.Profile(
                    user_id=match.user_a_rel.profile.user_id,
                    nickname=match.user_a_rel.profile.nickname,
                    gender=match.user_a_rel.profile.gender,
                    birth_year=match.user_a_rel.profile.birth_year,
                    height=match.user_a_rel.profile.height,
                    region=match.user_a_rel.profile.region,
                    job=match.user_a_rel.profile.job,
                    intro=match.user_a_rel.profile.intro,
                    photos=match.user_a_rel.profile.photos,
                    visible=match.user_a_rel.profile.visible
                )

            user_b_profile = None
            if match.user_b_rel and match.user_b_rel.profile:
                user_b_profile = schemas.Profile(
                    user_id=match.user_b_rel.profile.user_id,
                    nickname=match.user_b_rel.profile.nickname,
                    gender=match.user_b_rel.profile.gender,
                    birth_year=match.user_b_rel.profile.birth_year,
                    height=match.user_b_rel.profile.height,
                    region=match.user_b_rel.profile.region,
                    job=match.user_b_rel.profile.job,
                    intro=match.user_b_rel.profile.intro,
                    photos=match.user_b_rel.profile.photos,
                    visible=match.user_b_rel.profile.visible
                )

            payment_data = None
            if match.payment:
                payment_data = schemas.Payment(
                    id=match.payment.id,
                    match_id=match.payment.match_id,
                    method=match.payment.method,
                    amount=match.payment.amount,
                    code=match.payment.code,
                    depositor_name=match.payment.depositor_name,
                    verified_at=match.payment.verified_at,
                    memo=match.payment.memo
                )

            result.append(schemas.AdminMatch(
                id=match.id,
                user_a=match.user_a,
                user_b=match.user_b,
                created_at=match.created_at,
                status=match.status,
                user_a_profile=user_a_profile,
                user_b_profile=user_b_profile,
                payment=payment_data
            ))

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get matches: {str(e)}"
        )


@router.get("/payments", response_model=List[schemas.AdminPayment])
def get_payments(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by payment status (verified/pending)"),
    page: int = Query(0, ge=0, description="Page number"),
    admin_user: models.User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """Get payments for admin panel"""
    try:
        payments = crud_payment.get_payments_for_admin(db, status_filter, page)

        result = []
        for payment in payments:
            match_data = schemas.Match(
                id=payment.match.id,
                user_a=payment.match.user_a,
                user_b=payment.match.user_b,
                created_at=payment.match.created_at,
                status=payment.match.status
            )

            result.append(schemas.AdminPayment(
                id=payment.id,
                match_id=payment.match_id,
                method=payment.method,
                amount=payment.amount,
                code=payment.code,
                depositor_name=payment.depositor_name,
                verified_at=payment.verified_at,
                memo=payment.memo,
                match=match_data
            ))

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get payments: {str(e)}"
        )


@router.post("/payments/{payment_id}/verify", response_model=schemas.VerifyPaymentResponse)
def verify_payment(
    payment_id: str,
    admin_user: models.User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """Verify a payment"""
    try:
        payment = crud_payment.verify_payment(db, payment_id)

        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )

        # Log admin action
        admin_action = models.AdminAction(
            admin_id=admin_user.id,
            action="verify_payment",
            target_id=payment_id,
            detail={"payment_id": payment_id, "amount": payment.amount}
        )
        db.add(admin_action)
        db.commit()

        return schemas.VerifyPaymentResponse(ok=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify payment: {str(e)}"
        )


@router.post("/matches/{match_id}/activate", response_model=schemas.ActivateMatchResponse)
def activate_match(
    match_id: str,
    admin_user: models.User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """Activate a match"""
    try:
        match = crud_match.update_match_status(db, match_id, "active")

        if not match:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match not found"
            )

        # Log admin action
        admin_action = models.AdminAction(
            admin_id=admin_user.id,
            action="activate_match",
            target_id=match_id,
            detail={"match_id": match_id, "status": "active"}
        )
        db.add(admin_action)
        db.commit()

        return schemas.ActivateMatchResponse(ok=True)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate match: {str(e)}"
        )


@router.post("/recs/run")
def run_recommendations(
    admin_user: models.User = Depends(admin_only),
    db: Session = Depends(get_db)
):
    """Manually trigger recommendation generation"""
    try:
        from datetime import datetime

        # Generate current week label
        now = datetime.now()
        year, week, _ = now.isocalendar()
        week_label = f"{year}-W{week:02d}"

        # Run recommendation generation
        result = build_weekly_recommendations(week_label)

        # Log admin action
        admin_action = models.AdminAction(
            admin_id=admin_user.id,
            action="run_recommendations",
            target_id=week_label,
            detail=result
        )
        db.add(admin_action)
        db.commit()

        return {"ok": True, "week": week_label, "result": result}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run recommendations: {str(e)}"
        )