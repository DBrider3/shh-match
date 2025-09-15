'use client';

import Link from 'next/link';
import { useSession, signOut } from 'next-auth/react';
import { Button } from '@/components/ui/button';
import { Heart, Users, User, Settings, LogOut } from 'lucide-react';

export function Navbar() {
  const { data: session, status } = useSession();

  if (status === 'loading') {
    return (
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/" className="text-xl font-bold text-primary">
                💕 매칭사이트
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <div className="h-8 w-20 bg-gray-200 animate-pulse rounded"></div>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  if (!session) {
    return (
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/" className="text-xl font-bold text-primary">
                💕 매칭사이트
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/auth/signin">
                <Button variant="outline">로그인</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>
    );
  }

  return (
    <nav className="bg-white shadow-sm border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center space-x-8">
            <Link href="/" className="text-xl font-bold text-primary">
              💕 매칭사이트
            </Link>
            
            {/* 메인 네비게이션 */}
            <div className="hidden md:flex space-x-6">
              <Link 
                href="/discover" 
                className="text-gray-600 hover:text-primary transition-colors flex items-center space-x-1"
              >
                <Heart className="h-4 w-4" />
                <span>추천함</span>
              </Link>
              
              <Link 
                href="/matches" 
                className="text-gray-600 hover:text-primary transition-colors flex items-center space-x-1"
              >
                <Users className="h-4 w-4" />
                <span>매칭함</span>
              </Link>
              
              <Link 
                href="/profile/edit" 
                className="text-gray-600 hover:text-primary transition-colors flex items-center space-x-1"
              >
                <User className="h-4 w-4" />
                <span>프로필</span>
              </Link>
            </div>
          </div>

          {/* 사용자 메뉴 */}
          <div className="flex items-center space-x-4">
            <span className="text-sm text-gray-600">
              안녕하세요, {session.user?.name || '사용자'}님
            </span>
            
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => signOut({ callbackUrl: '/' })}
              className="flex items-center space-x-1"
            >
              <LogOut className="h-4 w-4" />
              <span>로그아웃</span>
            </Button>
          </div>
        </div>
      </div>
      
      {/* 모바일 네비게이션 */}
      <div className="md:hidden border-t bg-gray-50">
        <div className="flex justify-around py-2">
          <Link 
            href="/discover" 
            className="text-gray-600 hover:text-primary transition-colors flex flex-col items-center space-y-1 p-2"
          >
            <Heart className="h-5 w-5" />
            <span className="text-xs">추천함</span>
          </Link>
          
          <Link 
            href="/matches" 
            className="text-gray-600 hover:text-primary transition-colors flex flex-col items-center space-y-1 p-2"
          >
            <Users className="h-5 w-5" />
            <span className="text-xs">매칭함</span>
          </Link>
          
          <Link 
            href="/profile/edit" 
            className="text-gray-600 hover:text-primary transition-colors flex flex-col items-center space-y-1 p-2"
          >
            <User className="h-5 w-5" />
            <span className="text-xs">프로필</span>
          </Link>
        </div>
      </div>
    </nav>
  );
}