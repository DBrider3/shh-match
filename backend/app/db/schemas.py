from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, UUID4
from decimal import Decimal


# User schemas
class UserBase(BaseModel):
    kakao_user_id: str
    phone_verified: bool = False
    role: str = "user"
    banned: bool = False


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: UUID4
    created_at: datetime

    model_config = {"from_attributes": True}


# Profile schemas
class ProfileBase(BaseModel):
    nickname: str
    gender: str
    birth_year: int
    height: Optional[int] = None
    region: Optional[str] = None
    job: Optional[str] = None
    intro: Optional[str] = None
    photos: List[str] = []
    visible: Dict[str, bool] = {"age": True, "height": False, "region": True, "job": True, "intro": True}


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class Profile(ProfileBase):
    user_id: UUID4

    model_config = {"from_attributes": True}


# Preferences schemas
class PreferencesBase(BaseModel):
    target_gender: str
    age_min: int
    age_max: int
    regions: List[str] = []
    keywords: List[str] = []
    blocks: List[UUID4] = []


class PreferencesCreate(PreferencesBase):
    pass


class PreferencesUpdate(PreferencesBase):
    pass


class Preferences(PreferencesBase):
    user_id: UUID4

    model_config = {"from_attributes": True}


# Auth schemas
class SyncKakaoRequest(BaseModel):
    kakaoUserId: str
    email: Optional[str] = None
    nickname: Optional[str] = None


class AuthResponse(BaseModel):
    jwt: str
    user: User


class MeResponse(BaseModel):
    user: User
    profile: Optional[Profile] = None
    preferences: Optional[Preferences] = None


# Recommendation schemas
class RecommendationItem(BaseModel):
    id: int
    target_user_id: UUID4
    batch_week: str
    score: Decimal
    sent_at: Optional[datetime] = None
    responded: bool
    target_profile: Profile

    model_config = {"from_attributes": True}


# Like schemas
class LikeRequest(BaseModel):
    toUserId: UUID4
    batchWeek: str


class LikeResponse(BaseModel):
    ok: bool


# Match schemas
class Match(BaseModel):
    id: UUID4
    user_a: UUID4
    user_b: UUID4
    created_at: datetime
    status: str

    model_config = {"from_attributes": True}


class MatchDetail(BaseModel):
    match: Match
    other_profile: Profile


# Payment schemas
class PaymentIntentRequest(BaseModel):
    matchId: UUID4


class Payment(BaseModel):
    id: UUID4
    match_id: UUID4
    method: str
    amount: int
    code: str
    depositor_name: Optional[str] = None
    verified_at: Optional[datetime] = None
    memo: Optional[str] = None

    model_config = {"from_attributes": True}


# Admin schemas
class VerifyPaymentResponse(BaseModel):
    ok: bool


class ActivateMatchResponse(BaseModel):
    ok: bool


class AdminUser(BaseModel):
    id: UUID4
    kakao_user_id: str
    phone_verified: bool
    role: str
    banned: bool
    created_at: datetime
    profile: Optional[Profile] = None

    model_config = {"from_attributes": True}


class AdminMatch(BaseModel):
    id: UUID4
    user_a: UUID4
    user_b: UUID4
    created_at: datetime
    status: str
    user_a_profile: Optional[Profile] = None
    user_b_profile: Optional[Profile] = None
    payment: Optional[Payment] = None

    model_config = {"from_attributes": True}


class AdminPayment(BaseModel):
    id: UUID4
    match_id: UUID4
    method: str
    amount: int
    code: str
    depositor_name: Optional[str] = None
    verified_at: Optional[datetime] = None
    memo: Optional[str] = None
    match: Match

    model_config = {"from_attributes": True}


# Health check
class HealthResponse(BaseModel):
    status: str
    timestamp: datetime