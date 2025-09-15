import { getServerSession } from 'next-auth';
import { authOptions } from './auth';
import type { 
  User, 
  Profile, 
  Preferences, 
  RecommendationItem, 
  Match, 
  Payment, 
  LikePayload 
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

export async function apiServerSide<T>(path: string, options: RequestInit = {}): Promise<T> {
  const session = await getServerSession(authOptions);
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (session?.backendJwt) {
    headers['Authorization'] = `Bearer ${session.backendJwt}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
    cache: 'no-store',
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(response.status, errorText);
  }

  return response.json();
}

export async function apiClientSide<T>(path: string, options: RequestInit = {}, token?: string): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new ApiError(response.status, errorText);
  }

  return response.json();
}

// Auth API
export const authApi = {
  syncKakao: async (kakaoUserId: string, email?: string, nickname?: string) => {
    return apiClientSide<{ jwt: string; user: User }>('/auth/sync-kakao', {
      method: 'POST',
      body: JSON.stringify({ kakaoUserId, email, nickname }),
    });
  },
};

// User API (Server-side)
export const userApi = {
  getMe: async () => {
    return apiServerSide<{ user: User; profile?: Profile; preferences?: Preferences }>('/me');
  },
  
  updateProfile: async (profile: Partial<Profile>) => {
    return apiServerSide<Profile>('/profile', {
      method: 'PUT',
      body: JSON.stringify(profile),
    });
  },
  
  updatePreferences: async (preferences: Partial<Preferences>) => {
    return apiServerSide<Preferences>('/preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  },
};

// Recommendations API
export const recommendationsApi = {
  getRecommendations: async (week: string, token?: string) => {
    if (token) {
      return apiClientSide<RecommendationItem[]>(`/recommendations?week=${week}`, {}, token);
    }
    return apiServerSide<RecommendationItem[]>(`/recommendations?week=${week}`);
  },
  
  sendLike: async (payload: LikePayload, token: string) => {
    return apiClientSide<{ ok: true }>('/likes', {
      method: 'POST',
      body: JSON.stringify(payload),
    }, token);
  },
};

// Matches API
export const matchesApi = {
  getMatches: async (token?: string) => {
    if (token) {
      return apiClientSide<Match[]>('/matches', {}, token);
    }
    return apiServerSide<Match[]>('/matches');
  },
  
  getMatch: async (matchId: string, token?: string) => {
    if (token) {
      return apiClientSide<{ match: Match; otherProfile: Profile }>(`/matches/${matchId}`, {}, token);
    }
    return apiServerSide<{ match: Match; otherProfile: Profile }>(`/matches/${matchId}`);
  },
};

// Payments API
export const paymentsApi = {
  createPaymentIntent: async (matchId: string, token?: string) => {
    if (token) {
      return apiClientSide<Payment>('/payments/intent', {
        method: 'POST',
        body: JSON.stringify({ matchId }),
      }, token);
    }
    return apiServerSide<Payment>('/payments/intent', {
      method: 'POST',
      body: JSON.stringify({ matchId }),
    });
  },
  
  getPayment: async (paymentId: string, token?: string) => {
    if (token) {
      return apiClientSide<Payment>(`/payments/${paymentId}`, {}, token);
    }
    return apiServerSide<Payment>(`/payments/${paymentId}`);
  },
};

// Admin API (Server-side only)
export const adminApi = {
  getUsers: async (query?: string, page?: number) => {
    const params = new URLSearchParams();
    if (query) params.append('query', query);
    if (page) params.append('page', page.toString());
    const queryString = params.toString();
    return apiServerSide<any>(`/admin/users${queryString ? `?${queryString}` : ''}`);
  },
  
  getMatches: async (status?: string) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    const queryString = params.toString();
    return apiServerSide<any>(`/admin/matches${queryString ? `?${queryString}` : ''}`);
  },
  
  getPayments: async (status?: string) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    const queryString = params.toString();
    return apiServerSide<any>(`/admin/payments${queryString ? `?${queryString}` : ''}`);
  },
  
  verifyPayment: async (paymentId: string) => {
    return apiServerSide<any>(`/admin/payments/${paymentId}/verify`, {
      method: 'POST',
    });
  },
  
  activateMatch: async (matchId: string) => {
    return apiServerSide<any>(`/admin/matches/${matchId}/activate`, {
      method: 'POST',
    });
  },
  
  runRecommendations: async () => {
    return apiServerSide<any>('/admin/recs/run', {
      method: 'POST',
    });
  },
};

// Helper functions
export function getIsoWeekLabel(date: Date): string {
  const year = date.getFullYear();
  const startOfYear = new Date(year, 0, 1);
  const dayOfYear = Math.floor((date.getTime() - startOfYear.getTime()) / (24 * 60 * 60 * 1000)) + 1;
  const week = Math.ceil((dayOfYear - date.getDay() + 1) / 7);
  return `${year}-W${week.toString().padStart(2, '0')}`;
}

export { ApiError };