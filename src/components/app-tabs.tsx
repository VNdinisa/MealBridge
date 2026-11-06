import { NativeTabs } from 'expo-router/unstable-native-tabs';
import { useThemeColor } from 'heroui-native';

export function AppTabs() {
  const accent = useThemeColor('accent');
  return (
    <NativeTabs tintColor={accent}>
      <NativeTabs.Trigger name="index" disableAutomaticContentInsets>
        <NativeTabs.Trigger.Label>Deliveries</NativeTabs.Trigger.Label>
        <NativeTabs.Trigger.Icon sf={{ default: 'house', selected: 'house.fill' }} md="home" />
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="volunteers" disableAutomaticContentInsets>
        <NativeTabs.Trigger.Label>Volunteers</NativeTabs.Trigger.Label>
        <NativeTabs.Trigger.Icon sf={{ default: 'person.2', selected: 'person.2.fill' }} md="groups" />
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="voice" disableAutomaticContentInsets>
        <NativeTabs.Trigger.Label>Voice Hub</NativeTabs.Trigger.Label>
        <NativeTabs.Trigger.Icon sf={{ default: 'waveform', selected: 'waveform' }} md="mic" />
      </NativeTabs.Trigger>
      <NativeTabs.Trigger name="analytics" disableAutomaticContentInsets>
        <NativeTabs.Trigger.Label>Analytics</NativeTabs.Trigger.Label>
        <NativeTabs.Trigger.Icon sf={{ default: 'chart.bar.fill', selected: 'chart.bar.fill' }} md="bar_chart" />
      </NativeTabs.Trigger>
    </NativeTabs>
  );
}
