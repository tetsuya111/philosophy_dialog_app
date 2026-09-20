import { useLocalSearchParams } from 'expo-router';
import { useCallback } from 'react';

import Meeting from '@/components/Meeting';
import { leaveCall } from '@/lib/random-call';

export default function MeetingScreen() {
  // mode / endsAt はランダムコールから遷移したときのみ渡される（「一人で対話を開始する」では room のみ）
  const { room, mode, endsAt } = useLocalSearchParams<{ room: string; mode?: string; endsAt?: string }>();
  const isRandomCall = mode === 'random';

  const handleClose = useCallback(() => {
    // 通話終了をバックエンドに記録する。失敗しても有効時間の満了で「未参加」に戻るため画面遷移は妨げない
    leaveCall().catch(() => {});
  }, []);

  return (
    <Meeting
      room={room}
      onClose={isRandomCall ? handleClose : undefined}
      endsAt={isRandomCall && endsAt ? Number(endsAt) : undefined}
    />
  );
}
