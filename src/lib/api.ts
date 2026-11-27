import { storage } from './storage';

function resolveApiBaseUrl(): string {
  if (typeof window !== 'undefined' && window.location?.hostname?.endsWith('.app.github.dev')) {
    return `${window.location.protocol}//${window.location.hostname.replace('-8081.', '-8000.')}`;
  }
  return process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';
}

const API_BASE_URL = resolveApiBaseUrl();

export type UserRole = 'dispatcher' | 'volunteer' | 'admin';

export interface ApiRequestOptions extends RequestInit {
  requireAuth?: boolean;
}

export async function apiRequest<T>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const { requireAuth = true, headers, ...rest } = options;

  const token = storage.getString('auth.token');
  const role = storage.getString('auth.role') as UserRole | undefined;

  if (requireAuth && !token) {
    throw new Error('Unauthorized: Missing session token');
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...rest,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(role ? { 'X-User-Role': role } : {}),
      ...headers,
    },
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API Error (${response.status}): ${errorText}`);
  }

  return response.json() as Promise<T>;
}
