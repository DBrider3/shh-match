import { NextAuthOptions } from 'next-auth';
import KakaoProvider from 'next-auth/providers/kakao';
import type { User } from './types';

export const authOptions: NextAuthOptions = {
  providers: [
    KakaoProvider({
      clientId: process.env.KAKAO_CLIENT_ID!,
      clientSecret: process.env.KAKAO_CLIENT_SECRET!,
    }),
  ],
  callbacks: {
    async signIn({ user, account, profile }) {
      if (account?.provider === 'kakao') {
        try {
          // Kakao의 id를 백엔드와 동기화
          const kakaoUserId = account.providerAccountId;
          const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';
          
          const response = await fetch(`${API_BASE_URL}/auth/sync-kakao`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
              kakaoUserId, 
              email: user.email || undefined, 
              nickname: user.name || undefined 
            }),
          });
          
          if (!response.ok) {
            throw new Error('Failed to sync with backend');
          }
          
          const data: { jwt: string; user: User } = await response.json();
          
          // JWT를 세션에 저장하기 위해 user 객체에 부착
          (user as any).backendJwt = data.jwt;
          (user as any).id = data.user.id;
          
          return true;
        } catch (error) {
          console.error('Failed to sync with backend:', error);
          return false;
        }
      }
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
      session.backendJwt = token.backendJwt;
      session.userId = token.userId;
      return session;
    },
  },
  session: {
    strategy: 'jwt',
  },
  pages: {
    signIn: '/',
    error: '/auth/error',
  },
};