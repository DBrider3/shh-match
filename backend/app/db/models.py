import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Integer, Text, JSON, ForeignKey,
    CheckConstraint, UniqueConstraint, TIMESTAMP, DECIMAL, BIGINT
)
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kakao_user_id = Column(Text, unique=True, nullable=False)
    phone_verified = Column(Boolean, default=False)
    role = Column(String, default='user')
    banned = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    profile = relationship('Profile', uselist=False, back_populates='user', cascade='all, delete-orphan')
    preferences = relationship('Preferences', uselist=False, back_populates='user', cascade='all, delete-orphan')
    sent_likes = relationship('Like', foreign_keys='Like.from_user', back_populates='sender', cascade='all, delete-orphan')
    received_likes = relationship('Like', foreign_keys='Like.to_user', back_populates='receiver', cascade='all, delete-orphan')
    recommendations = relationship('Recommendation', back_populates='user', cascade='all, delete-orphan')
    exposure_logs = relationship('ExposureLog', foreign_keys='ExposureLog.user_id', cascade='all, delete-orphan')


class Profile(Base):
    __tablename__ = 'profiles'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    nickname = Column(String, nullable=False)
    gender = Column(String(1), nullable=False)
    birth_year = Column(Integer, nullable=False)
    height = Column(Integer)
    region = Column(String)
    job = Column(String)
    intro = Column(Text)
    photos = Column(JSON, nullable=False, default=list)
    visible = Column(JSON, nullable=False, default=lambda: {"age": True, "height": False, "region": True, "job": True, "intro": True})

    __table_args__ = (
        CheckConstraint(gender.in_(['M', 'F']), name='check_gender'),
    )

    # Relationships
    user = relationship('User', back_populates='profile')


class Preferences(Base):
    __tablename__ = 'preferences'

    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), primary_key=True)
    target_gender = Column(String(1), nullable=False)
    age_min = Column(Integer, nullable=False)
    age_max = Column(Integer, nullable=False)
    regions = Column(ARRAY(String), default=list)
    keywords = Column(ARRAY(String), default=list)
    blocks = Column(ARRAY(UUID(as_uuid=True)), default=list)

    __table_args__ = (
        CheckConstraint(target_gender.in_(['M', 'F']), name='check_target_gender'),
    )

    # Relationships
    user = relationship('User', back_populates='preferences')


class ExposureLog(Base):
    __tablename__ = 'exposure_log'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    reason = Column(Text)
    seen_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Note: Weekly uniqueness will be handled at application level
    # UniqueConstraint with date functions are complex in PostgreSQL

    # Relationships
    user = relationship('User', foreign_keys=[user_id])
    target_user = relationship('User', foreign_keys=[target_user_id])


class Recommendation(Base):
    __tablename__ = 'recommendations'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    target_user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    batch_week = Column(String, nullable=False)
    score = Column(DECIMAL(6, 3), default=0)
    sent_at = Column(TIMESTAMP(timezone=True))
    responded = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'target_user_id', 'batch_week', name='unique_recommendation_per_week'),
    )

    # Relationships
    user = relationship('User', back_populates='recommendations')
    target_user = relationship('User', foreign_keys=[target_user_id])


class Like(Base):
    __tablename__ = 'likes'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    from_user = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    to_user = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    batch_week = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint('from_user', 'to_user', 'batch_week', name='unique_like_per_week'),
    )

    # Relationships
    sender = relationship('User', foreign_keys=[from_user], back_populates='sent_likes')
    receiver = relationship('User', foreign_keys=[to_user], back_populates='received_likes')


class Match(Base):
    __tablename__ = 'matches'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_a = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    user_b = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    status = Column(String, nullable=False, default='pending')

    __table_args__ = (
        CheckConstraint(status.in_(['pending', 'active', 'closed']), name='check_status'),
        # Note: User pair uniqueness will be handled at application level
    )

    # Relationships
    user_a_rel = relationship('User', foreign_keys=[user_a])
    user_b_rel = relationship('User', foreign_keys=[user_b])
    payment = relationship('Payment', uselist=False, back_populates='match', cascade='all, delete-orphan')


class Payment(Base):
    __tablename__ = 'payments'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    match_id = Column(UUID(as_uuid=True), ForeignKey('matches.id', ondelete='CASCADE'), unique=True, nullable=False)
    method = Column(String, nullable=False, default='transfer')
    amount = Column(Integer, nullable=False)
    code = Column(String, nullable=False)
    depositor_name = Column(String)
    verified_at = Column(TIMESTAMP(timezone=True))
    memo = Column(Text)

    __table_args__ = (
        CheckConstraint(method.in_(['transfer']), name='check_payment_method'),
    )

    # Relationships
    match = relationship('Match', back_populates='payment')


class AdminAction(Base):
    __tablename__ = 'admin_actions'

    id = Column(BIGINT, primary_key=True, autoincrement=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    action = Column(String, nullable=False)
    target_id = Column(String)
    detail = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    admin = relationship('User', foreign_keys=[admin_id])


class Report(Base):
    __tablename__ = 'reports'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    reporter = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    reported = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    reason = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    handled = Column(Boolean, default=False)

    # Relationships
    reporter_user = relationship('User', foreign_keys=[reporter])
    reported_user = relationship('User', foreign_keys=[reported])