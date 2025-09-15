#!/usr/bin/env python3
"""Initialize the database with tables"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.db.session import engine
from app.db.base import Base
from app.db import models  # Import models to register them


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()