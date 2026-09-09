import { useLocalSearchParams } from 'expo-router';

import Meeting from '@/components/Meeting';

export default function MeetingScreen() {
  const { room } = useLocalSearchParams<{ room: string }>();

  return <Meeting room={room} />;
}
