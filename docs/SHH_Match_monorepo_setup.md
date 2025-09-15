# SHH Match — Monorepo Setup (Next.js + FastAPI)

> 목적: **프런트(Next.js)**와 **백엔드(FastAPI)**를 한 저장소(monorepo)에서 개발/운영하기 위한 표준 구조, `docker-compose` 개발 환경, 환경 변수 예시, 배포 힌트를 제공.

---

## 1) 디렉토리 구조

```
shh-match/
├─ frontend/                 # Next.js 14 (App Router, TS)
│  ├─ app/
│  ├─ components/
│  ├─ lib/
│  ├─ public/
│  ├─ Dockerfile
│  ├─ package.json
│  ├─ tsconfig.json
│  ├─ .env.local.example
│  └─ next.config.mjs
├─ backend/                  # FastAPI
│  ├─ app/
│  │  ├─ api/v1/
│  │  ├─ core/
│  │  ├─ db/
│  │  └─ main.py
│  ├─ Dockerfile
│  ├─ pyproject.toml / requirements.txt
│  ├─ alembic.ini
│  ├─ .env.example
│  └─ README.md
├─ docs/
│  └─ architecture.md
├─ docker-compose.yml
├─ .env                      # 루트 공용(개발) 환경변수
├─ Makefile                  # 자주 쓰는 명령 모음
└─ .github/workflows/
   ├─ ci-frontend.yml
   └─ ci-backend.yml
```

---

## 2) 환경 변수

### 2.1 루트 `.env` (개발용)
```
# 공용
TZ=Asia/Seoul

# 네트워크/도메인
WEB_BASE_URL=http://localhost:3000
API_BASE_URL=http://localhost:8000

# DB
POSTGRES_USER=app
POSTGRES_PASSWORD=changeme
POSTGRES_DB=kakao_match
POSTGRES_PORT=5432

# JWT
JWT_ISSUER=kakao-match-api
JWT_AUDIENCE=kakao-match-web
JWT_EXPIRE_MINUTES=10080
APP_SECRET=replace-with-32-bytes-secret
```

### 2.2 `frontend/.env.local.example`
```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=replace-with-32-bytes-secret

KAKAO_CLIENT_ID=___
KAKAO_CLIENT_SECRET=___
KAKAO_REDIRECT_URI=http://localhost:3000/api/auth/callback/kakao
```

### 2.3 `backend/.env.example`
```
APP_ENV=dev
APP_SECRET=replace-with-32-bytes-secret
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO

DB_HOST=db
DB_PORT=5432
DB_NAME=kakao_match
DB_USER=app
DB_PASSWORD=changeme

REDIS_URL=redis://redis:6379/0

PASSWORD_HASH_SCHEME=bcrypt
JWT_ISSUER=kakao-match-api
JWT_AUDIENCE=kakao-match-web
JWT_EXPIRE_MINUTES=10080
JWT_ALG=HS256
TZ=Asia/Seoul
```

---

## 3) Dockerfile 예시

### 3.1 `frontend/Dockerfile`
```dockerfile
# Dev image
FROM node:20-slim AS base
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm","run","dev"]
```

> 프로덕션 빌드는 Vercel/CloudFront 등을 권장. 필요 시 multi-stage로 `npm run build` → `next start`.

### 3.2 `backend/Dockerfile`
```dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY . /app
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--proxy-headers"]
```

---

## 4) docker-compose (개발용)

> 루트에 `docker-compose.yml`

```yaml
version: "3.9"
services:
  frontend:
    build: ./frontend
    container_name: km-frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=${API_BASE_URL}
      - NEXTAUTH_URL=${WEB_BASE_URL}
      - NEXTAUTH_SECRET=${APP_SECRET}
      - KAKAO_CLIENT_ID=${KAKAO_CLIENT_ID}
      - KAKAO_CLIENT_SECRET=${KAKAO_CLIENT_SECRET}
      - KAKAO_REDIRECT_URI=${WEB_BASE_URL}/api/auth/callback/kakao
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

  backend:
    build: ./backend
    container_name: km-backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env.example
    environment:
      - DB_HOST=db
      - DB_PORT=${POSTGRES_PORT}
      - DB_NAME=${POSTGRES_DB}
      - DB_USER=${POSTGRES_USER}
      - DB_PASSWORD=${POSTGRES_PASSWORD}
      - CORS_ORIGINS=${WEB_BASE_URL}
      - APP_SECRET=${APP_SECRET}
      - JWT_ISSUER=${JWT_ISSUER}
      - JWT_AUDIENCE=${JWT_AUDIENCE}
      - JWT_EXPIRE_MINUTES=${JWT_EXPIRE_MINUTES}
    volumes:
      - ./backend:/app
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    container_name: km-db
    ports:
      - "${POSTGRES_PORT}:5432"
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    volumes:
      - db_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    container_name: km-redis
    ports:
      - "6379:6379"

volumes:
  db_data: {}
```

> 프런트/백 모두 **볼륨 마운트**로 코드 변경이 바로 반영되어 로컬 개발에 유리.

---

## 5) Makefile (개발 생산성)

`Makefile` (루트):

```makefile
.PHONY: up down logs sh-fe sh-be psql migrate

up:
\tdocker-compose up -d --build

down:
\tdocker-compose down

logs:
\tdocker-compose logs -f --tail=100

sh-fe:
\tdocker exec -it km-frontend /bin/bash

sh-be:
\tdocker exec -it km-backend /bin/bash

psql:
\tdocker exec -it km-db psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

migrate:
\tdocker exec -it km-backend alembic upgrade head
```

---

## 6) 프런트/백엔드 개발 명령

### 6.1 Frontend (로컬 컨테이너 내부)
```bash
# 컨테이너 셸 진입
make sh-fe
# 의존성 설치
npm i
# 개발 서버
npm run dev
```

### 6.2 Backend (로컬 컨테이너 내부)
```bash
make sh-be
# 의존성 설치(요구사항 파일 사용 시)
pip install -r requirements.txt
# DB 마이그레이션
alembic upgrade head
# 개발 서버(uvicorn)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 7) CORS & 프록시

- 개발에서는 `CORS_ORIGINS=http://localhost:3000`으로 제한.
- 운영에서 Nginx/Cloudflare 프록시 사용 시 `X-Forwarded-*` 헤더 처리(`--proxy-headers` 옵션 이미 추가).

---

## 8) VSCode Devcontainers (선택)

`.devcontainer/` 구성으로 통합 개발 환경 제공 가능. 팀이 작은 경우 우선순위 낮음.

---

## 9) GitHub Actions (요약 샘플)

### 9.1 `frontend` CI (`.github/workflows/ci-frontend.yml`)
```yaml
name: Frontend CI
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: frontend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build --if-present
```

### 9.2 `backend` CI (`.github/workflows/ci-backend.yml`)
```yaml
name: Backend CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: backend
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python -m pytest -q || true  # 테스트 도입 전 임시
```

---

## 10) 로컬 실행 절차 (요약)

```bash
# 1) 루트 .env 생성 (예시는 파일 참고)
cp frontend/.env.local.example frontend/.env.local
cp backend/.env.example backend/.env
# 2) 도커 컴포즈
make up
# 3) 백엔드 DB 마이그레이션
make migrate
# 4) 브라우저
open http://localhost:3000
```

---

## 11) 운영 배포 힌트

- **프런트**: Vercel 또는 `next build && next start`로 ECS/EC2에 배포.
- **백엔드**: Docker 이미지를 ECR/Registry에 푸시 후 ECS/EC2/Kubernetes로 배포. Gunicorn+Uvicorn workers 권장.
- **DB**: RDS(PostgreSQL). 백업/스냅샷 정책.
- **비밀 관리**: AWS Secrets Manager / GitHub Encrypted Secrets.
- **도메인/SSL**: CloudFront+ACM 또는 Nginx+Let’s Encrypt.

---

## 12) 트러블슈팅 체크리스트

- 3000/8000 포트 충돌 → 로컬에서 사용 중인 포트 확인
- CORS 403 → `backend`의 `CORS_ORIGINS` 확인
- Kakao OAuth Redirect URI → 카카오 콘솔과 `.env` 일치 여부 확인
- DB 마이그레이션 실패 → `alembic` 버전 확인 후 재생성
- 프런트가 API에 인증 못 붙임 → NextAuth 세션에 `backendJwt` 저장 로직 검증

---

이 문서대로 구성하면 **monorepo로 빠르게 개발 환경을 띄우고**, MVP 검증 후 FE/BE를 분리 배포하는 전략으로 확장할 수 있습니다.
