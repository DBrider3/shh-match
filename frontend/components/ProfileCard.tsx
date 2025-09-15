'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Heart, X, ChevronLeft, ChevronRight } from 'lucide-react';
import type { RecommendationItem } from '@/lib/types';

interface ProfileCardProps {
  data: RecommendationItem;
  onLike: (userId: string) => void;
  onPass: (userId: string) => void;
  isLoading?: boolean;
}

export function ProfileCard({ data, onLike, onPass, isLoading }: ProfileCardProps) {
  const [currentPhotoIndex, setCurrentPhotoIndex] = useState(0);
  const { profile } = data;
  const photos = profile.photos.length > 0 ? profile.photos : ['/placeholder-profile.png'];

  const nextPhoto = () => {
    setCurrentPhotoIndex((prev) => (prev + 1) % photos.length);
  };

  const prevPhoto = () => {
    setCurrentPhotoIndex((prev) => (prev - 1 + photos.length) % photos.length);
  };

  const currentAge = new Date().getFullYear() - profile.birthYear;

  return (
    <Card className="max-w-sm mx-auto overflow-hidden">
      {/* 사진 슬라이더 */}
      <div className="relative h-80 bg-gray-200">
        <Image
          src={photos[currentPhotoIndex]}
          alt={`${profile.nickname}의 사진`}
          fill
          className="object-cover"
          onError={(e) => {
            (e.target as HTMLImageElement).src = '/placeholder-profile.png';
          }}
        />
        
        {/* 사진 네비게이션 */}
        {photos.length > 1 && (
          <>
            <Button
              variant="ghost"
              size="sm"
              className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black/50 text-white hover:bg-black/70"
              onClick={prevPhoto}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black/50 text-white hover:bg-black/70"
              onClick={nextPhoto}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </>
        )}
        
        {/* 사진 인디케이터 */}
        {photos.length > 1 && (
          <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-1">
            {photos.map((_, index) => (
              <div
                key={index}
                className={`w-2 h-2 rounded-full ${
                  index === currentPhotoIndex ? 'bg-white' : 'bg-white/50'
                }`}
              />
            ))}
          </div>
        )}
      </div>

      <CardContent className="p-4">
        {/* 기본 정보 */}
        <div className="mb-4">
          <h3 className="text-xl font-bold text-gray-900">
            {profile.nickname}
            {profile.visible.age && (
              <span className="text-gray-600 font-normal ml-2">{currentAge}세</span>
            )}
          </h3>
          
          <div className="space-y-1 text-sm text-gray-600 mt-2">
            {profile.visible.height && profile.height && (
              <p>키: {profile.height}cm</p>
            )}
            
            {profile.visible.region && profile.region && (
              <p>지역: {profile.region}</p>
            )}
            
            {profile.visible.job && profile.job && (
              <p>직업: {profile.job}</p>
            )}
          </div>
        </div>

        {/* 자기소개 */}
        {profile.visible.intro && profile.intro && (
          <div className="mb-4">
            <p className="text-sm text-gray-700 leading-relaxed">
              {profile.intro}
            </p>
          </div>
        )}

        {/* 액션 버튼 */}
        <div className="flex space-x-3 mt-6">
          <Button
            variant="outline"
            size="lg"
            className="flex-1 border-gray-300 hover:bg-gray-50"
            onClick={() => onPass(data.targetUserId)}
            disabled={isLoading}
          >
            <X className="h-5 w-5 mr-2" />
            패스
          </Button>
          
          <Button
            size="lg"
            className="flex-1 bg-pink-500 hover:bg-pink-600"
            onClick={() => onLike(data.targetUserId)}
            disabled={isLoading}
          >
            <Heart className="h-5 w-5 mr-2" />
            도전
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}