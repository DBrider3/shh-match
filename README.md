# SHH Match - 소확행 매칭 서비스

## 프로젝트 개요

SHH Match는 소확행(소소하지만 확실한 행복) 콘셉트의 사용자 매칭 서비스입니다. 카카오 소셜 로그인을 통한 간편한 회원가입과 JWT 기반 인증 시스템을 제공합니다.

**주요 기능:**
- 카카오 소셜 로그인 연동
- 사용자 매칭 시스템
- 실시간 세션 관리
- 안전한 JWT 인증

## 시스템 아키텍처

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Frontend  │    │   Backend   │    │ PostgreSQL  │
│  (Next.js)  │◄──►│  (FastAPI)  │◄──►│    DB       │
│   Port:3000 │    │  Port:8000  │    │ Port:CUSTOM │
└─────────────┘    └─────────────┘    └─────────────┘
       │                   │                   │
       │            ┌─────────────┐    ┌─────────────┐
       │            │    Redis    │    │   PgAdmin   │
       └────────────│ (Sessions)  │    │  (DB Admin) │
                    │  Port:6379  │    │  Port:5050  │
                    └─────────────┘    └─────────────┘
```

**서비스 구성:**
- **Frontend**: Next.js 기반 웹 애플리케이션, NextAuth.js 인증
- **Backend**: FastAPI 기반 RESTful API, JWT 토큰 관리
- **Database**: PostgreSQL 15 데이터 저장소
- **Cache**: Redis 7 세션 및 캐시 관리
- **Admin**: PgAdmin4 데이터베이스 관리 도구

## 개발 환경 설정

### 시스템 요구사항

- Docker 20.10 이상
- Docker Compose 2.0 이상
- Git
- 최소 4GB RAM

### 초기 설정

1. **저장소 클론**
```bash
git clone <repository-url>
cd shh-match
```

2. **환경변수 설정**
```bash
# 개발용 환경변수 파일 생성
make dev-setup
```

3. **전체 서비스 실행**
```bash
make up
```

## Docker 실행 방법

### 기본 명령어

```bash
# 전체 서비스 시작 (백그라운드)
make up

# 전체 서비스 중지
make down

# 서비스 재시작
make restart

# 서비스 상태 확인
make status

# 실시간 로그 확인
make logs

# 개별 서비스 로그
make logs-fe    # Frontend
make logs-be    # Backend
make logs-db    # Database
```

### 개발용 명령어

```bash
# 컨테이너 쉘 접속
make sh-fe      # Frontend 컨테이너
make sh-be      # Backend 컨테이너

# 데이터베이스 직접 접속
make psql

# 데이터베이스 마이그레이션
make migrate
make migrate-create msg="migration description"
make migrate-downgrade
```

### 테스트 실행

```bash
# Frontend 테스트
make test-fe

# Backend 테스트
make test-be
```

### 환경 정리

```bash
# 전체 정리 (볼륨 포함)
make clean
```

## 환경변수 설정 가이드

### 필수 환경변수

프로젝트 루트에 `.env` 파일을 생성하고 다음 변수들을 설정해주세요:

```bash
# 서비스 URL
API_BASE_URL=http://localhost:8000
WEB_BASE_URL=http://localhost:3000

# 보안 키
APP_SECRET=your-secret-key-here-32-characters-minimum

# 데이터베이스 설정
POSTGRES_USER=app
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=kakao_match
POSTGRES_PORT=5432

# JWT 설정
JWT_ISSUER=shh-match
JWT_AUDIENCE=shh-match-users
JWT_EXPIRE_MINUTES=30

# 카카오 소셜 로그인
KAKAO_CLIENT_ID=your-kakao-app-id
KAKAO_CLIENT_SECRET=your-kakao-app-secret
```

### 환경변수 파일 위치

```
shh-match/
├── .env                    # 루트 환경변수 (Docker Compose용)
├── frontend/.env.local     # Frontend 전용 환경변수
└── backend/.env           # Backend 전용 환경변수
```

### 보안 주의사항

- 모든 `.env` 파일은 Git에서 제외됩니다
- 프로덕션에서는 강력한 비밀번호와 시크릿 키를 사용하세요
- 카카오 개발자 콘솔에서 Redirect URI를 정확히 설정하세요: `http://localhost:3000/api/auth/callback/kakao`

## 서비스별 접근 정보

| 서비스 | URL | 설명 | 기본 계정 |
|--------|-----|------|-----------|
| **Frontend** | http://localhost:3000 | 메인 웹 애플리케이션 | - |
| **Backend API** | http://localhost:8000 | REST API 서버 | - |
| **API 문서** | http://localhost:8000/docs | FastAPI Swagger UI | - |
| **PgAdmin** | http://localhost:5050 | 데이터베이스 관리 | admin@example.com / admin |
| **Redis** | localhost:6379 | 캐시 서버 (CLI 접근만) | - |
| **PostgreSQL** | localhost:${POSTGRES_PORT} | 데이터베이스 | ${POSTGRES_USER} / ${POSTGRES_PASSWORD} |

### PgAdmin 데이터베이스 연결 설정

PgAdmin 접속 후 서버 추가 시 다음 정보를 사용하세요:

- **Host**: `km-db` (Docker 네트워크 내부)
- **Port**: `5432`
- **Database**: `kakao_match`
- **Username**: `app` (또는 설정한 POSTGRES_USER)
- **Password**: 설정한 POSTGRES_PASSWORD

## 개발 워크플로우

### 1. 기능 개발

```bash
# 개발 환경 시작
make up

# 코드 변경 후 실시간 확인 (Hot Reload 지원)
# Frontend: http://localhost:3000
# Backend: http://localhost:8000/docs

# 로그 모니터링
make logs
```

### 2. 데이터베이스 변경

```bash
# 모델 변경 후 마이그레이션 생성
make migrate-create msg="add user profile table"

# 마이그레이션 적용
make migrate

# 필요시 롤백
make migrate-downgrade
```

### 3. 테스트 및 빌드

```bash
# 개별 테스트 실행
make test-fe
make test-be

# 이미지 다시 빌드
make build
```

### 4. 디버깅

```bash
# 컨테이너 내부 접속
make sh-be  # Backend 컨테이너
make sh-fe  # Frontend 컨테이너

# 데이터베이스 직접 확인
make psql

# 실시간 로그 확인
make logs-be  # Backend만
make logs-fe  # Frontend만
```

## 트러블슈팅 가이드

### 자주 발생하는 문제

#### 1. 서비스가 시작되지 않는 경우

```bash
# 서비스 상태 확인
make status

# 상세 로그 확인
make logs

# 포트 충돌 확인
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000

# 완전 정리 후 재시작
make clean
make up
```

#### 2. 데이터베이스 연결 오류

```bash
# 데이터베이스 컨테이너 상태 확인
docker ps | grep km-db

# 데이터베이스 로그 확인
make logs-db

# 직접 연결 테스트
make psql
```

#### 3. 환경변수 설정 문제

```bash
# 환경변수 파일 존재 확인
ls -la .env frontend/.env.local backend/.env

# 컨테이너 내 환경변수 확인
docker exec km-backend env | grep DB_
docker exec km-frontend env | grep NEXT_
```

#### 4. Redis 연결 문제

```bash
# Redis 컨테이너 확인
docker ps | grep km-redis

# Redis 연결 테스트
docker exec km-redis redis-cli ping
```

### 성능 최적화

#### 개발 환경 속도 향상

```bash
# 불필요한 로그 줄이기
docker compose logs --tail=50

# 사용하지 않는 이미지 정리
docker system prune -f

# 볼륨 정리 (주의: 데이터 손실 가능)
docker volume prune
```

## 프로젝트 구조

```
shh-match/
├── .github/                    # GitHub Actions 설정
├── frontend/                   # Next.js 프론트엔드
│   ├── .env.local.example     # 환경변수 템플릿
│   ├── Dockerfile             # Frontend 컨테이너 설정
│   └── ...                    # Next.js 프로젝트 파일들
├── backend/                    # FastAPI 백엔드
│   ├── .env.example          # 환경변수 템플릿
│   ├── Dockerfile            # Backend 컨테이너 설정
│   └── ...                   # FastAPI 프로젝트 파일들
├── docs/                       # 프로젝트 문서
├── docker-compose.yml          # Docker 서비스 정의
├── Makefile                   # 개발용 명령어 스크립트
├── .gitignore                 # Git 제외 파일 목록
└── README.md                  # 이 파일
```

### 컨테이너별 역할

- **km-frontend**: Next.js 개발 서버, NextAuth.js 인증 처리
- **km-backend**: FastAPI 서버, JWT 토큰 발급/검증, 비즈니스 로직
- **km-db**: PostgreSQL 데이터베이스, 사용자 데이터 저장
- **km-redis**: Redis 캐시 서버, 세션 및 임시 데이터 관리
- **km-pgadmin**: PgAdmin4 웹 인터페이스, 데이터베이스 관리 도구

### 데이터 볼륨

- **db_data**: PostgreSQL 데이터 영구 저장
- **redis_data**: Redis 데이터 영구 저장
- **pgadmin_data**: PgAdmin 설정 및 데이터 저장

## 추가 정보

### 관련 문서

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Next.js 공식 문서](https://nextjs.org/docs)
- [NextAuth.js 문서](https://next-auth.js.org/)
- [Docker Compose 참조](https://docs.docker.com/compose/)

### 지원 및 문의

개발 관련 문의나 버그 리포트는 프로젝트 이슈 트래커를 이용해주세요.

---

**주의사항**: 프로덕션 배포 시에는 보안 설정을 강화하고, 환경변수를 안전하게 관리하세요.