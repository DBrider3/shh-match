import Link from 'next/link';

export function Footer() {
  return (
    <footer className="bg-gray-50 border-t mt-auto">
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* 서비스 정보 */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">
              매칭사이트
            </h3>
            <p className="text-sm text-gray-600 mb-4">
              카카오 로그인으로 시작하는 안전한 매칭 서비스
            </p>
            <p className="text-xs text-gray-500">
              © 2024 매칭사이트. All rights reserved.
            </p>
          </div>

          {/* 이용 안내 */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">
              이용 안내
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                <Link href="/terms" className="hover:text-gray-900 transition-colors">
                  이용약관
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="hover:text-gray-900 transition-colors">
                  개인정보처리방침
                </Link>
              </li>
              <li>
                <Link href="/safety" className="hover:text-gray-900 transition-colors">
                  안전 가이드
                </Link>
              </li>
              <li>
                <Link href="/faq" className="hover:text-gray-900 transition-colors">
                  자주묻는질문
                </Link>
              </li>
            </ul>
          </div>

          {/* 고객 지원 */}
          <div>
            <h3 className="text-sm font-semibold text-gray-900 mb-4">
              고객 지원
            </h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>
                <Link href="/contact" className="hover:text-gray-900 transition-colors">
                  문의하기
                </Link>
              </li>
              <li>
                <span className="text-gray-500">운영시간: 평일 09:00 - 18:00</span>
              </li>
              <li>
                <span className="text-gray-500">이메일: support@matching.com</span>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            건전한 만남을 위해 불법적이거나 부적절한 행위는 엄격히 금지됩니다.
          </p>
        </div>
      </div>
    </footer>
  );
}