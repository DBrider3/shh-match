'use client';

import { useSession } from 'next-auth/react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

export default function ProfileEditPage() {
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
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardHeader>
            <CardTitle>프로필 편집</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="nickname">닉네임</Label>
                <Input
                  id="nickname"
                  placeholder="표시될 닉네임을 입력하세요"
                />
              </div>

              <div>
                <Label>성별</Label>
                <div className="flex space-x-4 mt-2">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="gender"
                      value="M"
                      className="mr-2"
                    />
                    남성
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      name="gender"
                      value="F"
                      className="mr-2"
                    />
                    여성
                  </label>
                </div>
              </div>

              <div>
                <Label htmlFor="birthYear">출생연도</Label>
                <Input
                  id="birthYear"
                  type="number"
                  placeholder="예: 1995"
                />
              </div>

              <div>
                <Label htmlFor="region">지역</Label>
                <Input
                  id="region"
                  placeholder="예: 서울 강남구"
                />
              </div>

              <Button className="w-full">
                프로필 저장 (백엔드 API 연동 후 동작)
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}