'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useSession } from 'next-auth/react';
import { RecommendationList } from '@/components/RecommendationList';
import { CozySpinner } from '@/components/ui/sohaeng-components';
import { Card, CardContent, CardHeader, CardTitle, CozyCard } from '@/components/ui/card';
import { apiClientSide, getIsoWeekLabel } from '@/lib/api';
import type { RecommendationItem, LikePayload } from '@/lib/types';

export default function DiscoverPage() {
  const { data: session } = useSession();
  const queryClient = useQueryClient();
  const currentWeek = getIsoWeekLabel(new Date());

  // 소확행 주제에 맞는 Mock data
  const mockRecommendations: RecommendationItem[] = [
    {
      targetUserId: 'user1',
      batchWeek: currentWeek,
      profile: {
        nickname: '커피러버 민지',
        gender: 'F',
        birthYear: 1996,
        height: 165,
        region: '서울 강남구',
        job: '카페 매니저',
        photos: ['https://via.placeholder.com/300x400'],
        intro: '소확행을 추구하며 일상의 작은 행복을 찾아가는 중입니다 ☕ 커피와 책, 그리고 따뜻한 대화를 좋아해요',
        visible: {
          age: true,
          height: true,
          region: true,
          job: true,
          intro: true,
        }
      }
    },
    {
      targetUserId: 'user2',
      batchWeek: currentWeek,
      profile: {
        nickname: '책방지기 준호',
        gender: 'M',
        birthYear: 1993,
        height: 178,
        region: '서울 마포구',
        job: '독립 서점 운영',
        photos: ['https://via.placeholder.com/300x400'],
        intro: '조용한 카페에서 책 읽는 시간이 가장 행복해요 📚 좋은 책과 맛있는 커피를 나누고 싶어요',
        visible: {
          age: true,
          height: true,
          region: true,
          job: true,
          intro: true,
        }
      }
    }
  ];

  // 추천 리스트 가져오기 (현재는 Mock 데이터 사용)
  const { data: recommendations = mockRecommendations, isLoading, error } = useQuery({
    queryKey: ['recommendations', currentWeek],
    queryFn: async () => {
      // 백엔드 API가 준비되면 실제 API 호출로 변경
      return mockRecommendations;
    },
    enabled: !!session,
  });

  // 좋아요 보내기 mutation
  const likeMutation = useMutation({
    mutationFn: async (payload: LikePayload) => {
      // 백엔드 API가 준비되면 실제 API 호출로 변경
      console.log('Like sent:', payload);
      return { ok: true };
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['matches'] });
    },
    onError: (error) => {
      console.error('Like error:', error);
      alert('좋아요 전송에 실패했습니다.');
    },
  });

  const handleLike = (toUserId: string) => {
    likeMutation.mutate({
      toUserId,
      batchWeek: currentWeek,
    });
  };

  const handlePass = (userId: string) => {
    console.log('Passed user:', userId);
  };

  if (!session) {
    return (
      <div className="min-h-screen bg-sohaeng-gradient flex items-center justify-center">
        <CozyCard className="text-center max-w-md">
          <div className="text-6xl mb-4">☕</div>
          <h2 className="text-xl font-semibold text-coffee mb-2">
            소확행에 오신 걸 환영해요!
          </h2>
          <p className="text-warm-coffee">
            따뜻한 만남을 위해 로그인이 필요합니다.
          </p>
        </CozyCard>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-sohaeng-gradient flex items-center justify-center">
        <div className="text-center">
          <CozySpinner className="mb-4" />
          <h2 className="text-xl font-semibold text-coffee mb-2">
            당신을 위한 특별한 만남을 찾고 있어요
          </h2>
          <p className="text-warm-coffee">
            커피 한 잔의 여유로 기다려주세요... ☕
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-sohaeng-gradient">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* 따뜻한 헤더 */}
          <div className="text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-warm-brown rounded-full shadow-warm mb-4">
              <span className="text-2xl text-white">☕</span>
            </div>
            <h1 className="text-3xl font-bold text-coffee mb-2 font-cozy">
              오늘의 소확행 만남
            </h1>
            <p className="text-warm-coffee mb-2">
              {currentWeek} · {recommendations.length}명의 따뜻한 만남이 기다리고 있어요
            </p>
            <div className="inline-flex items-center gap-1 text-sm text-warm-coffee/70">
              <span>🌿</span>
              <span>소소하지만 확실한 행복을 찾아보세요</span>
            </div>
          </div>

          {/* 추천 리스트 */}
          <RecommendationList
            items={recommendations}
            onLike={handleLike}
            onPass={handlePass}
            isLoading={likeMutation.isPending}
          />

          {/* 안내 메시지 */}
          {recommendations.length > 0 && (
            <CozyCard className="mt-8 text-center">
              <div className="text-4xl mb-3">💕</div>
              <h3 className="font-semibold text-coffee mb-2">
                매칭이 성사되는 방법
              </h3>
              <p className="text-sm text-warm-coffee leading-relaxed">
                매주 월요일마다 새로운 추천 리스트가 업데이트됩니다.
                <br />
                서로 관심을 표현하면 매칭이 성사되고,
                <br />
                커피 한 잔과 함께 따뜻한 대화를 시작할 수 있어요 ☕
              </p>
            </CozyCard>
          )}

          {/* 오늘의 소확행 팁 */}
          <div className="mt-8">
            <Card className="bg-warm-cream/50">
              <CardHeader>
                <CardTitle className="text-center text-coffee">
                  💡 오늘의 소확행 대화 팁
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-4 text-sm">
                  <div className="text-center p-4 bg-white/50 rounded-xl">
                    <span className="text-2xl mb-2 block">☕</span>
                    <p className="text-warm-coffee">
                      "어떤 커피를 좋아하세요?"<br />
                      같은 간단한 질문으로 시작해보세요
                    </p>
                  </div>
                  <div className="text-center p-4 bg-white/50 rounded-xl">
                    <span className="text-2xl mb-2 block">🌱</span>
                    <p className="text-warm-coffee">
                      "일상에서 작은 행복을 어디서 찾으세요?"<br />
                      소확행에 대해 이야기해보세요
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}