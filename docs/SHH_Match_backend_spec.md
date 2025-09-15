# SHH Match Backend — FastAPI Build Spec (MVP)

> 목적: 카카오 소셜 로그인으로 유입된 사용자가 **주간 추천 → 좋아요/매칭 → 계좌이체 결제 → 관리자 승인**까지 진행할 수 있는 백엔드(REST API) 설계 및 구현 가이드. 프런트는 Next.js(App Router)이며, 인증 연동/엔드포인트 계약을 본 문서에 명시한다. 타임존은 **Asia/Seoul** 기준.

---

## 0. 범위(Goals / Non‑Goals)

**Goals**
- FastAPI 기반 REST API
- JWT 인증(Stateless) + RBAC(관리자 권한)
- 카카오 로그인 동기화 엔드포인트(`/auth/sync-kakao`)
- 프로필/선호 저장 및 조회
- 주간 추천 생성(중복 방지) + 좋아요/매칭
- 결제(계좌이체) **수기 확인** → 승인/매칭 활성화
- 관리자 콘솔용 엔드포인트
- 관측성(로그/메트릭), 마이그레이션(Alembic), 배포(Docker)

**Non‑Goals (MVP 제외)**
- 카카오 비즈메시지 발송, 가상계좌/PG 자동확인(Phase 2)
- 고도화된 추천 모델(간단 스코어만)

---

## 1. 아키텍처 개요

- **App**: FastAPI + Uvicorn/Gunicorn
- **DB**: PostgreSQL (SQLAlchemy + Alembic)
- **Cache/Queue(선택)**: Redis (세션 없음, 배치 락/캐시용)
- **Storage**: S3/R2 (사진 URL만 저장, 업로드는 프런트에서 pre-signed 사용)
- **Scheduler**: APScheduler (주 1회 `build_weekly_recommendations`)
- **Auth**: Kakao OAuth는 프런트(NextAuth)에서 처리 → 백엔드 `/auth/sync-kakao`로 `kakaoUserId` 동기화 → **백엔드 JWT 발급**
- **Observability**: structlog, Prometheus(선택), OpenTelemetry(선택)

---

## 2. 환경 변수(.env)

```bash
APP_ENV=prod
APP_SECRET=replace-with-32-bytes-secret
API_BASE_PATH=/
CORS_ORIGINS=https://web.your-domain.com
LOG_LEVEL=INFO

DB_HOST=postgres
DB_PORT=5432
DB_NAME=kakao_match
DB_USER=app
DB_PASSWORD=change-me

REDIS_URL=redis://redis:6379/0    # optional

# Security
PASSWORD_HASH_SCHEME=bcrypt
JWT_ISSUER=kakao-match-api
JWT_AUDIENCE=kakao-match-web
JWT_EXPIRE_MINUTES=10080          # 7 days
JWT_ALG=HS256

# Timezone
TZ=Asia/Seoul
```

---

## 3. 데이터 모델(ER 요약)

엔티티 및 핵심 관계:

```
users (1)──(1) profiles
users (1)──(1) preferences
users (1)──(*) likes ──(*) users
users (1)──(*) matches (양쪽 userA, userB)
matches (1)──(1) payments
users (1)──(*) exposure_log (본인에게 노출된 대상 기록)
recommendations: 주차별 제안 스냅샷
```

### 3.1 SQL DDL (초안)

```sql
-- users
CREATE TABLE users (
  id UUID PRIMARY KEY,
  kakao_user_id TEXT UNIQUE NOT NULL,
  phone_verified BOOLEAN DEFAULT FALSE,
  role TEXT DEFAULT 'user', -- 'user' | 'admin'
  banned BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- profiles
CREATE TABLE profiles (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  nickname TEXT NOT NULL,
  gender CHAR(1) CHECK (gender IN ('M','F')) NOT NULL,
  birth_year INT NOT NULL,
  height INT,
  region TEXT,
  job TEXT,
  intro TEXT,
  photos JSONB NOT NULL DEFAULT '[]'::jsonb,
  visible JSONB NOT NULL DEFAULT '{"age":true,"height":false,"region":true,"job":true,"intro":true}'
);

-- preferences
CREATE TABLE preferences (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  target_gender CHAR(1) CHECK (target_gender IN ('M','F')) NOT NULL,
  age_min INT NOT NULL,
  age_max INT NOT NULL,
  regions TEXT[] DEFAULT '{}',
  keywords TEXT[] DEFAULT '{}',
  blocks UUID[] DEFAULT '{}'
);

-- exposure log: 노출 중복 방지
CREATE TABLE exposure_log (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  target_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  reason TEXT,                           -- 'weekly_rec', etc.
  seen_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (user_id, target_user_id, date_trunc('week', seen_at))
);

-- recommendations: 주간 추천 스냅샷
CREATE TABLE recommendations (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  target_user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  batch_week TEXT NOT NULL,              -- e.g., 2025-W37
  score NUMERIC(6,3) DEFAULT 0,
  sent_at TIMESTAMPTZ,
  responded BOOLEAN DEFAULT FALSE,
  UNIQUE (user_id, target_user_id, batch_week)
);

-- likes
CREATE TABLE likes (
  id BIGSERIAL PRIMARY KEY,
  from_user UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  to_user UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  batch_week TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  UNIQUE (from_user, to_user, batch_week)
);

-- matches
CREATE TABLE matches (
  id UUID PRIMARY KEY,
  user_a UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  user_b UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  status TEXT NOT NULL CHECK (status IN ('pending','active','closed')),
  UNIQUE (LEAST(user_a, user_b), GREATEST(user_a, user_b)) -- 한 쌍 중복 방지
);

-- payments
CREATE TABLE payments (
  id UUID PRIMARY KEY,
  match_id UUID NOT NULL UNIQUE REFERENCES matches(id) ON DELETE CASCADE,
  method TEXT NOT NULL CHECK (method IN ('transfer')),
  amount INT NOT NULL,
  code TEXT NOT NULL,             -- 입금자명에 포함될 고유코드
  depositor_name TEXT,
  verified_at TIMESTAMPTZ,
  memo TEXT
);

-- admin actions (감사 로그)
CREATE TABLE admin_actions (
  id BIGSERIAL PRIMARY KEY,
  admin_id UUID NOT NULL REFERENCES users(id),
  action TEXT NOT NULL,
  target_id TEXT,
  detail JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- reports (신고)
CREATE TABLE reports (
  id UUID PRIMARY KEY,
  reporter UUID NOT NULL REFERENCES users(id),
  reported UUID NOT NULL REFERENCES users(id),
  reason TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  handled BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_recs_user_week ON recommendations(user_id, batch_week);
CREATE INDEX idx_exposure_user ON exposure_log(user_id, seen_at);
```

---

## 4. API 설계(엔드포인트 계약)

> 모든 보호 라우트는 `Authorization: Bearer <jwt>` 필요. 응답은 `application/json`.

### 4.1 인증/사용자
- `POST /auth/sync-kakao`
  - Body: `{ kakaoUserId: string, email?: string, nickname?: string }`
  - Res: `{ jwt: string, user: User }`
- `GET /me`
  - Res: `{ user: User, profile?: Profile, preferences?: Preferences }`

### 4.2 프로필/선호
- `PUT /profile` → Profile 저장/갱신, 본인만
- `PUT /preferences` → Preferences 저장/갱신, 본인만

### 4.3 추천/노출
- `GET /recommendations?week=YYYY-Www`
  - Res: `RecommendationItem[]`
- (관리자) `POST /admin/recs/run` (임시 배치 트리거)

### 4.4 좋아요/매칭
- `POST /likes`
  - Body: `{ toUserId: string, batchWeek: string }`
  - Res: `{ ok: true }`
- `GET /matches`
  - Res: `Match[]`
- `GET /matches/:matchId`
  - Res: `{ match: Match, otherProfile: Profile }`

### 4.5 결제
- `POST /payments/intent`
  - Body: `{ matchId: string }`
  - Res: `Payment`
- `GET /payments/:paymentId`
  - Res: `Payment`
- (관리자) `POST /admin/payments/:paymentId/verify`
  - Res: `{ ok: true }`
- (관리자) `POST /admin/matches/:matchId/activate`
  - Res: `{ ok: true }`

### 4.6 관리자
- `GET /admin/users?query=&page=`
- `GET /admin/matches?status=`
- `GET /admin/payments?status=`

---

## 5. 인증/JWT 설계

- NextAuth(Kakao) 로그인 직후, 프런트가 `/auth/sync-kakao` 호출
- 서버는 `kakao_user_id`로 `users` upsert 후 **JWT** 발급
- JWT 클레임:
  ```json
  {
    "sub": "<user_id>",
    "role": "user|admin",
    "iss": "kakao-match-api",
    "aud": "kakao-match-web",
    "iat": 1710000000,
    "exp": 1710604800
  }
  ```
- 보호 라우트는 `Depends(current_user)`로 토큰 검증

---

## 6. 추천 배치 로직(주 1회)

### 6.1 스케줄러
- APScheduler cron: 매주 월요일 10:00 KST (예시)
- Job: `build_weekly_recommendations(week_label: str)`

### 6.2 알고리즘(간단 버전)
1) 각 사용자 u에 대해 후보 풀: 상호 선호/차단/연령/지역/활동조건 필터
2) 점수화: 선호 적합도 + 신규/미노출 가점 – 최근 노출 페널티
3) 상위 K명(예: 10명) → `recommendations` insert
4) `exposure_log` 기록 (중복 방지 기준 8~12주 유지)
5) 알림은 프런트(폴링/배너)로 처리

```python
def build_for_user(u):
    candidates = filter_by_mutual_prefs(u)
    candidates = exclude_recent_exposure(u, candidates, weeks=12)
    scored = score_candidates(u, candidates)  # simple heuristic
    topk = take_topk(scored, k=10)
    save_recommendations(u, topk, week_label)
    log_exposure(u, topk, reason='weekly_rec')
```

---

## 7. 결제 흐름(계좌이체 + 수기 확인)

- 상호 좋아요 → `matches(status='pending')`
- 사용자가 `/payments/intent` 호출 → 서버는 금액·고유코드(code) 생성, 결제 레코드 생성
- 사용자가 실제 계좌이체 수행(입금자명에 code 포함)
- 관리자가 **입금 확인** 후 `POST /admin/payments/:id/verify`
  - 서버: `payments.verified_at` 설정 → 감사로그 기록
  - 필요 시 `POST /admin/matches/:id/activate`로 `status='active'`
- Phase 2: 가상계좌/PG 연동(웹훅으로 자동 확인)

---

## 8. 보안/컴플라이언스

- 최소 수집 원칙: 연락처/민감정보 저장 금지(매칭 활성화 때 공개되는 범위 명확화)
- 사진 URL은 공개 CDN 사용 시 워터마크 권장
- PII 필드(전화번호 등 필요 시)는 **암호화**(pgcrypto 또는 앱 레벨 Fernet) 저장
- RBAC: `role='admin'`만 관리자 라우트 접근 가능
- 레이트리밋(선택): `X-RateLimit-*` 헤더, 또는 NGINX 레벨
- CORS: 화이트리스트 도메인만 허용
- 로깅: 요청 ID, 사용자 ID, 액션, 결과, 에러 스택
- 감사 로그: 모든 관리자 승인/변경은 `admin_actions`에 기록
- 법적 고지: 개인정보 처리방침, 이용약관, 환불정책, 19+ 확인

---

## 9. 디렉터리 구조(FastAPI)

```
app/
  core/
    config.py          # Env, settings
    security.py        # JWT, pwd hashing
    deps.py            # Depends(get_db, current_user, admin_only)
    scheduling.py      # APScheduler init, jobs
  db/
    base.py            # SQLAlchemy Base
    session.py         # engine/sessionmaker
    models.py          # ORM models
    schemas.py         # Pydantic models
    crud/              # repository functions
    migrations/        # Alembic
  api/
    v1/
      routes_auth.py
      routes_users.py
      routes_profile.py
      routes_recs.py
      routes_likes.py
      routes_matches.py
      routes_payments.py
      routes_admin.py
  main.py
  __init__.py
Dockerfile
docker-compose.yml
alembic.ini
```

---

## 10. Pydantic/ORM 예시(발췌)

```python
# app/db/models.py
import uuid
from sqlalchemy import Column, String, Boolean, Integer, Text, JSON, ForeignKey, CheckConstraint, UniqueConstraint, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from .base import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kakao_user_id = Column(Text, unique=True, nullable=False)
    phone_verified = Column(Boolean, default=False)
    role = Column(String, default='user')
    banned = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default="now()")

    profile = relationship('Profile', uselist=False, back_populates='user', cascade='all, delete')
    preferences = relationship('Preferences', uselist=False, back_populates='user', cascade='all, delete')

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
    visible = Column(JSON, nullable=False, default=dict)
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
    user = relationship('User', back_populates='preferences')
```

```python
# app/core/security.py
from datetime import datetime, timedelta, timezone
import jwt
from pydantic import BaseModel

class JwtPayload(BaseModel):
    sub: str
    role: str = 'user'
    iss: str
    aud: str
    iat: int
    exp: int

def create_jwt(user_id: str, role: str, secret: str, issuer: str, audience: str, minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id, "role": role,
        "iss": issuer, "aud": audience,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp())
    }
    return jwt.encode(payload, secret, algorithm="HS256")
```

```python
# app/api/v1/routes_auth.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.db.session import get_db
from app.db import models
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_jwt

router = APIRouter(prefix="/auth", tags=["auth"])

class SyncKakaoReq(BaseModel):
    kakaoUserId: str
    email: str | None = None
    nickname: str | None = None

@router.post("/sync-kakao")
def sync_kakao(body: SyncKakaoReq, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(kakao_user_id=body.kakaoUserId).first()
    if not user:
        user = models.User(kakao_user_id=body.kakaoUserId)
        db.add(user); db.commit(); db.refresh(user)
        # 기본 프로필/선호 생성(선택)
        db.add(models.Profile(user_id=user.id, nickname=body.nickname or "사용자", gender='M', birth_year=1990, photos=[], visible={"age":True,"height":False,"region":True,"job":True,"intro":True}))
        db.add(models.Preferences(user_id=user.id, target_gender='F', age_min=20, age_max=40))
        db.commit()
    token = create_jwt(str(user.id), user.role, settings.APP_SECRET, settings.JWT_ISSUER, settings.JWT_AUDIENCE, settings.JWT_EXPIRE_MINUTES)
    return {"jwt": token, "user": {"id": str(user.id), "kakaoUserId": user.kakao_user_id, "phoneVerified": user.phone_verified, "banned": user.banned, "createdAt": str(user.created_at)}}
```

---

## 11. 추천/좋아요/매칭 라우터(요지)

```python
# app/api/v1/routes_recs.py
@router.get("/recommendations")
def get_recs(week: str, current=Depends(current_user), db: Session = Depends(get_db)):
    rows = db.query(models.Recommendation)...  # user_id=current.id, batch_week=week
    # 필요한 프로필 join 후 공개 필드만 반환
    return serialize_recommendations(rows)
```

```python
# app/api/v1/routes_likes.py
class LikeReq(BaseModel):
    toUserId: str
    batchWeek: str

@router.post("/likes")
def like(body: LikeReq, current=Depends(current_user), db: Session = Depends(get_db)):
    # insert like (unique by from, to, week)
    # 상호 좋아요 여부 확인 → 있으면 matches pending 생성
    # 이미 pending/active 매칭 존재하면 무시
    return {"ok": True}
```

```python
# app/api/v1/routes_matches.py
@router.get("/matches")
def my_matches(current=Depends(current_user), db: Session = Depends(get_db)):
    # user가 포함된 matches 목록
    return serialize_matches(...)
```

---

## 12. 결제 라우터(요지)

```python
# app/api/v1/routes_payments.py
class PaymentIntentReq(BaseModel):
    matchId: str

@router.post("/payments/intent")
def create_intent(body: PaymentIntentReq, current=Depends(current_user), db: Session = Depends(get_db)):
    # match 소유권 검사(userA/B 중 한명이어야)
    # 금액/코드 생성 → payments upsert
    # code 예: KM-{last4(user)}-{rand3}
    return serialize_payment(...)

@router.get("/payments/{payment_id}")
def get_payment(payment_id: str, current=Depends(current_user), db: Session = Depends(get_db)):
    # 자신의 match에 속한 payment만 조회 허용
    return serialize_payment(...)
```

관리자용:

```python
# app/api/v1/routes_admin.py
@router.post("/admin/payments/{payment_id}/verify")
def verify_payment(payment_id: str, admin=Depends(admin_only), db: Session = Depends(get_db)):
    # verified_at=now(), 감사로그
    return {"ok": True}

@router.post("/admin/matches/{match_id}/activate")
def activate_match(match_id: str, admin=Depends(admin_only), db: Session = Depends(get_db)):
    # status='active'
    return {"ok": True}
```

---

## 13. 스케줄러 초기화

```python
# app/core/scheduling.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from zoneinfo import ZoneInfo
from datetime import datetime
from .jobs import build_weekly_recommendations

def init_scheduler():
    scheduler = AsyncIOScheduler(timezone=ZoneInfo("Asia/Seoul"))
    scheduler.add_job(lambda: build_weekly_recommendations(), 'cron', day_of_week='mon', hour=10, minute=0, id='weekly-recs')
    scheduler.start()
    return scheduler
```

```python
# app/main.py
def create_app():
    app = FastAPI()
    # CORS, routers, db init ...
    if settings.APP_ENV != 'test':
        init_scheduler()
    return app
```

---

## 14. 배포(Docker)

**Dockerfile** (예시)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry && poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
COPY . /app
EXPOSE 8000
CMD [\"gunicorn\", \"app.main:app\", \"-k\", \"uvicorn.workers.UvicornWorker\", \"--bind\", \"0.0.0.0:8000\", \"--workers\", \"2\", \"--timeout\", \"120\"]
```

**docker-compose.yml** (요지)
```yaml
services:
  api:
    build: .
    env_file: .env
    ports: [\"8000:8000\"]
    depends_on: [db]
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: change-me
      POSTGRES_DB: kakao_match
    volumes: [db_data:/var/lib/postgresql/data]
  redis:
    image: redis:7
volumes:
  db_data: {}
```

Alembic:
```bash
alembic init app/db/migrations
alembic revision -m "init" --autogenerate
alembic upgrade head
```

---

## 15. 관측성

- **로그**: JSON 구조화(요청 ID, userId, path, status, latency)
- **메트릭**: 요청 수/에러율/DB 쿼리 시간/배치 실행 시간
- **헬스체크**: `/healthz` (DB 연결 확인)

---

## 16. 테스트 전략

- 유닛: CRUD/서비스 레이어
- 통합: `/auth/sync-kakao`, `/likes` 상호매칭 케이스
- 배치: 추천 생성 시 중복 노출 방지
- 보안: 관리자 라우트 권한, 토큰 만료

---

## 17. AI Agent 실행 체크리스트

1. Python 3.11 프로젝트 초기화(poetry/pipenv)
2. FastAPI/SQLAlchemy/Alembic 기본 셋업
3. `users/profiles/preferences` 모델 및 마이그레이션 생성
4. JWT 발급/검증 유틸 작성
5. `/auth/sync-kakao` 구현 → 통합 테스트
6. `/profile`, `/preferences` CRUD 구현
7. 추천 스케줄러/서비스 구현 + `/recommendations` 조회
8. `/likes` 구현 → 상호 좋아요 시 `matches(pending)` 생성
9. `/matches` 조회/상세
10. 결제: `/payments/intent`, `/payments/:id`
11. 관리자: 결제 `verify`, 매칭 `activate`, `recs/run`
12. CORS/보안 헤더/로그/헬스체크
13. Dockerfile/Compose 및 Alembic 마이그레이션
14. 기본 E2E 흐름 검증

---

## 18. Phase 2 제안(선택)
- PG 연동(가상계좌): 입금 웹훅 → 자동 `verified_at`
- 알림센터(이메일/SMS) 및 카카오 비즈 채널 템플릿 발송
- 추천 점수 고도화(노출균형, 신뢰지표, 신고 패널티)
- 프로필 사진 AI 검수(부적절 콘텐츠 필터)

---

본 문서를 기반으로 백엔드와 프런트의 계약이 일치하며, MVP 범위에서 안정적으로 운영 가능한 구조를 제공한다.
