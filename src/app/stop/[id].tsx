import { useLocalSearchParams, router } from 'expo-router';
import { useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import { Presets } from 'react-native-pulsar';

import { Pressable } from '@/components/pressable';
import { useMealFlowStore } from '@/features/mealflow/store/mealflow-store';
import type { StopStatus } from '@/features/mealflow/types/mealflow';

export default function StopDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const stop = useMealFlowStore((state) => state.stops.find((item) => item.id === id));
  const volunteers = useMealFlowStore((state) => state.volunteers);
  const reassignStop = useMealFlowStore((state) => state.reassignStop);
  const setStopStatus = useMealFlowStore((state) => state.setStopStatus);
  const [confirmed, setConfirmed] = useState(false);
  if (!stop) return <View className="flex-1 items-center justify-center gap-4 bg-background p-6"><Text className="text-lg text-foreground">This stop could not be found.</Text><Pressable onPress={() => router.back()} className="rounded-full bg-accent px-5 py-3"><Text className="font-bold text-background">Back to route</Text></Pressable></View>;
  const owner = volunteers.find((volunteer) => volunteer.id === stop.ownerId);
  const available = volunteers.filter((volunteer) => volunteer.status === 'available' || volunteer.status === 'onRoute');
  const updateStatus = (status: StopStatus) => {
    setStopStatus(stop.id, status);
    if (status === 'delivered') {
      setConfirmed(true);
      Presets.System.notificationSuccess();
    }
  };

  return (
    <ScrollView className="flex-1 bg-background" contentContainerClassName="px-4 pt-safe-offset-2 pb-safe-offset-4 gap-4" showsVerticalScrollIndicator={false}>
      <Pressable onPress={() => router.back()} className="self-start rounded-full border border-border px-4 py-2"><Text className="text-sm text-foreground">‹  Back</Text></Pressable>
      <View className="gap-2 rounded-3xl border-2 border-success bg-surface p-5">
        <Text className="text-xs font-bold text-success">STOP {stop.number} · {stop.status.toUpperCase()}</Text>
        <Text className="text-2xl font-bold text-foreground">{stop.recipient}</Text>
        <Text className="text-sm text-muted">{stop.address}</Text><Text className="text-sm text-muted">{stop.city} · ETA {stop.eta}</Text>
        <Text className="text-sm text-foreground">{stop.meals} meal{stop.meals > 1 ? 's' : ''} · {stop.contact}</Text>
        <Text className={`text-sm font-semibold ${owner ? 'text-success' : 'text-warning'}`}>Owner: {owner?.name ?? 'Unassigned — needs attention'}</Text>
        {stop.updatedAt ? <Text className="text-xs text-muted">Last update {stop.updatedAt}{stop.note ? ` · ${stop.note}` : ''}</Text> : null}
        {confirmed ? <View className="items-center gap-1 rounded-2xl border border-success p-3"><Text className="text-2xl font-bold text-success">✓</Text><Text className="text-sm font-semibold text-success">Delivery closed</Text></View> : null}
      </View>
      <View className="gap-2 rounded-2xl border border-border bg-surface p-4"><Text className="text-base font-semibold text-foreground">Contact outcome</Text>{['Reached · delivered', 'Reached · running late', 'No answer · follow up'].map((outcome) => <Pressable key={outcome} onPress={() => setStopStatus(stop.id, outcome.includes('late') ? 'delayed' : outcome.includes('delivered') ? 'delivered' : 'open', outcome)} className="rounded-xl border border-border bg-background p-3"><Text className="text-sm text-foreground">{outcome}</Text></Pressable>)}</View>
      <View className="gap-2 rounded-2xl border border-border bg-surface p-4"><Text className="text-base font-semibold text-foreground">Delivery status</Text>{([['open', 'Open'], ['enRoute', 'En Route'], ['delayed', 'Delayed'], ['delivered', 'Mark delivered']] as [StopStatus, string][]).map(([status, label]) => <Pressable key={status} onPress={() => updateStatus(status)} className={`items-center rounded-full border py-3 ${stop.status === status ? 'border-success bg-accent' : 'border-border bg-background'}`}><Text className={`text-sm font-semibold ${stop.status === status ? 'text-background' : 'text-foreground'}`}>{label}</Text></Pressable>)}</View>
      <View className="gap-2 rounded-2xl border border-border bg-surface p-4"><Text className="text-base font-semibold text-foreground">Assign an owner</Text><Pressable onPress={() => reassignStop(stop.id, null)} className={`rounded-xl border p-3 ${stop.ownerId === null ? 'border-warning' : 'border-border'}`}><Text className="text-sm text-warning">Unassigned</Text></Pressable>{available.map((volunteer) => <Pressable key={volunteer.id} onPress={() => reassignStop(stop.id, volunteer.id)} className={`flex-row items-center justify-between rounded-xl border p-3 ${stop.ownerId === volunteer.id ? 'border-success' : 'border-border'}`}><View><Text className="text-sm font-semibold text-foreground">{volunteer.name}</Text><Text className="text-xs text-muted">{volunteer.status === 'available' ? 'Available' : volunteer.route}</Text></View><Text className="text-sm text-success">{stop.ownerId === volunteer.id ? 'Assigned' : 'Assign'}</Text></Pressable>)}</View>
    </ScrollView>
  );
}
