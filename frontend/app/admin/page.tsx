'use client';

import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Users, Heart, CreditCard } from 'lucide-react';

export default function AdminDashboardPage() {
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
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            관리자 대시보드
          </h1>
          <p className="text-gray-600">
            시스템 현황을 확인하고 관리 작업을 수행하세요.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>사용자 관리</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600">
                등록된 사용자를 확인하고 프로필을 관리하세요.
              </p>
              <Link href="/admin/users">
                <Button>
                  <Users className="h-4 w-4 mr-2" />
                  사용자 관리
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>매칭 관리</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600">
                매칭 현황을 확인하고 활성화 작업을 수행하세요.
              </p>
              <Link href="/admin/matches">
                <Button>
                  <Heart className="h-4 w-4 mr-2" />
                  매칭 관리
                </Button>
              </Link>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>결제 관리</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600">
                입금 확인이 필요한 결제를 처리하세요.
              </p>
              <Link href="/admin/payments">
                <Button>
                  <CreditCard className="h-4 w-4 mr-2" />
                  결제 관리
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}