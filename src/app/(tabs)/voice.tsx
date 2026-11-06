import { useState } from 'react';
import { ScrollView, Text, TextInput, View } from 'react-native';

import { Pressable } from '@/components/pressable';
import { useMealFlowStore } from '@/features/mealflow/store/mealflow-store';
import type { StopStatus } from '@/features/mealflow/types/mealflow';
import { router, type Href } from 'expo-router';

export default function VoiceScreen() {
  const stops = useMealFlowStore((state) => state.stops);
  const updates = useMealFlowStore((state) => state.updates);
  const addVoiceUpdate = useMealFlowStore((state) => state.addVoiceUpdate);
  const [confirmedMessage, setConfirmedMessage] = useState('');
  const [transcript, setTranscript] = useState('');
  const [selectedStop, setSelectedStop] = useState(stops[0]?.id ?? 's1');
  const [status, setStatus] = useState<StopStatus>('delivered');
  const [note, setNote] = useState('Recipient reached');
  const [reviewing, setReviewing] = useState(false);

  const suggestions = [
    { label: 'Delivered, recipient answered', text: 'Meal delivered. Recipient answered the door.', status: 'delivered' as const },
    { label: 'Recipient not home', text: 'Recipient not home. Please follow up.', status: 'open' as const },
    { label: 'Running late', text: 'Running about ten minutes late.', status: 'delayed' as const },
  ];
  const propose = (text: string, nextStatus: StopStatus) => {
    setTranscript(text);
    setStatus(nextStatus);
    setReviewing(true);
  };
  const confirm = () => {
    if (!transcript.trim()) return;
    const target = stops.find((stop) => stop.id === selectedStop);
    addVoiceUpdate(transcript.trim(), selectedStop, status, note);
    setConfirmedMessage(`Update saved · Stop ${target?.number} is ${statusName(status)}.`);
    setTranscript('');
    setReviewing(false);
  };
  const statusName = (value: StopStatus) => value === 'enRoute' ? 'En route' : value[0].toUpperCase() + value.slice(1);

  return (
    <ScrollView className="flex-1 bg-background" contentContainerClassName="px-4 pt-safe-offset-4 pb-safe-offset-28 gap-3" showsVerticalScrollIndicator={false} scrollIndicatorInsets={{ bottom: 104 }}>
      <Text className="text-2xl font-bold text-foreground">Voice Hub</Text>
      <Text className="text-sm text-muted">Turn a shift update into a reviewed stop change.</Text>
      <View className="flex-row items-center gap-3 rounded-3xl border border-info bg-surface p-4"><View className="size-12 items-center justify-center rounded-full bg-info"><Text className="text-xl">🎙</Text></View><View className="flex-1 gap-1"><Text className="text-base font-semibold text-foreground">Quick update</Text><Text className="text-xs text-muted">Choose a phrase or type what you heard. Confirm before any stop changes.</Text></View></View>
      <View className="gap-2"><Text className="text-sm font-semibold text-foreground">Suggested updates</Text>{suggestions.map((suggestion) => <Pressable key={suggestion.label} onPress={() => propose(suggestion.text, suggestion.status)} className="rounded-2xl border border-border bg-surface p-3"><Text className="text-sm text-foreground">{suggestion.label}</Text></Pressable>)}</View>
      <View className="gap-2 rounded-3xl border border-border bg-surface p-4">
        <Text className="text-sm font-semibold text-foreground">Update details</Text>
        <Text className="text-xs text-muted">Stop</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerClassName="gap-2">
          {stops.map((stop) => <Pressable key={stop.id} onPress={() => setSelectedStop(stop.id)} className={`rounded-full border px-3 py-2 ${selectedStop === stop.id ? 'border-accent bg-accent' : 'border-border bg-background'}`}><Text className={`text-xs ${selectedStop === stop.id ? 'font-bold text-background' : 'text-foreground'}`}>{stop.number} · {stop.recipient.split(' ')[0]}</Text></Pressable>)}
        </ScrollView>
        <Text className="text-xs text-muted">Transcript or dispatcher note</Text>
        <TextInput value={transcript} onChangeText={setTranscript} multiline className="min-h-20 rounded-xl border border-border bg-background p-3 text-sm leading-normal text-foreground" placeholder="Type what the volunteer said…" placeholderTextColor="#8093B2" />
        <View className="flex-row gap-2">{(['delivered', 'delayed', 'open'] as StopStatus[]).map((item) => <Pressable key={item} onPress={() => setStatus(item)} className={`flex-1 items-center rounded-full border py-2 ${status === item ? 'border-accent bg-accent' : 'border-border'}`}><Text className={`text-xs ${status === item ? 'font-bold text-background' : 'text-muted'}`}>{statusName(item)}</Text></Pressable>)}</View>
        {reviewing ? <View className="gap-2 rounded-xl border border-warning p-3"><Text className="text-sm font-semibold text-warning">Review before applying</Text><Text className="text-xs text-foreground">{transcript}</Text><Text className="text-xs text-muted">Stop {stops.find((stop) => stop.id === selectedStop)?.number} · {statusName(status)}</Text><View className="flex-row gap-2"><Pressable onPress={() => setReviewing(false)} className="flex-1 items-center rounded-full border border-border py-2"><Text className="text-xs text-foreground">Keep editing</Text></Pressable><Pressable onPress={confirm} className="flex-1 items-center rounded-full bg-accent py-2"><Text className="text-xs font-bold text-background">Confirm update</Text></Pressable></View></View> : <Pressable onPress={() => setReviewing(true)} className="items-center rounded-full bg-accent py-3"><Text className="text-sm font-bold text-background">Review update</Text></Pressable>}
        <Text className="text-xs text-muted">Voice transcription is not connected in this prototype. Text proposals stay on this device and are applied only after confirmation.</Text>
      </View>
      {confirmedMessage ? <View className="rounded-2xl border border-success bg-surface p-3"><Text className="text-sm font-semibold text-success">{confirmedMessage}</Text></View> : null}
      <Text className="text-lg font-semibold text-foreground">Recent Updates</Text>
      {updates.map((update) => <Pressable key={update.id} onPress={() => router.push((`/stop/${update.stopId}` as Href))} className="gap-2 rounded-2xl border border-border bg-surface p-3"><View className="flex-row justify-between"><Text className="text-xs font-semibold text-success">{update.outcome}</Text><Text className="text-xs text-muted">{update.time}</Text></View><Text className="text-sm text-foreground">{update.transcript}</Text><Text className="text-xs text-info">View stop {stops.find((stop) => stop.id === update.stopId)?.number} ›</Text></Pressable>)}
    </ScrollView>
  );
}
