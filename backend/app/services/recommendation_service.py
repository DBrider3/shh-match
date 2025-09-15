from typing import Dict, Any
import structlog
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db import models
from app.db.crud import recommendation as crud_recommendation, user as crud_user

logger = structlog.get_logger()


def build_weekly_recommendations(week_label: str) -> Dict[str, Any]:
    """Build weekly recommendations for all users"""
    db = SessionLocal()
    result = {
        "week": week_label,
        "users_processed": 0,
        "recommendations_created": 0,
        "errors": []
    }

    try:
        # Get all active users with profiles and preferences
        users = (
            db.query(models.User)
            .join(models.Profile, models.User.id == models.Profile.user_id)
            .join(models.Preferences, models.User.id == models.Preferences.user_id)
            .filter(
                models.User.banned == False,
                models.User.role != 'admin'
            )
            .all()
        )

        logger.info(f"Building recommendations for {len(users)} users", week=week_label)

        for user in users:
            try:
                user_recommendations = build_recommendations_for_user(db, user, week_label)
                result["users_processed"] += 1
                result["recommendations_created"] += user_recommendations

            except Exception as e:
                logger.error(f"Failed to build recommendations for user {user.id}: {str(e)}")
                result["errors"].append({
                    "user_id": str(user.id),
                    "error": str(e)
                })

        logger.info(
            f"Completed recommendation generation",
            week=week_label,
            users_processed=result["users_processed"],
            recommendations_created=result["recommendations_created"],
            errors_count=len(result["errors"])
        )

    except Exception as e:
        logger.error(f"Failed to build weekly recommendations: {str(e)}")
        result["errors"].append({"general_error": str(e)})

    finally:
        db.close()

    return result


def build_recommendations_for_user(db: Session, user, week_label: str, max_recommendations: int = 10) -> int:
    """Build recommendations for a single user"""
    user_id = str(user.id)

    # Get recently exposed users (to avoid showing same users repeatedly)
    recent_exposures = crud_recommendation.get_recent_exposures(db, user_id, weeks=12)

    # Get potential matches based on preferences
    candidates = crud_recommendation.get_potential_matches(db, user_id)

    # Filter out recently exposed candidates
    filtered_candidates = [
        candidate for candidate in candidates
        if str(candidate.id) not in recent_exposures
    ]

    if not filtered_candidates:
        logger.info(f"No new candidates for user {user_id}", week=week_label)
        return 0

    # Score candidates
    scored_candidates = []
    for candidate in filtered_candidates:
        score = crud_recommendation.calculate_match_score(user, candidate)
        scored_candidates.append((candidate, score))

    # Sort by score and take top candidates
    scored_candidates.sort(key=lambda x: x[1], reverse=True)
    top_candidates = scored_candidates[:max_recommendations]

    # Create recommendations
    recommendations_created = 0
    for candidate, score in top_candidates:
        try:
            # Check if recommendation already exists
            existing = (
                db.query(models.Recommendation)
                .filter(
                    models.Recommendation.user_id == user_id,
                    models.Recommendation.target_user_id == str(candidate.id),
                    models.Recommendation.batch_week == week_label
                )
                .first()
            )

            if not existing:
                crud_recommendation.create_recommendation(
                    db, user_id, str(candidate.id), week_label, float(score)
                )
                crud_recommendation.log_exposure(
                    db, user_id, str(candidate.id), "weekly_rec"
                )
                recommendations_created += 1

        except Exception as e:
            logger.error(
                f"Failed to create recommendation for user {user_id} -> {candidate.id}: {str(e)}"
            )

    logger.info(
        f"Created {recommendations_created} recommendations for user {user_id}",
        week=week_label
    )

    return recommendations_created