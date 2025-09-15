'use client';

import Link from 'next/link';
import { useSession } from 'next-auth/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Heart } from 'lucide-react';

export default function MatchesPage() {
  const { data: session } = useSession();

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
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            매칭함
          </h1>
          <p className="text-gray-600">
            성사된 매칭을 확인하고 관리하세요.
          </p>
        </div>

        <div className="text-center py-16">
          <div className="mb-4">
            <div className="w-24 h-24 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
              <Heart className="h-12 w-12 text-gray-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              아직 매칭이 없습니다
            </h3>
            <p className="text-gray-600 max-w-md mx-auto mb-6">
              추천함에서 마음에 드는 분께 도전해보세요.
              상호 관심을 표현하면 매칭이 성사됩니다.
            </p>
            <Link href="/discover">
              <Button>
                <Heart className="h-4 w-4 mr-2" />
                추천함 보기
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}