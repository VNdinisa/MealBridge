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
