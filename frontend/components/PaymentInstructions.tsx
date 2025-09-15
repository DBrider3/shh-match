'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import type { Payment } from '@/lib/types';
import { Copy, CheckCircle, Clock, RefreshCw } from 'lucide-react';

interface PaymentInstructionsProps {
  payment: Payment;
  onRefresh: () => void;
  isRefreshing?: boolean;
}

export function PaymentInstructions({ 
  payment, 
  onRefresh, 
  isRefreshing 
}: PaymentInstructionsProps) {
  const [copied, setCopied] = useState<string | null>(null);
  const [timeLeft, setTimeLeft] = useState<string>('');

  useEffect(() => {
    const updateTimer = () => {
      const now = new Date();
      const created = new Date(payment.id);
      const expiry = new Date(created.getTime() + 60 * 60 * 1000);
      
      if (now >= expiry) {
        setTimeLeft('만료됨');
        return;
      }
      
      const diff = expiry.getTime() - now.getTime();
      const minutes = Math.floor(diff / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);
      
      setTimeLeft(`${minutes}분 ${seconds}초`);
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);
    
    return () => clearInterval(interval);
  }, [payment.id]);

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(type);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error('복사 실패:', err);
    }
  };

  const getStatusBadge = () => {
    if (payment.verifiedAt) {
      return (
        <Badge className="bg-green-100 text-green-800">
          <CheckCircle className="h-3 w-3 mr-1" />
          입금 확인됨
        </Badge>
      );
    }
    
    return (
      <Badge className="bg-yellow-100 text-yellow-800">
        <Clock className="h-3 w-3 mr-1" />
        입금 대기 중
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>결제 상태</CardTitle>
            {getStatusBadge()}
          </div>
        </CardHeader>
        <CardContent>
          {payment.verifiedAt ? (
            <div className="text-center py-4">
              <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-green-900 mb-2">
                입금이 확인되었습니다!
              </h3>
              <p className="text-gray-600">
                관리자 승인 후 매칭이 활성화됩니다.
                잠시만 기다려주세요.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">결제 금액</span>
                <span className="text-xl font-bold text-blue-600">
                  {payment.amount.toLocaleString()}원
                </span>
              </div>
              
              {timeLeft && timeLeft !== '만료됨' && (
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">남은 시간</span>
                  <span className="text-orange-600 font-semibold">
                    {timeLeft}
                  </span>
                </div>
              )}
              
              <Button 
                onClick={onRefresh}
                disabled={isRefreshing}
                variant="outline"
                size="sm"
                className="w-full"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
                {isRefreshing ? '확인 중...' : '입금 확인하기'}
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {!payment.verifiedAt && (
        <Card>
          <CardHeader>
            <CardTitle>계좌이체 안내</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-semibold text-gray-700">
                  입금 계좌
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard('123-456-789012', 'account')}
                >
                  <Copy className="h-4 w-4 mr-1" />
                  {copied === 'account' ? '복사됨!' : '복사'}
                </Button>
              </div>
              <p className="text-lg font-mono">123-456-789012</p>
              <p className="text-sm text-gray-600">국민은행</p>
            </div>

            <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-semibold text-yellow-800">
                  입금자명 (중요)
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(payment.code, 'code')}
                >
                  <Copy className="h-4 w-4 mr-1" />
                  {copied === 'code' ? '복사됨!' : '복사'}
                </Button>
              </div>
              <p className="text-lg font-mono font-bold text-yellow-900">
                {payment.code}
              </p>
              <p className="text-sm text-yellow-700 mt-2">
                입금자명에 위 코드를 정확히 입력해주세요.
                코드가 일치하지 않으면 입금 확인이 지연될 수 있습니다.
              </p>
            </div>

            <div className="space-y-2 text-sm text-gray-600">
              <h4 className="font-semibold text-gray-900">입금 시 주의사항</h4>
              <ul className="space-y-1 ml-4">
                <li>• 정확한 금액({payment.amount.toLocaleString()}원)을 입금해주세요</li>
                <li>• 입금자명에 제공된 코드를 반드시 포함해주세요</li>
                <li>• 입금 후 자동으로 확인되며, 최대 5분 정도 소요됩니다</li>
                <li>• 문제 발생 시 고객센터로 연락해주세요</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">환불 정책</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-xs text-gray-600 space-y-1">
            <p>• 상호 매칭 성사 후 일방적 취소 시 환불이 제한됩니다</p>
            <p>• 시스템 오류나 서비스 문제로 인한 경우 전액 환불됩니다</p>
            <p>• 환불 문의는 고객센터를 통해 처리됩니다</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}