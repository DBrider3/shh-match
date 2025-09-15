import { AlertCircle, RefreshCw, Home } from 'lucide-react';
import { Button } from './button';
import { cn } from '@/lib/utils';

interface ErrorStateProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  onGoHome?: () => void;
  showHome?: boolean;
  className?: string;
}

export function ErrorState({
  title = '오류가 발생했습니다',
  message = '일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.',
  onRetry,
  onGoHome,
  showHome = true,
  className
}: ErrorStateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center py-12 px-4', className)}>
      <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
        <AlertCircle className="h-8 w-8 text-red-600" />
      </div>
      
      <h3 className="text-lg font-semibold text-gray-900 mb-2 text-center">
        {title}
      </h3>
      
      <p className="text-gray-600 text-center max-w-md mb-6">
        {message}
      </p>
      
      <div className="flex space-x-3">
        {onRetry && (
          <Button onClick={onRetry} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            다시 시도
          </Button>
        )}
        
        {showHome && (
          <Button 
            onClick={onGoHome || (() => window.location.href = '/')}
          >
            <Home className="h-4 w-4 mr-2" />
            홈으로 이동
          </Button>
        )}
      </div>
    </div>
  );
}

export function ErrorPage({
  title = '페이지를 찾을 수 없습니다',
  message = '요청하신 페이지가 존재하지 않거나 접근 권한이 없습니다.',
  ...props
}: ErrorStateProps) {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <ErrorState 
        title={title}
        message={message}
        {...props}
      />
    </div>
  );
}