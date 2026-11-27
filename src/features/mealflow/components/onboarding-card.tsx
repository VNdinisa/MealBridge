import { Text, View } from 'react-native';

import { Pressable } from '@/components/pressable';

interface OnboardingCardProps {
  onFinish: () => void;
}

export function OnboardingCard({ onFinish }: OnboardingCardProps) {
  return (
    <View className="flex-1 justify-center gap-5 bg-background px-5 pt-safe-offset-4 pb-safe-offset-4">
      <View className="gap-2">
        <Text className="text-xs font-bold tracking-widest text-success">RIVERSIDE COMMUNITY MEALS</Text>
        <Text className="text-4xl font-bold text-foreground">A clear route, from first stop to last.</Text>
        <Text className="text-base leading-6 text-muted">MealFlow helps the dispatch team keep every meal and every volunteer accounted for.</Text>
      </View>
      <View className="gap-3 rounded-3xl border border-border bg-surface p-4">
        <View className="gap-1"><Text className="text-base font-semibold text-success">01 · Follow the route</Text><Text className="text-sm leading-5 text-muted">The delivery board shows progress, status, and a named owner for every open stop.</Text></View>
        <View className="h-px bg-border" />
        <View className="gap-1"><Text className="text-base font-semibold text-info">02 · Adjust the team</Text><Text className="text-sm leading-5 text-muted">Update volunteer availability and reassign stops when plans change.</Text></View>
        <View className="h-px bg-border" />
        <View className="gap-1"><Text className="text-base font-semibold text-warning">03 · Review every update</Text><Text className="text-sm leading-5 text-muted">Turn a reported delivery or delay into a stop change only after you confirm it.</Text></View>
      </View>
      <Text className="text-xs leading-5 text-muted">This sample route stays on this device. Names and delivery details are fictional.</Text>
      <Pressable onPress={onFinish} className="items-center rounded-full bg-accent py-4"><Text className="text-base font-bold text-background">Start today’s route</Text></Pressable>
      <Text className="text-center text-xs text-muted">You can review the route details any time in Deliveries.</Text>
    </View>
  );
}
