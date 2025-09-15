import { withAuth } from 'next-auth/middleware';
import { NextResponse } from 'next/server';

export default withAuth(
  function middleware(req) {
    const token = req.nextauth.token;
    const isAuth = !!token;
    const isAuthPage = req.nextUrl.pathname.startsWith('/auth');
    const isProtectedPage = 
      req.nextUrl.pathname.startsWith('/profile') ||
      req.nextUrl.pathname.startsWith('/discover') ||
      req.nextUrl.pathname.startsWith('/matches') ||
      req.nextUrl.pathname.startsWith('/payment') ||
      req.nextUrl.pathname.startsWith('/admin');
    
    // 인증이 필요한 페이지인데 로그인하지 않은 경우
    if (isProtectedPage && !isAuth) {
      return NextResponse.redirect(new URL('/', req.url));
    }
    
    // 이미 로그인한 상태에서 인증 페이지 접근 시 홈으로 리다이렉트
    if (isAuthPage && isAuth) {
      return NextResponse.redirect(new URL('/discover', req.url));
    }
    
    // 관리자 페이지는 추가 권한 체크 (여기서는 기본 인증만)
    if (req.nextUrl.pathname.startsWith('/admin') && isAuth) {
      // 실제 구현에서는 백엔드에서 role을 체크해야 함
      // 현재는 모든 로그인 사용자가 접근 가능
    }
    
    return NextResponse.next();
  },
  {
    callbacks: {
      authorized: () => true, // 미들웨어 함수에서 직접 처리
    },
  }
);

export const config = {
  matcher: [
    '/profile/:path*',
    '/discover/:path*', 
    '/matches/:path*',
    '/payment/:path*',
    '/admin/:path*',
    '/auth/:path*'
  ]
};