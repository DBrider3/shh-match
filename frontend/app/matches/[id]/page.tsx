'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

export default function MatchDetailPage() {
  const params = useParams();
  const { data: session } = useSession();
  const matchId = params.id as string;

  if (!session) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">
          <p>로그인이 필요합니다.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-6">
          <Link href="/matches" className="inline-flex items-center text-gray-600 hover:text-gray-900 mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            매칭함으로 돌아가기
          </Link>
          
          <h1 className="text-2xl font-bold text-gray-900">
            매칭 상세
          </h1>
          <p className="text-gray-600 mt-1">
            매칭 ID: {matchId}
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>매칭 정보</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600">
              매칭 상세 기능은 백엔드 API 완성 후 구현됩니다.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}