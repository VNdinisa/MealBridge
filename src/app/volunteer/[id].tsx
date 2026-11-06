import { useLocalSearchParams, router, type Href } from 'expo-router';
import { ScrollView, Text, View } from 'react-native';

import { Pressable } from '@/components/pressable';
import { useMealFlowStore } from '@/features/mealflow/store/mealflow-store';

export default function VolunteerDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const volunteer = useMealFlowStore((state) => state.volunteers.find((item) => item.id === id));
  const stops = useMealFlowStore((state) => state.stops.filter((stop) => stop.ownerId === id));
  const setAvailability = useMealFlowStore((state) => state.setAvailability);
  if (!volunteer) return <View className="flex-1 items-center justify-center bg-background p-6"><Text className="text-foreground">Volunteer not found.</Text><Pressable onPress={() => router.back()} className="rounded-full bg-accent px-4 py-3"><Text className="text-background">Back</Text></Pressable></View>;
  const outstanding = stops.filter((stop) => stop.status !== 'delivered');

  return (
    <ScrollView className="flex-1 bg-background" contentContainerClassName="px-4 pt-safe-offset-2 pb-safe-offset-4 gap-4" showsVerticalScrollIndicator={false}>
      <Pressable onPress={() => router.back()} className="self-start rounded-full border border-border px-4 py-2"><Text className="text-sm text-foreground">‹  Back</Text></Pressable>
      <View className="items-center gap-2 rounded-3xl border border-info bg-surface p-5"><View className="size-16 items-center justify-center rounded-full bg-info"><Text className="text-xl font-bold text-foreground">{volunteer.name}</Text></View><Text className="text-xl font-bold text-foreground">{volunteer.name}</Text><Text className="text-sm text-muted">{volunteer.status === 'onRoute' ? 'On route' : volunteer.status === 'available' ? 'Available for assignment' : 'Unavailable today'}</Text><Text className="text-xs text-muted">{volunteer.route} · {volunteer.phone}</Text></View>
      <View className="flex-row gap-2">{[['Hours', volunteer.hours], ['Shifts', volunteer.shifts], ['Rating', volunteer.rating]].map(([label, value]) => <View key={String(label)} className="flex-1 items-center gap-1 rounded-2xl border border-border bg-surface p-3"><Text className="text-xs text-muted">{label}</Text><Text className="text-lg font-bold text-foreground">{value}</Text></View>)}</View>
      <View className="gap-2 rounded-2xl border border-border bg-surface p-4"><Text className="text-base font-semibold text-foreground">Availability</Text>{(['available', 'onRoute', 'unavailable'] as const).map((status) => <Pressable key={status} onPress={() => setAvailability(volunteer.id, status)} className={`items-center rounded-full border py-3 ${volunteer.status === status ? 'border-accent bg-accent' : 'border-border bg-background'}`}><Text className={`text-sm ${volunteer.status === status ? 'font-bold text-background' : 'text-foreground'}`}>{status === 'onRoute' ? 'On route' : status[0].toUpperCase() + status.slice(1)}</Text></Pressable>)}</View>
      <Text className="text-lg font-semibold text-foreground">Assigned Stops</Text>
      {stops.map((stop) => <Pressable key={stop.id} onPress={() => router.push((`/stop/${stop.id}` as Href))} className="flex-row items-center justify-between rounded-2xl border border-border bg-surface p-3"><View className="gap-1"><Text className="text-sm font-semibold text-foreground">{stop.number}. {stop.recipient}</Text><Text className="text-xs text-muted">{stop.address} · {stop.status}</Text></View><Text className="text-info">›</Text></Pressable>)}
      {outstanding.length > 0 && volunteer.status === 'unavailable' ? <View className="gap-2 rounded-2xl border border-warning bg-surface p-4"><Text className="text-sm font-semibold text-warning">{outstanding.length} open stop{outstanding.length === 1 ? '' : 's'} still assigned</Text><Text className="text-xs text-muted">Reassign each stop before closing the shift.</Text></View> : null}
    </ScrollView>
  );
}
