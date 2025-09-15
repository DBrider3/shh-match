#!/usr/bin/env python3
"""Create an admin user"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import SessionLocal
from app.db import models


def create_admin_user(kakao_user_id: str, nickname: str = "Admin"):
    """Create an admin user"""
    db = SessionLocal()

    try:
        # Check if admin already exists
        existing_admin = db.query(models.User).filter(
            models.User.kakao_user_id == kakao_user_id
        ).first()

        if existing_admin:
            print(f"Admin user with Kakao ID {kakao_user_id} already exists")
            return

        # Create admin user
        admin_user = models.User(
            kakao_user_id=kakao_user_id,
            role="admin"
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)

        # Create admin profile
        admin_profile = models.Profile(
            user_id=admin_user.id,
            nickname=nickname,
            gender="M",  # Default
            birth_year=1990,  # Default
            photos=[],
            visible={"age": False, "height": False, "region": False, "job": False, "intro": False}
        )
        db.add(admin_profile)

        # Create admin preferences (not really used but required by schema)
        admin_preferences = models.Preferences(
            user_id=admin_user.id,
            target_gender="F",
            age_min=18,
            age_max=80
        )
        db.add(admin_preferences)

        db.commit()

        print(f"Admin user created successfully!")
        print(f"User ID: {admin_user.id}")
        print(f"Kakao User ID: {kakao_user_id}")
        print(f"Role: {admin_user.role}")

    except Exception as e:
        db.rollback()
        print(f"Failed to create admin user: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python create_admin.py <kakao_user_id> [nickname]")
        sys.exit(1)

    kakao_user_id = sys.argv[1]
    nickname = sys.argv[2] if len(sys.argv) > 2 else "Admin"

    create_admin_user(kakao_user_id, nickname)