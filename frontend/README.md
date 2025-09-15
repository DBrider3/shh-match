# 카카오 매칭 MVP 사이트

카카오 OAuth로 시작하는 안전한 매칭 서비스입니다.

## 기술 스택

- **프레임워크**: Next.js 14 (App Router)
- **언어**: TypeScript
- **인증**: NextAuth.js (Auth.js) + Kakao Provider
- **스타일링**: Tailwind CSS + shadcn/ui
- **상태관리**: TanStack Query (React Query)
- **폼**: React Hook Form + Zod
- **배포**: Vercel (권장)

## 주요 기능

1. **카카오 OAuth 로그인**: 간편하고 안전한 로그인
2. **프로필 작성/편집**: 상세한 프로필 정보 관리
3. **주간 추천**: 매주 새로운 추천 리스트
4. **매칭 시스템**: 상호 관심 표현 시 매칭 성사
5. **결제 시스템**: 계좌이체를 통한 결제
6. **관리자 콘솔**: 사용자/매칭/결제 관리

## 시작하기

### 1. 환경 변수 설정

`.env.local` 파일을 생성하고 다음 변수들을 설정하세요:

```bas
# API Configuration
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# NextAuth Configuration
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-super-secret-key-here

# Kakao OAuth Configuration
KAKAO_CLIENT_ID=your-kakao-client-id
KAKAO_CLIENT_SECRET=your-kakao-client-secret
KAKAO_REDIRECT_URI=http://localhost:3000/api/auth/callback/kakao
```

### 2. 카카오 개발자 설정

1. [Kakao Developers](https://developers.kakao.com/)에서 애플리케이션 생성
2. **플랫폼 설정**에서 웹 플랫폼 추가
3. **Redirect URI** 설정: `http://localhost:3000/api/auth/callback/kakao`
4. **동의항목**에서 필요한 권한 설정
5. **보안**에서 Client Secret 사용 설정

### 3. 설치 및 실행

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드
npm run build

# 프로덕션 서버 실행
npm run start

# 코드 검사
npm run lint
```

## 프로젝트 구조

```
app/
├── (marketing)/           # 마케팅 페이지 (랜딩)
├── api/auth/[...nextauth]/ # NextAuth API 라우트
├── admin/                 # 관리자 페이지
├── discover/              # 추천 페이지
├── matches/               # 매칭 관리
├── payment/               # 결제 페이지
├── profile/edit/          # 프로필 편집
├── layout.tsx             # 루트 레이아웃
└── page.tsx               # 홈페이지

components/
├── ui/                    # shadcn/ui 컴포넌트
├── AdminTable.tsx         # 관리자 테이블
├── Navbar.tsx             # 네비게이션
├── ProfileCard.tsx        # 프로필 카드
└── ...

lib/
├── api.ts                 # API 클라이언트
├── auth.ts                # NextAuth 설정
├── types.ts               # TypeScript 타입 정의
├── validators.ts          # Zod 스키마
└── utils.ts               # 유틸리티 함수
```

## API 연동

백엔드 API는 별도로 구현이 필요합니다. 다음 엔드포인트들을 구현해야 합니다:

- `POST /auth/sync-kakao` - 카카오 사용자 동기화
- `GET /me` - 현재 사용자 정보
- `PUT /profile` - 프로필 업데이트
- `GET /recommendations` - 주간 추천 리스트
- `POST /likes` - 좋아요 전송
- `GET /matches` - 매칭 리스트
- `POST /payments/intent` - 결제 의도 생성
- 관리자 API들...

자세한 API 명세는 `docs/` 폴더의 문서를 참조하세요.

## 배포

### Vercel 배포 (권장)

1. Vercel에 GitHub 저장소 연결
2. 환경 변수 설정
3. 자동 배포 완료

### 기타 플랫폼

- Netlify
- AWS Amplify
- Cloudflare Pages
- 직접 서버 배포

## 개발 가이드

### 코드 품질 원칙

1. **가독성**: 코드가 읽기 쉽고 한 번에 고려할 맥락이 적음
2. **예측 가능성**: 함수명과 파라미터만 보고도 동작을 예측 가능
3. **응집도**: 함께 수정되어야 할 코드가 항상 같이 수정됨
4. **결합도**: 코드 수정 시 영향범위가 예측 가능하고 제한적

### 컴포넌트 설계

- 단일 책임 원칙 준수
- Props 인터페이스 최소화
- 조건부 렌더링 분리
- 컴포넌트 조합 활용

### 스타일링

- Tailwind CSS 활용
- shadcn/ui 컴포넌트 재사용
- 반응형 디자인 적용
- 다크모드 지원 고려

## 라이선스

MIT License

## 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/amazing-feature`)
3. Commit your Changes (`git commit -m 'Add some amazing feature'`)
4. Push to the Branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 문의

프로젝트 관련 문의사항이 있으시면 이슈를 생성해주세요."