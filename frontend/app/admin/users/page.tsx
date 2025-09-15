'use client';

import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

export default function AdminUsersPage() {
  const { data: session } = useSession();

  if (!session) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">관리자 로그인 필요</h1>
          <p className="text-gray-600">관리자 권한이 필요한 페이지입니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <Link 
            href="/admin" 
            className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            대시보드로 돌아가기
          </Link>
          
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            사용자 관리
          </h1>
          <p className="text-gray-600">
            등록된 사용자를 확인하고 관리하세요.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>사용자 리스트</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600">
              사용자 관리 기능은 백엔드 API 완성 후 구현됩니다.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}