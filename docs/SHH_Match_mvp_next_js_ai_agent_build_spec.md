# SHH Match MVP — Next.js AI Agent Build Spec

> 목적: 카카오 소셜 로그인으로 가입한 사용자가 **매주 추천 이성**을 중복 없이 받아 보고, **상호 매칭 시 계좌이체 결제 → 관리자 승인** 후 연락처 공개(또는 채팅 오픈)까지 이어지는 웹 서비스의 **Next.js 프런트엔드**를 구축한다. 백엔드는 FastAPI 기준으로 별도 구현(본 문서에 API 계약 포함).

---

## 0. 범위(Goals / Non‑Goals)

**Goals**
- 카카오 OAuth 로그인(NextAuth)으로 사용자 식별 및 세션 관리
- 프로필 작성/편집 + “이성에게 보이는 항목” 가시성 설정
- 매주 추천 리스트 노출(중복 방지: 백엔드에서 계산, 프런트는 표시)
- 좋아요(도전) / 패스 → 상호 매칭 시 결제 페이지로 안내
- 결제(계좌이체) 후 **관리자 승인**되면 매칭 활성화 상태/연락처 공개
- 관리자 콘솔(요약판): 유저/프로필 검수, 매칭/결제 확인 및 승인 버튼

**Non‑Goals (MVP에서 제외)**
- 카카오 비즈메시지 발송, 실시간 푸시(알림센터는 폴링 기반)
- 추천 알고리즘 고도화(백엔드 점수 산정은 단순 기준)
- 가상계좌/PG 연동(후속 단계)

---

## 1. 기술 스택
- **Next.js 14 (App Router, TypeScript)**
- **Auth.js(NextAuth v5)** + Kakao Provider
- **Tailwind CSS + shadcn/ui + lucide-react**
- **TanStack Query (React Query)**: 데이터 fetching/캐싱/에러/로딩 관리
- 상태: 서버 상태는 React Query, 전역 UI 상태는 컨텍스트(필요 시 Zustand)
- 폼: **react-hook-form** + **zod** 유효성 검증
- 배포: Vercel (또는 자체 서버)

---

## 2. 디렉터리 구조 (요지)
```
app/
  (marketing)/
    page.tsx                 # 랜딩
  api/auth/[...nextauth]/route.ts  # NextAuth Kakao OAuth
  layout.tsx
  page.tsx                  # 로그인 후 홈(추천함으로 리다이렉트)
  profile/
    edit/page.tsx
  discover/page.tsx         # 주간 추천 리스트
  matches/page.tsx          # 매칭 내역
  payment/[matchId]/page.tsx
  admin/
    page.tsx                # 대시보드(요약)
    users/page.tsx
    matches/page.tsx
    payments/page.tsx
    actions.ts              # 서버액션(관리자 승인 등)
components/
  ui/*                      # shadcn/ui 래핑 컴포넌트
  Navbar.tsx, Footer.tsx
  ProfileCard.tsx
  RecommendationList.tsx
  LikePassButtons.tsx
  PaymentInstructions.tsx
  AdminTable.tsx
lib/
  api.ts                    # 백엔드 REST 클라이언트(fetch wrapper)
  auth.ts                   # NextAuth 옵션
  types.ts                  # 공유 타입 정의
  validators.ts             # zod 스키마
  utils.ts
middleware.ts               # 접근 제어
```

---

## 3. 환경 변수(.env)
```
NEXT_PUBLIC_API_BASE_URL=https://api.your-domain.com
NEXTAUTH_URL=https://web.your-domain.com
NEXTAUTH_SECRET=... # openssl rand -base64 32
KAKAO_CLIENT_ID=...
KAKAO_CLIENT_SECRET=...
KAKAO_REDIRECT_URI=https://web.your-domain.com/api/auth/callback/kakao
```

> 주의: 카카오 개발자 콘솔에서 Redirect URI를 동일하게 등록.

---

## 4. 데이터/타입 계약 (프런트 관점)
```ts
// lib/types.ts
export type Gender = 'M' | 'F';

export interface User {
  id: string;
  kakaoUserId: string;
  phoneVerified: boolean;
  createdAt: string;
  banned: boolean;
}

export interface Profile {
  userId: string;
  nickname: string;
  gender: Gender;
  birthYear: number;
  height?: number;
  region?: string;
  job?: string;
  intro?: string;
  photos: string[]; // public CDN urls
  visible: {
    age: boolean; height: boolean; region: boolean; job: boolean; intro: boolean;
  }
}

export interface Preferences {
  userId: string;
  targetGender: Gender;
  ageMin: number; ageMax: number;
  regions: string[];
  keywords: string[];
  blocks: string[]; // userIds
}

export interface RecommendationItem {
  targetUserId: string;
  profile: Pick<Profile, 'nickname'|'gender'|'birthYear'|'region'|'job'|'photos'|'intro'|'visible'>;
  batchWeek: string; // e.g., 2025-W37
}

export interface LikePayload { toUserId: string; batchWeek: string; }

export interface Match {
  id: string; userA: string; userB: string;
  createdAt: string; status: 'pending'|'active'|'closed';
}

export interface Payment {
  id: string; matchId: string; method: 'transfer'; amount: number; code: string; depositorName?: string;
  verifiedAt?: string; memo?: string;
}
```

---

## 5. 백엔드 API 계약(프런트가 기대하는 REST)
> 실제 FastAPI에서 구현 필요. 응답은 `application/json`, 인증은 **NextAuth 세션 → 백엔드 JWT 교환**(아래 6장 참조) 또는 세션 쿠키 프록시.

```
POST /auth/sync-kakao
  Body: { kakaoUserId, email?, nickname? }
  Res:  { jwt, user: User }

GET  /me
  Auth: Bearer jwt
  Res:  { user: User, profile?: Profile, preferences?: Preferences }

PUT  /profile
  Body: Profile
  Res:  Profile

PUT  /preferences
  Body: Preferences
  Res:  Preferences

GET  /recommendations?week=2025-W37
  Res:  RecommendationItem[]

POST /likes
  Body: LikePayload
  Res:  { ok: true }

GET  /matches
  Res:  Match[]

GET  /matches/:matchId
  Res:  { match: Match, otherProfile: Profile }

POST /payments/intent
  Body: { matchId }
  Res:  Payment  # amount, code(입금자명+고유코드 안내)

GET  /payments/:paymentId
  Res:  Payment

# Admin
GET  /admin/users?query=&page=
GET  /admin/matches?status=
GET  /admin/payments?status=
POST /admin/payments/:paymentId/verify   # 입금 확인
POST /admin/matches/:matchId/activate    # 매칭 활성화(연락처 공개)
POST /admin/recs/run                     # 주간 추천 생성 트리거(임시)
```

---

## 6. 인증 설계 (NextAuth + Kakao + 백엔드 동기화)

### 6.1 흐름
1) 사용자가 카카오로 로그인
2) NextAuth Kakao Provider로 프로필/ID 수신
3) **`signIn` 콜백에서** FastAPI `/auth/sync-kakao` 호출 → 사용자 생성/조회 + **백엔드 JWT** 발급
4) NextAuth 세션에 `backendJwt` 저장 → 이후 API 호출 시 Authorization 헤더로 첨부

### 6.2 NextAuth 설정 샘플
```ts
// lib/auth.ts
import NextAuth from "next-auth";
import Kakao from "@auth/core/providers/kakao"; // NextAuth v5(Auth.js)

export const authOptions = {
  providers: [
    Kakao({
      clientId: process.env.KAKAO_CLIENT_ID!,
      clientSecret: process.env.KAKAO_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      // Kakao의 id를 백엔드와 동기화
      const kakaoUserId = account?.providerAccountId;
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/auth/sync-kakao`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ kakaoUserId, email: user.email, nickname: user.name })
      });
      if (!res.ok) return false;
      const data = await res.json();
      // data.jwt를 세션에 저장하기 위해 임시 필드에 부착
      (user as any).backendJwt = data.jwt;
      (user as any).id = data.user.id;
      return true;
    },
    async jwt({ token, user }) {
      if (user) {
        token.backendJwt = (user as any).backendJwt;
        token.userId = (user as any).id;
      }
      return token;
    },
    async session({ session, token }) {
      (session as any).backendJwt = token.backendJwt;
      (session as any).userId = token.userId;
      return session;
    },
  },
  session: { strategy: 'jwt' },
};
```

```ts
// app/api/auth/[...nextauth]/route.ts
import NextAuth from 'next-auth';
import { authOptions } from '@/lib/auth';

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
```

프런트에서 API 호출 시:
```ts
// lib/api.ts
export async function api<T>(path: string, opt: RequestInit = {}) {
  const { getServerSession } = await import('next-auth');
  const session = await getServerSession();
  const headers: any = { 'Content-Type': 'application/json', ...(opt.headers||{}) };
  if (session?.backendJwt) headers['Authorization'] = `Bearer ${session.backendJwt}`;
  const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}${path}`, { ...opt, headers, cache: 'no-store' });
  if (!res.ok) throw new Error(await res.text());
  return res.json() as Promise<T>;
}
```

> 클라이언트 컴포넌트에서는 `useSession()`으로 `backendJwt`를 얻고 fetch 헤더에 삽입하거나, 서버 컴포넌트/서버액션에서는 위 `api()` 사용.

---

## 7. 페이지 & UX 플로우

### 7.1 랜딩 /(마케팅)
- 카카오 로그인 버튼, 서비스 소개, 약관/개인정보 링크
- 로그인 후 `/discover` 리다이렉트

### 7.2 프로필 편집 /profile/edit
- 필수: 닉네임, 성별, 출생연도
- 선택: 키, 지역, 직업, 자기소개, 사진(최대 6장)
- “이성에게 보이는 항목” 체크박스(가시성)
- 저장 시 `PUT /profile`

### 7.3 추천함 /discover
- 상단: 이번 주 배치(예: 2025-W37) 라벨
- 카드 리스트: `RecommendationItem[]`
- 각 카드: 프로필 요약, 사진 캐러셀, 공개 항목만 표시
- 버튼: **도전(좋아요)** / **패스**
- 좋아요 시 `POST /likes` → UI 뱃지 변경. 상호 매칭되면 `/matches`에 표시

### 7.4 매칭함 /matches
- 리스트: 매칭 상태 뱃지(`pending/active/closed`)
- 항목 클릭 → 상세 `/matches/[id]` (선택)
  - `pending`: 결제 안내 버튼 → `/payment/[matchId]`
  - `active`: 연락처/채팅 링크 표시(정책에 따라)

### 7.5 결제 안내 /payment/[matchId]
- 백엔드 `POST /payments/intent`로 코드·금액 수신
- 안내: 계좌번호, **입금자명은 ‘{code}’ 포함**
- 상태: `GET /payments/:id` 폴링(예: 10초)
- 입금 확인되면 **자동 이동** 또는 배너로 `/matches` 안내

### 7.6 관리자 /admin
- 탭: Users / Matches / Payments
- Payments: 미확인 → 확인(verify) 버튼 → `POST /admin/payments/:id/verify`
- Matches: 승인(activate) 버튼 → `POST /admin/matches/:id/activate`
- Actions: “주간 추천 생성” 버튼(임시) → `POST /admin/recs/run`
- 보호: 미들웨어로 관리자 권한 체크(백엔드 토큰 payload role)

---

## 8. 컴포넌트 설계(요지)

- `ProfileCard`
  - props: `{ data: RecommendationItem, onLike: (id)=>void, onPass: (id)=>void }`
  - 내부: 사진 슬라이더, 공개항목만 마스킹 해제

- `RecommendationList`
  - props: `{ items: RecommendationItem[] }`
  - 무한/페이지네이션(주간 단위이므로 페이지네이션 권장)

- `LikePassButtons`
  - 재사용 버튼 세트(로딩/에러 처리 포함)

- `PaymentInstructions`
  - props: `{ payment: Payment }`
  - 코드/금액/계좌/유의사항 렌더링

- `AdminTable`
  - 칼럼 정의 + 서버 정렬/필터 훅

---

## 9. 접근 제어 & 라우팅

- `middleware.ts`
  - 보호 라우트: `/profile/*`, `/discover`, `/matches/*`, `/payment/*`, `/admin/*`
  - 세션 없으면 `/`로 리다이렉트
  - `/admin/*`은 세션의 role 클레임 또는 `/me` 응답으로 검증(서버 측에서 401/403 시 홈으로)

---

## 10. 폼 & 유효성 검증

- `react-hook-form` + `zod`
- 예: 프로필 편집 `ProfileSchema`
```ts
export const ProfileSchema = z.object({
  nickname: z.string().min(2).max(20),
  gender: z.enum(['M','F']),
  birthYear: z.number().min(1950).max(new Date().getFullYear()-19),
  height: z.number().int().min(120).max(220).optional(),
  region: z.string().max(30).optional(),
  job: z.string().max(30).optional(),
  intro: z.string().max(500).optional(),
  photos: z.array(z.string().url()).max(6),
  visible: z.object({
    age: z.boolean(), height: z.boolean(), region: z.boolean(), job: z.boolean(), intro: z.boolean(),
  })
});
```

---

## 11. React Query 예시
```ts
// app/discover/page.tsx (서버 컴포넌트 + 클라 컴포 혼합 가능)
'use client';
import { useQuery, useMutation } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { RecommendationList } from '@/components/RecommendationList';

export default function DiscoverPage(){
  const { data: session } = useSession();
  const week = getIsoWeekLabel(new Date());

  const recs = useQuery({
    queryKey: ['recs', week],
    queryFn: async () => {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/recommendations?week=${week}`, {
        headers: { Authorization: `Bearer ${(session as any)?.backendJwt}` }
      });
      if(!res.ok) throw new Error('Failed');
      return res.json();
    }
  });

  const like = useMutation({
    mutationFn: async (toUserId: string) => fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/likes`, {
      method: 'POST', headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${(session as any)?.backendJwt}`
      }, body: JSON.stringify({ toUserId, batchWeek: week })
    })
  });

  return <RecommendationList items={recs.data||[]} />
}
```

---

## 12. 에러/로딩/빈 상태 UX
- 로딩 스켈레톤, 네트워크 오류 토스트, 빈 추천 시 안내(프로필/선호 업데이트 유도)
- 권한 부족 시 403 화면

---

## 13. 보안/개인정보 고려
- 최소한의 개인정보만 표시(가시성 옵션)
- 사진 경로는 서명 URL 또는 공개 CDN(워터마크 권장)
- 세션 탈취 방지: SameSite/Lax, HTTPS 강제, CSRF 보호(NextAuth 내장)
- 관리자 기능은 백엔드 권한 기반으로만 노출

---

## 14. 배포/설정 체크리스트
- Vercel 환경변수 등록(NEXTAUTH_SECRET, KAKAO_*, API_BASE_URL)
- 카카오 개발자 콘솔: Redirect URI/도메인 등록
- 도메인 HTTPS 적용
- robots/meta: 비공개 베타 시 noindex

---

## 15. 테스트 전략
- 단위: 폼 검증(zod), 유틸
- 통합: NextAuth 콜백 signIn → 백엔드 mock 서버로 JWT 수신 확인
- E2E: Playwright — 로그인 → 프로필 작성 → 추천 좋아요 → 결제 페이지 흐름

---

## 16. 관리자 기능 상세(요지)
- Users: 검색/정렬/정지(ban)
- Matches: 상태 필터, Activate 버튼(연락처 공개)
- Payments: 미확인→확인, 매칭과 연결된 결제 확인 가능
- Recs Run: 버튼 클릭 시 백엔드 배치 트리거(임시 운영)

---

## 17. 스프린트 계획(예시)
- **W1**: 프로젝트 셋업, NextAuth+Kakao, 레이아웃/네비, `/profile/edit`
- **W2**: `/discover` 추천 리스트, 좋아요/패스 API 연동, 빈/로딩 처리
- **W3**: `/matches`, `/payment/[matchId]` 폴링, 관리자 대시보드
- **W4**: 접근 제어/미들웨어, QA/E2E, 배포

---

## 18. AI Agent용 작업 목록 (Executable Checklist)
1. Next.js 14 TypeScript 템플릿 생성 및 Tailwind/shadcn 세팅
2. Auth.js Kakao Provider 설정 + 콜백에서 `/auth/sync-kakao` 호출 구현
3. `lib/api.ts`, `lib/types.ts`, `lib/validators.ts` 생성
4. 공통 레이아웃/네비게이션/보호 라우팅(middleware)
5. `/profile/edit`: 폼 + 업로드 UI(사진 URL 입력 또는 임시 더미)
6. `/discover`: 추천 리스트 + 좋아요/패스 액션
7. `/matches`: 목록/상세 + 상태 뱃지
8. `/payment/[matchId]`: intent 생성/폴링/완료 UI
9. `/admin`: Users/Matches/Payments 테이블 + 승인/활성화 액션
10. 에러/로딩/빈 상태 컴포넌트 구현
11. 환경변수/배포 스크립트 정리
12. Playwright 시나리오 1세트 작성

---

## 19. 후속(Phase 2) 제안
- 가상계좌/PG 연동으로 자동 입금확인
- 알림센터(이메일/SMS) + 카카오 비즈 채널 연동(승인 후)
- 추천 알고리즘 점수 고도화(노출균형/신규 가점/리뷰)

---

### 부록 A. Kakao 콘솔 체크
- 설정 > 보안: Client Secret 사용
- Redirect URI: `https://web.your-domain.com/api/auth/callback/kakao`
- 사용자 정보: id(필수), 닉네임/프로필이미지/이메일(동의 항목)

### 부록 B. UI 카피 초안
- 결제 안내: “매칭이 성사되었습니다. 아래 계좌로 **입금자명에 ‘{code}’를 포함**하여 입금해주세요. 확인되면 자동으로 활성화됩니다.”

---

이 문서대로 구현하면, 카카오톡으로 유입 → 웹으로 가입/로그인 → 주간 추천/좋아요 → 매칭 → 결제 → 관리자 승인까지의 MVP 플로우가 동작합니다.

