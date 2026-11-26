#!/usr/bin/env bash
set -euo pipefail

echo "1. Creating environment config..."
cat << 'ENV' > .env.example
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_ENV=development
ENV

if [ ! -f ".env" ]; then
  cp .env.example .env
fi

echo "2. Creating src/lib/api.ts..."
mkdir -p src/lib
cat << 'TS' > src/lib/api.ts
import { storage } from './storage';

const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000';

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
TS

echo "3. Running TypeScript check..."
bun run typecheck
