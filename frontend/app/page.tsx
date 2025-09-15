'use client';

import { useSession, signIn } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { Button } from '@/components/ui/button';

export default function HomePage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  useEffect(() => {
    // 이미 로그인한 사용자는 추천 페이지로 리다이렉트
    if (session) {
      router.push('/discover');
    }
  }, [session, router]);

  if (status === 'loading') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (session) {
    return null; // 리다이렉트 중
  }

  return (
    <div className="min-h-screen bg-sohaeng-gradient">
      {/* Hero Section */}
      <section className="container mx-auto px-4 py-16 sm:py-24">
        <div className="text-center">
          {/* 로고 영역 */}
          <div className="mb-8 animate-gentle-bounce">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-warm-brown rounded-full shadow-warm mb-4">
              <span className="text-3xl text-white">☕</span>
            </div>
            <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-coffee mb-2 font-cozy">
              소확행<span className="text-warm-pink">♥</span>
            </h1>
            <p className="text-lg text-warm-brown font-medium">
              소소하지만 확실한, 행복한 만남<span className="text-warm-pink">♥</span>
            </p>
          </div>

          {/* 메인 메시지 */}
          <div className="max-w-3xl mx-auto mb-12">
            <h2 className="text-2xl sm:text-3xl font-semibold text-coffee mb-6 leading-relaxed">
              커피 한 잔의 여유로 시작하는
              <br className="hidden sm:block" />
              <span className="text-warm-brown">따뜻한 만남</span>
            </h2>

            <p className="text-lg text-warm-coffee mb-8 leading-relaxed">
              바쁜 일상 속에서 잠시 멈춰 서서 마시는 커피 한 잔처럼,
              <br />
              소소하지만 확실한 행복을 느낄 수 있는 따뜻한 만남을 만들어보세요.
            </p>

            {/* 매칭 시작 버튼 */}
            <Button
              size="lg"
              className="bg-coffee-gradient hover:shadow-warm text-white text-xl px-10 py-6 rounded-xl transition-all duration-300 shadow-lg hover:scale-105 font-medium"
              onClick={() => signIn('kakao', { callbackUrl: '/discover' })}
            >
              ☕ 커피 한 잔과 함께 시작하기 ♥
            </Button>

            <p className="text-sm text-warm-coffee/70 mt-6 leading-relaxed">
              가입하면 <a href="/terms" className="underline hover:text-warm-brown transition-colors">이용약관</a>과{' '}
              <a href="/privacy" className="underline hover:text-warm-brown transition-colors">개인정보처리방침</a>에 동의한 것으로 간주됩니다.
            </p>
          </div>
        </div>
      </section>

      {/* 소확행 가치 소개 섹션 */}
      <section className="py-16 bg-cream/50">
        <div className="container mx-auto px-4">
          <h3 className="text-3xl font-bold text-center text-coffee mb-12">
            소확행이 추구하는 가치
          </h3>

          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            {/* 카드 1: 소소한 행복 */}
            <div className="bg-white/80 p-8 rounded-2xl shadow-cozy text-center hover:shadow-warm transition-all duration-300">
              <div className="w-16 h-16 bg-warm-orange rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🌿</span>
              </div>
              <h4 className="text-xl font-semibold text-coffee mb-3">소소한 행복</h4>
              <p className="text-warm-coffee leading-relaxed">
                일상에서 찾을 수 있는<br />
                작은 기쁨과 소소한 행복
              </p>
            </div>

            {/* 카드 2: 따뜻한 만남 */}
            <div className="bg-white/80 p-8 rounded-2xl shadow-cozy text-center hover:shadow-warm transition-all duration-300">
              <div className="w-16 h-16 bg-warm-pink rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">☕</span>
              </div>
              <h4 className="text-xl font-semibold text-coffee mb-3">따뜻한 만남</h4>
              <p className="text-warm-coffee leading-relaxed">
                커피 한 잔의 여유로<br />
                시작하는 편안한 대화
              </p>
            </div>

            {/* 카드 3: 진정성 */}
            <div className="bg-white/80 p-8 rounded-2xl shadow-cozy text-center hover:shadow-warm transition-all duration-300">
              <div className="w-16 h-16 bg-warm-brown rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl text-white">♥</span>
              </div>
              <h4 className="text-xl font-semibold text-coffee mb-3">진정성</h4>
              <p className="text-warm-coffee leading-relaxed">
                시간을 두고 천천히<br />
                알아가는 진심 어린 관계
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 바닥 CTA */}
      <section className="py-20 bg-warm-brown/5">
        <div className="container mx-auto px-4 text-center">
          <h3 className="text-2xl font-semibold text-coffee mb-4">
            오늘도 소소하지만 확실한 행복을 찾아보세요
          </h3>
          <p className="text-warm-coffee mb-8">
            당신의 일상에 작은 행복을 더하는 소확행과 함께하세요
          </p>

          <Button
            size="lg"
            variant="outline"
            className="border-warm-brown text-warm-brown hover:bg-warm-brown hover:text-white px-8 py-4 text-lg transition-all duration-300"
            onClick={() => signIn('kakao', { callbackUrl: '/discover' })}
          >
            지금 시작하기 →
          </Button>
        </div>
      </section>
    </div>
  );
}