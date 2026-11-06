import { ScrollView, Text, View } from 'react-native';
import { useState } from 'react';

import { Pressable } from '@/components/pressable';
import { useMealFlowStore } from '@/features/mealflow/store/mealflow-store';

type Period = '7D' | '30D' | '90D' | 'All';

export default function AnalyticsScreen() {
  const [period, setPeriod] = useState<Period>('7D');
  const stops = useMealFlowStore((state) => state.stops);
  const volunteers = useMealFlowStore((state) => state.volunteers);
  const delivered = stops.filter((stop) => stop.status === 'delivered').length;
  const late = stops.filter((stop) => stop.status === 'delayed').length;
  const open = stops.filter((stop) => stop.status === 'open').length;
  const owned = stops.filter((stop) => stop.status !== 'delivered' && stop.ownerId !== null).length;
  const onTimeRate = Math.round((delivered / Math.max(1, delivered + late)) * 100);
  const areas = [
    ['Riverside North', stops.slice(0, 6).length], ['Downtown', stops.slice(6, 12).length],
    ['Canyon Crest', stops.slice(12, 16).length], ['Eastside', stops.slice(16).length],
  ];
  const days = [
    { day: 'M', done: 13, delayed: 2, remaining: 5 }, { day: 'T', done: 16, delayed: 1, remaining: 3 },
    { day: 'W', done: 18, delayed: 1, remaining: 1 }, { day: 'T', done: 14, delayed: 2, remaining: 4 },
    { day: 'F', done: 19, delayed: 0, remaining: 1 }, { day: 'S', done: 17, delayed: 1, remaining: 2 },
    { day: 'S', done: 16, delayed: 1, remaining: 3 },
  ];
  const maxArea = Math.max(...areas.map((area) => area[1] as number));
  const metrics = [
    { label: 'Today’s Stops', value: String(stops.length), color: 'text-foreground' },
    { label: 'On Time', value: `${onTimeRate}%`, color: 'text-success' },
    { label: 'Need Action', value: String(open + late), color: 'text-warning' },
    { label: 'Owned Open', value: `${owned}/${open + late + stops.filter((stop) => stop.status === 'enRoute').length}`, color: 'text-info' },
  ];

  return (
    <ScrollView className="flex-1 bg-background" contentContainerClassName="px-4 pt-safe-offset-4 pb-safe-offset-28 gap-3" showsVerticalScrollIndicator={false} scrollIndicatorInsets={{ bottom: 104 }}>
      <Text className="text-2xl font-bold text-foreground">Analytics</Text>
      <Text className="text-sm text-muted">Riverside Community Meals · Dispatch snapshot</Text>
      <View className="flex-row gap-2">{(['7D', '30D', '90D', 'All'] as Period[]).map((value) => <Pressable key={value} onPress={() => setPeriod(value)} className={`flex-1 items-center rounded-full border py-2 ${period === value ? 'border-accent bg-accent' : 'border-border bg-surface'}`}><Text className={`text-xs ${period === value ? 'font-bold text-background' : 'text-muted'}`}>{value}</Text></Pressable>)}</View>
      <View className="flex-row flex-wrap gap-2">{metrics.map((metric) => <View key={metric.label} className="w-[48%] gap-1 rounded-2xl border border-border bg-surface p-3"><Text className="text-xs text-muted">{metric.label}</Text><Text className={`text-2xl font-bold ${metric.color}`}>{metric.value}</Text></View>)}</View>
      <View className="gap-3 rounded-3xl border border-border bg-surface p-4">
        <View className="flex-row items-center justify-between"><Text className="text-base font-semibold text-foreground">Deliveries by Day</Text><Text className="text-xs text-muted">{period} sample</Text></View>
        <View className="flex-row items-end justify-between gap-2">
          {days.map((day, index) => <View key={`${day.day}-${index}`} className="flex-1 items-center gap-1"><View className="h-28 w-full justify-end overflow-hidden rounded-lg bg-background"><View className="w-full rounded-t-md bg-success" style={{ height: `${day.done / 20 * 100}%` }} /><View className="w-full bg-warning" style={{ height: `${day.delayed / 20 * 100}%` }} /><View className="w-full bg-info" style={{ height: `${day.remaining / 20 * 100}%` }} /></View><Text className="text-xs text-muted">{day.day}</Text></View>)}
        </View>
        <View className="flex-row flex-wrap gap-3"><Text className="text-xs text-success">● Delivered</Text><Text className="text-xs text-warning">● Delayed</Text><Text className="text-xs text-info">● Open / en route</Text></View>
        <Text className="text-xs text-muted">Illustrative weekly sample, not historical program data. Today’s figures above come from the editable 20-stop route.</Text>
      </View>
      <View className="gap-2 rounded-2xl border border-border bg-surface p-4"><Text className="text-base font-semibold text-foreground">Average delivery time</Text><Text className="text-2xl font-bold text-info">32 min</Text><Text className="text-xs text-muted">Illustrative sample estimate · validate against real shift records before operational use.</Text></View>
      <View className="flex-row gap-2">
        <View className="flex-1 gap-2 rounded-2xl border border-border bg-surface p-3"><Text className="text-sm font-semibold text-foreground">Delivery Window</Text>{[['8–9 AM', 8], ['9–10 AM', 9], ['10–11 AM', 3]].map(([label, count]) => <View key={String(label)} className="flex-row justify-between"><Text className="text-xs text-muted">{label}</Text><Text className="text-xs font-semibold text-foreground">{count}</Text></View>)}</View>
        <View className="flex-1 gap-2 rounded-2xl border border-border bg-surface p-3"><Text className="text-sm font-semibold text-foreground">Order Type</Text><View className="flex-row justify-between"><Text className="text-xs text-muted">Standard</Text><Text className="text-xs font-semibold text-foreground">18</Text></View><View className="flex-row justify-between"><Text className="text-xs text-muted">2 meals</Text><Text className="text-xs font-semibold text-foreground">2</Text></View><View className="flex-row justify-between"><Text className="text-xs text-muted">Volunteer team</Text><Text className="text-xs font-semibold text-foreground">{volunteers.length}</Text></View></View>
      </View>
      <View className="gap-3 rounded-2xl border border-border bg-surface p-4"><Text className="text-base font-semibold text-foreground">Stops by Area</Text>{areas.map(([name, count]) => <View key={String(name)} className="gap-1"><View className="flex-row justify-between"><Text className="text-xs text-foreground">{name}</Text><Text className="text-xs text-muted">{count} stops</Text></View><View className="h-2 overflow-hidden rounded-full bg-background"><View className="h-full rounded-full bg-info" style={{ width: `${(count as number) / maxArea * 100}%` }} /></View></View>)}</View>
      <View className="gap-2 rounded-2xl border border-success bg-surface p-4"><Text className="text-base font-semibold text-success">Dispatch Insight</Text><Text className="text-sm text-foreground">{open} stops remain open and {stops.filter((stop) => stop.ownerId === null && stop.status !== 'delivered').length} currently have no owner. Review ownership before shift closure.</Text><Text className="text-xs text-muted">Filter period: {period} · Live route totals</Text></View>
      <View className="gap-3 rounded-2xl border border-border bg-surface p-4"><Text className="text-base font-semibold text-foreground">Cloud & AI delivery plan</Text><Text className="text-xs leading-normal text-muted">Prototype status: all records and summaries are local fictional samples. No cloud or speech model is connected.</Text><Text className="text-xs leading-normal text-foreground">Google Cloud: future secure service for stop ownership, audited status events, notification processing and aggregate reporting. NVIDIA: future protected speech/intent inference to suggest a transcript and stop update; a dispatcher confirms every change.</Text><Text className="text-xs leading-normal text-muted">Steps: validate dispatcher workflow → test the 20-stop prototype → security/privacy review → secured cloud and inference pilot → monitored operations pilot. Plan estimate: 8–14 weeks. Team: program lead, dispatcher/volunteer advisors, mobile engineer, cloud security engineer, data engineer, inference engineer and QA.</Text><Text className="text-xs leading-normal text-muted">Risks: inaccurate speech (human confirmation + typed fallback), stale availability (timestamp and coordinator check), unowned stops (visible ownership invariant), sensitive recipient data (minimize, restrict, encrypt, retention controls), weak connectivity (offline-first and safe reconciliation). Test accessibility and diverse voices before any pilot; no automated clinical decisions.</Text><Text className="text-xs leading-normal text-muted">Evidence basis: the challenge statement identifies cancellations and schedule changes as missed-stop causes. Names, counts, history and impact figures here are fictional assumptions, not field research or measured SDG outcomes. SDG 3 link: support continuity of community meal delivery as a well-being service.</Text></View>
    </ScrollView>
  );
}
