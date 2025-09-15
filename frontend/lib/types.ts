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
    age: boolean; 
    height: boolean; 
    region: boolean; 
    job: boolean; 
    intro: boolean;
  }
}

export interface Preferences {
  userId: string;
  targetGender: Gender;
  ageMin: number; 
  ageMax: number;
  regions: string[];
  keywords: string[];
  blocks: string[]; // userIds
}

export interface RecommendationItem {
  targetUserId: string;
  profile: Pick<Profile, 'nickname'|'gender'|'birthYear'|'height'|'region'|'job'|'photos'|'intro'|'visible'>;
  batchWeek: string; // e.g., 2025-W37
}

export interface LikePayload { 
  toUserId: string; 
  batchWeek: string; 
}

export interface Match {
  id: string; 
  userA: string; 
  userB: string;
  createdAt: string; 
  status: 'pending'|'active'|'closed';
}

export interface Payment {
  id: string; 
  matchId: string; 
  method: 'transfer'; 
  amount: number; 
  code: string; 
  depositorName?: string;
  verifiedAt?: string; 
  memo?: string;
}

// NextAuth 확장 타입
declare module "next-auth" {
  interface Session {
    backendJwt?: string;
    userId?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    backendJwt?: string;
    userId?: string;
  }
}