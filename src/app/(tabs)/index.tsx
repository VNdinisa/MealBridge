import { useState } from 'react';
import { Image } from 'expo-image';
import { ScrollView, Text, View } from 'react-native';
import { Presets } from 'react-native-pulsar';

import { Pressable } from '@/components/pressable';
import { useMealFlowStore } from '@/features/mealflow/store/mealflow-store';
import type { DeliveryStop, StopStatus } from '@/features/mealflow/types/mealflow';
import { router, useNavigation, type Href } from 'expo-router';

const statusLabel: Record<StopStatus, string> = { delivered: 'Delivered', enRoute: 'En route', delayed: 'Delayed', open: 'Open' };
const statusColor: Record<StopStatus, string> = { delivered: 'text-success', enRoute: 'text-info', delayed: 'text-warning', open: 'text-muted' };

function StopCard({ stop, ownerName }: { stop: DeliveryStop; ownerName: string }) {
  return (
    <Pressable onPress={() => router.push((`/stop/${stop.id}` as Href))} className="w-full flex-row items-center gap-3 rounded-2xl border border-border bg-surface p-3">
      <View className={`size-9 items-center justify-center rounded-full ${stop.status === 'delayed' ? 'bg-warning' : stop.status === 'delivered' ? 'bg-accent' : 'bg-background'}`}>
        <Text className="text-sm font-bold text-foreground">{stop.number}</Text>
      </View>
      <View className="flex-1 gap-1">
        <Text className="text-sm font-semibold text-foreground" numberOfLines={1}>{stop.recipient}</Text>
        <Text className="text-xs text-muted" numberOfLines={1}>{stop.address} · Riverside, CA</Text>
        <Text className={`text-xs ${statusColor[stop.status]}`} numberOfLines={1}>{stop.updatedAt ? `${statusLabel[stop.status]} ${stop.updatedAt}` : statusLabel[stop.status]} · {stop.meals} meal{stop.meals > 1 ? 's' : ''} · {ownerName}</Text>
      </View>
      <View className={`rounded-full px-2 py-1 ${stop.status === 'delivered' ? 'bg-accent' : stop.status === 'delayed' ? 'bg-warning' : 'bg-background'}`}>
        <Text className="text-xs font-semibold text-foreground">{stop.status === 'delivered' ? 'Done' : statusLabel[stop.status]}</Text>
      </View>
    </Pressable>
  );
}

export default function DeliveriesScreen() {
  const stops = useMealFlowStore((state) => state.stops);
  const volunteers = useMealFlowStore((state) => state.volunteers);
  const [filter, setFilter] = useState<StopStatus | 'all'>('all');
  const delivered = stops.filter((stop) => stop.status === 'delivered').length;
  const enRoute = stops.filter((stop) => stop.status === 'enRoute').length;
  const delayed = stops.filter((stop) => stop.status === 'delayed').length;
  const open = stops.filter((stop) => stop.status === 'open').length;
  const next = stops.find((stop) => stop.status !== 'delivered');
  const selected = stops.filter((stop) => filter === 'all' || stop.status === filter);
  const ownerFor = (stop: DeliveryStop) => volunteers.find((volunteer) => volunteer.id === stop.ownerId)?.name ?? 'Unassigned';
  const statuses: { key: StopStatus; label: string; count: number; color: string }[] = [
    { key: 'delivered', label: 'Delivered', count: delivered, color: 'text-success' },
    { key: 'enRoute', label: 'En Route', count: enRoute, color: 'text-info' },
    { key: 'delayed', label: 'Delayed', count: delayed, color: 'text-warning' },
    { key: 'open', label: 'Open', count: open, color: 'text-muted' },
  ];
  const setStopStatus = useMealFlowStore((state) => state.setStopStatus);
  const navigation = useNavigation();

  const completeNext = () => {
    if (!next) return;
    setStopStatus(next.id, 'delivered');
    Presets.System.notificationSuccess();
  };

  return (
    <ScrollView className="flex-1 bg-background" contentContainerClassName="px-4 pt-safe-offset-4 pb-safe-offset-28 gap-3" showsVerticalScrollIndicator={false} scrollIndicatorInsets={{ bottom: 104 }}>
      <View className="flex-row items-center gap-3">
        <View className="flex-1 gap-1">
          <Text className="text-lg font-semibold text-foreground">Today’s Deliveries</Text>
          <Text className="text-4xl font-bold text-success">{delivered}<Text className="text-muted"> / {stops.length}</Text></Text>
        </View>
        <Image source={require('@/assets/mealflow-mascot.png')} contentFit="contain" className="size-20" />
      </View>
      <View className="h-2 overflow-hidden rounded-full bg-border"><View className="h-full rounded-full bg-success" style={{ width: `${stops.length === 0 ? 0 : delivered / stops.length * 100}%` }} /></View>
      <Text className="text-sm text-muted">{open + enRoute + delayed} remaining · {delayed} on-time alert{delayed === 1 ? '' : 's'} · Riverside Community Meals</Text>
      <View className="flex-row gap-2">
        {statuses.map((item) => <Pressable key={item.key} onPress={() => setFilter(filter === item.key ? 'all' : item.key)} className={`flex-1 items-center gap-1 rounded-2xl border ${filter === item.key ? 'border-accent' : 'border-border'} bg-surface p-2`}><Text className={`text-xs ${item.color}`}>{item.label}</Text><Text className={`text-lg font-bold ${item.color}`}>{item.count}</Text></Pressable>)}
      </View>
      {next ? <Pressable onPress={() => router.push((`/stop/${next.id}` as Href))} className="gap-2 rounded-3xl border-2 border-success bg-surface p-4">
        <View className="flex-row items-center gap-3">
          <View className="size-12 items-center justify-center rounded-full bg-success"><Text className="text-lg font-bold text-background">{next.number}</Text></View>
          <View className="flex-1 gap-1"><Text className="text-xs font-bold text-success">NEXT STOP</Text><Text className="text-lg font-semibold text-foreground">{next.recipient}</Text><Text className="text-sm text-muted">{next.address} · Riverside, CA</Text></View>
          <View className="rounded-full bg-accent px-3 py-2"><Text className="text-xs font-bold text-background">{ownerFor(next)}</Text></View>
        </View>
        <Text className="text-xs text-muted">◷ ETA {next.eta}   ·   {next.meals} meal{next.meals > 1 ? 's' : ''}   ·   {ownerFor(next)}</Text>
        <Pressable onPress={completeNext} className="items-center rounded-full bg-accent py-2"><Text className="text-sm font-bold text-background">Mark delivered</Text></Pressable>
      </Pressable> : <View className="items-center gap-2 rounded-3xl border border-success bg-surface p-4"><Text className="text-lg font-semibold text-success">All 20 stops are closed</Text><Text className="text-sm text-muted">Today’s route is complete.</Text></View>}
      <Pressable onPress={() => navigation.getParent()?.navigate('voice' as never)} className="flex-row items-center gap-3 rounded-3xl border border-info bg-surface p-3">
        <View className="size-12 items-center justify-center rounded-full bg-info"><Text className="text-xl text-foreground">🎙</Text></View><View className="flex-1 gap-1"><Text className="text-base font-semibold text-foreground">Voice Update</Text><Text className="text-xs text-muted">Review a quick delivery update</Text></View><Text className="text-xl text-muted">›</Text>
      </Pressable>
      <View className="flex-row items-center justify-between px-1"><Text className="text-lg font-semibold text-foreground">Today’s Stops</Text><Text className="text-xs text-muted">{delivered} done · {delayed} late · {open} open</Text></View>
      {filter !== 'all' ? <Pressable onPress={() => setFilter('all')} className="self-start rounded-full border border-border px-3 py-1"><Text className="text-xs text-info">Showing {statusLabel[filter]} · Clear filter</Text></Pressable> : null}
      {selected.map((stop) => <StopCard key={stop.id} stop={stop} ownerName={ownerFor(stop)} />)}
      {selected.length === 0 ? <Text className="rounded-2xl border border-border p-4 text-center text-sm text-muted">No stops match this status.</Text> : null}
    </ScrollView>
  );
}
