import { apiRequest, UserRole } from './api';
import { storage } from './storage';

export interface OnboardPayload {
  name: string;
  role: 'volunteer' | 'dispatcher';
  pretend_phone: string;
  zone?: string;
}

export interface OnboardSession {
  user_id: string;
  name: string;
  role: UserRole;
  zone: string;
  token: string;
  is_pretend_data: boolean;
}

export interface DeliveryStop {
  stop_id: string;
  neighbor_alias: string;
  pretend_address: string;
  pretend_phone: string;
  dietary_note: string;
  assigned_volunteer_id: string;
  status: 'pending' | 'in_transit' | 'delivered';
  is_pretend_data: boolean;
  updated_at: string;
}

export interface VoiceProcessResponse {
  stop_id: string;
  scrubbed_transcript: string;
  redacted_categories: string[];
  ai_analysis: {
    provider: string;
    model: string;
    summary: string;
  };
}

/** 1. Onboard pretend user and hydrate MMKV auth keys */
export async function submitOnboarding(payload: OnboardPayload): Promise<OnboardSession> {
  const res = await apiRequest<{ message: string; session: OnboardSession }>(
    '/api/onboarding',
    {
      method: 'POST',
      requireAuth: false,
      body: JSON.stringify({
        ...payload,
        is_pretend_data: true,
      }),
    }
  );

  storage.set('auth.token', res.session.token);
  storage.set('auth.role', res.session.role);
  storage.set('auth.userId', res.session.user_id);
  storage.set('onboarding.completed', true);

  return res.session;
}

/** 2. Fetch stops (backend automatically filters to assigned stops for volunteers) */
export async function fetchDeliveryStops(): Promise<DeliveryStop[]> {
  const res = await apiRequest<{ count: number; stops: DeliveryStop[] }>('/api/stops');
  storage.set('cache.stops', JSON.stringify(res.stops));
  return res.stops;
}

/** 3. Mark a stop delivered and update local MMKV cache */
export async function completeDeliveryStop(stopId: string): Promise<DeliveryStop> {
  const res = await apiRequest<{ message: string; stop: DeliveryStop }>(
    `/api/stops/${encodeURIComponent(stopId)}/deliver`,
    { method: 'PATCH' }
  );
  return res.stop;
}

/** 4. Submit voice-note transcript for PII scrubbing + Google Cloud / NVIDIA summary */
export async function processVoiceTranscript(
  stopId: string,
  rawTranscript: string,
  provider: 'google' | 'nvidia' = 'google'
): Promise<VoiceProcessResponse> {
  return apiRequest<VoiceProcessResponse>(
    `/api/voice-notes/process?provider=${provider}`,
    {
      method: 'POST',
      body: JSON.stringify({
        stop_id: stopId,
        raw_transcript: rawTranscript,
        is_pretend_data: true,
      }),
    }
  );
}
