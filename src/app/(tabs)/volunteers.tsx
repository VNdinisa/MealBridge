import { ScrollView, Text, View } from 'react-native';

import { Pressable } from '@/components/pressable';
import { useMealFlowStore } from '@/features/mealflow/store/mealflow-store';
import type { Volunteer, VolunteerStatus } from '@/features/mealflow/types/mealflow';
import { Href, router } from 'expo-router';

function VolunteerCard({ volunteer, stopsOpen }: { volunteer: Volunteer; stopsOpen: number }) {
  const setAvailability = useMealFlowStore((state) => state.setAvailability);
  const statuses: VolunteerStatus[] = ['available', 'onRoute', 'unavailable'];
  const nextStatus: VolunteerStatus = volunteer.status === 'available' ? 'unavailable' : 'available';
  const label = volunteer.status === 'onRoute' ? 'On Route' : volunteer.status === 'available' ? 'Available' : 'Unavailable';
  const badge = volunteer.status === 'onRoute' ? 'bg-info' : volunteer.status === 'available' ? 'bg-success' : 'bg-border';
  return (
    <View className="gap-2 rounded-2xl border border-border bg-surface p-3">
      <Pressable onPress={() => router.push((`/volunteer/${volunteer.id}` as Href))} className="flex-row items-center gap-3">
        <View className="size-10 items-center justify-center rounded-full bg-info"><Text className="text-sm font-bold text-foreground">{volunteer.name.split(' ').map((part) => part[0]).join('')}</Text></View>
        <View className="flex-1 gap-1"><Text className="text-sm font-semibold text-foreground">{volunteer.name}</Text><Text className="text-xs text-muted">{volunteer.route} · {stopsOpen} open stop{stopsOpen === 1 ? '' : 's'}</Text></View>
        <View className={`rounded-full px-2 py-1 ${badge}`}><Text className="text-xs font-semibold text-background">{label}</Text></View>
      </Pressable>
      <View className="flex-row gap-2">
        {statuses.map((status) => <Pressable key={status} onPress={() => setAvailability(volunteer.id, status)} className={`flex-1 items-center rounded-xl border py-2 ${volunteer.status === status ? 'border-accent bg-accent' : 'border-border bg-background'}`}><Text className={`text-xs ${volunteer.status === status ? 'font-bold text-background' : 'text-muted'}`}>{status === 'onRoute' ? 'On Route' : status[0].toUpperCase() + status.slice(1)}</Text></Pressable>)}
      </View>
    </View>
  );
}

export default function VolunteersScreen() {
  const volunteers = useMealFlowStore((state) => state.volunteers);
  const stops = useMealFlowStore((state) => state.stops);
  const available = volunteers.filter((volunteer) => volunteer.status === 'available').length;
  const onRoute = volunteers.filter((volunteer) => volunteer.status === 'onRoute').length;
  const unavailable = volunteers.filter((volunteer) => volunteer.status === 'unavailable').length;
  const ownerName = (id: string | null) => volunteers.find((volunteer) => volunteer.id === id)?.name;
  const changeStatus = useMealFlowStore((state) => state.setAvailability);
  const lisa = volunteers.find((volunteer) => volunteer.id === 'v4');
  const lisaStops = stops.filter((stop) => stop.ownerId === 'v4' && stop.status !== 'delivered').length;
  const ownedOpen = stops.filter((stop) => stop.status !== 'delivered' && stop.ownerId !== null).length;
  const unassigned = stops.filter((stop) => stop.status !== 'delivered' && stop.ownerId === null).length;
  const roster = [...volunteers].sort((a, b) => a.status === 'unavailable' ? 1 : b.status === 'unavailable' ? -1 : a.name.localeCompare(b.name));

  return (
    <ScrollView className="flex-1 bg-background" contentContainerClassName="px-4 pt-safe-offset-4 pb-safe-offset-28 gap-3" showsVerticalScrollIndicator={false}>
      <Text className="text-2xl font-bold text-foreground">Volunteers</Text>
      <Text className="text-sm text-muted">Riverside Community Meals · Tuesday shift</Text>
      <View className="flex-row gap-2">
        {[['Available', available, 'text-success'], ['On Route', onRoute, 'text-info'], ['Unavailable', unavailable, 'text-warning'], ['Stops Owned', ownedOpen, 'text-foreground']].map(([label, count, color]) => <View key={String(label)} className="flex-1 items-center gap-1 rounded-2xl border border-border bg-surface p-2"><Text className="text-xs text-muted">{label}</Text><Text className={`text-lg font-bold ${color}`}>{count}</Text></View>)}
      </View>
      {unassigned > 0 ? <Pressable onPress={() => router.navigate('/')} className="flex-row items-center justify-between rounded-2xl border border-warning bg-surface p-3"><View className="gap-1"><Text className="text-sm font-bold text-warning">{unassigned} unassigned stop{unassigned === 1 ? '' : 's'} need an owner</Text><Text className="text-xs text-muted">Open the stop to assign an available volunteer.</Text></View><Text className="text-lg text-warning">›</Text></Pressable> : null}
      {lisa ? <View className="gap-2 rounded-3xl border-2 border-success bg-surface p-4"><Text className="text-xs font-bold text-success">ON-CALL VOLUNTEER</Text><Text className="text-xl font-semibold text-foreground">{lisa.name}</Text><Text className="text-sm text-muted">{lisaStops} open stops · {lisa.status === 'unavailable' ? 'Unavailable' : lisa.status === 'available' ? 'Available for assignment' : lisa.route}</Text><View className="flex-row gap-2"><Pressable onPress={() => changeStatus(lisa.id, 'available')} className="flex-1 items-center rounded-full bg-accent py-2"><Text className="text-sm font-bold text-background">Available</Text></Pressable><Pressable onPress={() => changeStatus(lisa.id, 'unavailable')} className="flex-1 items-center rounded-full border border-border py-2"><Text className="text-sm font-semibold text-foreground">Unavailable</Text></Pressable></View></View> : null}
      <View className="flex-row items-center justify-between"><Text className="text-lg font-semibold text-foreground">Today’s Team</Text><Text className="text-xs text-muted">{volunteers.length} volunteers</Text></View>
      {roster.map((volunteer) => <VolunteerCard key={volunteer.id} volunteer={volunteer} stopsOpen={stops.filter((stop) => stop.ownerId === volunteer.id && stop.status !== 'delivered').length} />)}
      <View className="gap-2 rounded-2xl border border-border bg-surface p-3"><Text className="text-sm font-semibold text-foreground">Coverage check</Text><Text className="text-xs text-muted">{ownedOpen} open stops have an owner. {unassigned} need dispatcher attention.</Text><Text className="text-xs text-muted">Set a volunteer unavailable, then reassign their open stops from each stop’s details.</Text></View>
    </ScrollView>
  );
}
