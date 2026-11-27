#!/usr/bin/env bash
set -euo pipefail

echo "1. Checking existing components and storage helper..."
ls -la src/components/ src/lib/

echo "2. Creating MealBridge Onboarding Screen (src/app/onboarding.tsx)..."
cat << 'TSX' > src/app/onboarding.tsx
import React, { useState } from 'react';
import { ScrollView, TextInput, Pressable, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { submitOnboarding } from '@/lib/mealbridgeService';

export default function OnboardingScreen() {
  const router = useRouter();
  const [name, setName] = useState('Pretend Volunteer 11');
  const [role, setRole] = useState<'volunteer' | 'dispatcher'>('volunteer');
  const [pretendPhone, setPretendPhone] = useState('555-0111');
  const [zone, setZone] = useState('Zone 1');
  const [loading, setLoading] = useState(false);

  const handleOnboard = async () => {
    try {
      setLoading(true);
      const session = await submitOnboarding({
        name,
        role,
        pretend_phone: pretendPhone,
        zone,
      });
      Alert.alert(
        'Onboarded (Pretend Mode)',
        `Signed in as ${session.user_id} (${session.role})`
      );
      router.replace('/');
    } catch (err: any) {
      Alert.alert('Guardrail / Onboarding Error', err?.message ?? 'Failed to onboard');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ThemedView className="flex-1 p-5">
      <ScrollView contentContainerClassName="gap-4 pb-10">
        <ThemedText className="text-2xl font-bold">MealBridge Onboarding</ThemedText>
        <ThemedText className="text-sm opacity-75">
          Pretend-Data Privacy Mode: Use synthetic 555 test phone numbers only.
        </ThemedText>

        <ThemedView className="flex-row gap-2">
          {(['volunteer', 'dispatcher'] as const).map((r) => (
            <Pressable
              key={r}
              onPress={() => setRole(r)}
              className={`flex-1 p-3 rounded-xl border ${
                role === r ? 'bg-primary border-primary' : 'border-border'
              }`}
            >
              <ThemedText className="text-center font-semibold capitalize">{r}</ThemedText>
            </Pressable>
          ))}
        </ThemedView>

        <TextInput
          value={name}
          onChangeText={setName}
          placeholder="Pretend Name"
          className="p-3 rounded-xl border border-border text-foreground"
        />

        <TextInput
          value={pretendPhone}
          onChangeText={setPretendPhone}
          placeholder="555-0111"
          className="p-3 rounded-xl border border-border text-foreground"
        />

        {role === 'volunteer' && (
          <TextInput
            value={zone}
            onChangeText={setZone}
            placeholder="Zone 1"
            className="p-3 rounded-xl border border-border text-foreground"
          />
        )}

        <Pressable
          onPress={handleOnboard}
          disabled={loading}
          className="p-4 rounded-xl bg-primary items-center"
        >
          <ThemedText className="font-bold text-primary-foreground">
            {loading ? 'Registering Session...' : 'Start Pretend Shift'}
          </ThemedText>
        </Pressable>
      </ScrollView>
    </ThemedView>
  );
}
TSX

echo "3. Creating Delivery Stops & Voice-Note Screen (src/app/index.tsx)..."
cat << 'TSX' > src/app/index.tsx
import React, { useEffect, useState } from 'react';
import { ScrollView, Pressable, TextInput, Alert } from 'react-native';
import { useRouter } from 'expo-router';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { storage } from '@/lib/storage';
import {
  DeliveryStop,
  VoiceProcessResponse,
  completeDeliveryStop,
  fetchDeliveryStops,
  processVoiceTranscript,
} from '@/lib/mealbridgeService';

export default function MealBridgeHomeScreen() {
  const router = useRouter();
  const [stops, setStops] = useState<DeliveryStop[]>([]);
  const [selectedStopId, setSelectedStopId] = useState('STOP-01');
  const [transcript, setTranscript] = useState(
    'Delivered meal at 123 Pretend Ave. Neighbor asked to call 555-0199.'
  );
  const [voiceResult, setVoiceResult] = useState<VoiceProcessResponse | null>(null);
  const [busy, setBusy] = useState(false);

  const role = storage.getString('auth.role') ?? 'guest';
  const userId = storage.getString('auth.userId') ?? 'unauthenticated';

  const loadStops = async () => {
    try {
      const data = await fetchDeliveryStops();
      setStops(data);
      if (data.length > 0) setSelectedStopId(data[0].stop_id);
    } catch {
      const cached = storage.getString('cache.stops');
      if (cached) setStops(JSON.parse(cached));
    }
  };

  useEffect(() => {
    if (!storage.getBoolean('onboarding.completed')) {
      router.replace('/onboarding');
      return;
    }
    loadStops();
  }, []);

  const handleDeliver = async (stopId: string) => {
    try {
      const updated = await completeDeliveryStop(stopId);
      setStops((prev) => prev.map((s) => (s.stop_id === stopId ? updated : s)));
    } catch (err: any) {
      Alert.alert('Delivery Update Error', err?.message ?? 'Could not update stop');
    }
  };

  const handleAnalyzeVoice = async () => {
    try {
      setBusy(true);
      const res = await processVoiceTranscript(selectedStopId, transcript, 'google');
      setVoiceResult(res);
    } catch (err: any) {
      Alert.alert('PII / AI Guardrail', err?.message ?? 'Voice processing failed');
    } finally {
      setBusy(false);
    }
  };

  return (
    <ThemedView className="flex-1 p-5">
      <ScrollView contentContainerClassName="gap-4 pb-12">
        <ThemedView className="flex-row justify-between items-center">
          <ThemedView>
            <ThemedText className="text-xl font-bold">MealBridge Routes</ThemedText>
            <ThemedText className="text-xs opacity-75">
              Active: {userId} ({role})
            </ThemedText>
          </ThemedView>
          <Pressable
            onPress={() => router.push('/onboarding')}
            className="px-3 py-2 rounded-lg border border-border"
          >
            <ThemedText className="text-xs font-semibold">Switch Role</ThemedText>
          </Pressable>
        </ThemedView>

        <ThemedView className="p-4 rounded-xl border border-border gap-3">
          <ThemedText className="font-bold">Voice-Note PII Scrubber & AI Summary</ThemedText>
          <TextInput
            value={transcript}
            onChangeText={setTranscript}
            multiline
            className="p-3 rounded-lg border border-border text-foreground"
          />
          <Pressable
            onPress={handleAnalyzeVoice}
            disabled={busy}
            className="p-3 rounded-lg bg-primary items-center"
          >
            <ThemedText className="font-semibold text-primary-foreground">
              {busy ? 'Scrubbing & Summarizing...' : `Process Note for ${selectedStopId}`}
            </ThemedText>
          </Pressable>

          {voiceResult && (
            <ThemedView className="p-3 rounded-lg border border-border gap-1">
              <ThemedText className="text-xs font-semibold">
                Redacted: {voiceResult.redacted_categories.join(', ') || 'None'}
              </ThemedText>
              <ThemedText className="text-xs">
                Scrubbed: {voiceResult.scrubbed_transcript}
              </ThemedText>
              <ThemedText className="text-xs font-medium">
                AI Summary: {voiceResult.ai_analysis.summary}
              </ThemedText>
            </ThemedView>
          )}
        </ThemedView>

        <ThemedText className="font-bold">
          Assigned Pretend Stops ({stops.length})
        </ThemedText>

        {stops.map((stop) => (
          <Pressable
            key={stop.stop_id}
            onPress={() => setSelectedStopId(stop.stop_id)}
            className="p-4 rounded-xl border border-border gap-1"
          >
            <ThemedText className="font-bold">
              {stop.stop_id} · {stop.neighbor_alias} ({stop.status})
            </ThemedText>
            <ThemedText className="text-xs opacity-80">
              {stop.pretend_address} · {stop.pretend_phone} · {stop.dietary_note}
            </ThemedText>
            {stop.status !== 'delivered' && (
              <Pressable
                onPress={() => handleDeliver(stop.stop_id)}
                className="mt-2 py-2 px-3 rounded-lg bg-primary self-start"
              >
                <ThemedText className="text-xs font-bold text-primary-foreground">
                  Mark Delivered
                </ThemedText>
              </Pressable>
            )}
          </Pressable>
        ))}
      </ScrollView>
    </ThemedView>
  );
}
TSX

echo "4. Done! Running TypeScript check..."
npx tsc --noEmit || true
