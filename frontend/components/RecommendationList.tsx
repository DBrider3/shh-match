'use client';

import { useState } from 'react';
import { ProfileCard } from './ProfileCard';
import type { RecommendationItem } from '@/lib/types';

interface RecommendationListProps {
  items: RecommendationItem[];
  onLike: (userId: string) => void;
  onPass: (userId: string) => void;
  isLoading?: boolean;
}

export function RecommendationList({ 
  items, 
  onLike, 
  onPass, 
  isLoading 
}: RecommendationListProps) {
  const [currentIndex, setCurrentIndex] = useState(0);

  const handleLike = (userId: string) => {
    onLike(userId);
    nextCard();
  };

  const handlePass = (userId: string) => {
    onPass(userId);
    nextCard();
  };

  const nextCard = () => {
    if (currentIndex < items.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  if (items.length === 0) {
    return (
      <div className="text-center py-16">
        <div className="mb-4">
          <div className="w-24 h-24 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
            💕
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            이번 주 추천이 없습니다
          </h3>
          <p className="text-gray-600 max-w-md mx-auto">
            프로필을 더 자세히 작성하거나 선호 설정을 조정해보세요.
            다음 주에 새로운 추천을 받아보실 수 있습니다.
          </p>
        </div>
      </div>
    );
  }

  if (currentIndex >= items.length) {
    return (
      <div className="text-center py-16">
        <div className="mb-4">
          <div className="w-24 h-24 bg-primary/10 rounded-full mx-auto mb-4 flex items-center justify-center">
            ✨
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            이번 주 추천을 모두 확인했습니다!
          </h3>
          <p className="text-gray-600 max-w-md mx-auto">
            다음 주 월요일에 새로운 추천 리스트가 업데이트됩니다.
            매칭 결과는 매칭함에서 확인해보세요.
          </p>
        </div>
      </div>
    );
  }

  const currentItem = items[currentIndex];

  return (
    <div className="space-y-6">
      {/* 진행 상황 */}
      <div className="max-w-sm mx-auto">
        <div className="flex justify-between text-sm text-gray-600 mb-2">
          <span>{currentIndex + 1} / {items.length}</span>
          <span>이번 주 추천</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-primary rounded-full h-2 transition-all duration-300"
            style={{ width: `${((currentIndex + 1) / items.length) * 100}%` }}
          />
        </div>
      </div>

      {/* 현재 카드 */}
      <ProfileCard
        data={currentItem}
        onLike={handleLike}
        onPass={handlePass}
        isLoading={isLoading}
      />

      {/* 키보드 안내 */}
      <div className="text-center text-sm text-gray-500">
        <p>스와이프하거나 버튼을 눌러 선택하세요</p>
      </div>
    </div>
  );
}