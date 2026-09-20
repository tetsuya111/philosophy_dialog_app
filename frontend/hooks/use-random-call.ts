import { useFocusEffect } from 'expo-router';
import { useCallback, useEffect, useRef, useState } from 'react';

import {
  cancelQueue,
  enterCall,
  getStatus,
  joinQueue,
  stateFromError,
  type RandomCallState,
} from '@/lib/random-call';

// マッチング成立を5秒以内に画面へ反映するためのポーリング間隔（requirements ストーリー3-8）
const POLL_INTERVAL_MS = 3000;

const TIMEOUT_NOTICE = '相手が見つかりませんでした。もう一度お試しください。';
const NETWORK_ERROR_NOTICE = '通信に失敗しました。時間をおいて再度お試しください。';

function serverClockOffset(state: RandomCallState): number {
  return Date.parse(state.server_time) - Date.now();
}

export interface EnteredRoom {
  roomName: string;
  /** 通話の有効期限（端末時刻に補正したミリ秒） */
  endsAt: number;
}

/**
 * Home画面のランダムコール（待機・マッチング・入室）の状態管理。
 * 画面にフォーカスがある間だけ、待機中・マッチング済み・通話中の状態をポーリングする。
 */
export function useRandomCall() {
  const [state, setState] = useState<RandomCallState | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [focused, setFocused] = useState(false);
  const [now, setNow] = useState(() => Date.now());
  // サーバー時刻 - 端末時刻
  const [clockOffset, setClockOffset] = useState(0);

  const prevStatusRef = useRef<RandomCallState['status'] | null>(null);
  const cancelingRef = useRef(false);
  // リクエストの発行順。古いポーリング結果が、後から実行した操作の結果を上書きしないようにする
  const requestSeqRef = useRef(0);

  const apply = useCallback((next: RandomCallState) => {
    setClockOffset(serverClockOffset(next));
    // waiting → none になる経路は「取りやめ」と「タイムアウト」だけなので、取りやめ中でなければタイムアウト
    if (prevStatusRef.current === 'waiting' && next.status === 'none' && !cancelingRef.current) {
      setNotice(TIMEOUT_NOTICE);
    }
    prevStatusRef.current = next.status;
    setState(next);
    setNow(Date.now());
  }, []);

  const refresh = useCallback(async () => {
    const seq = ++requestSeqRef.current;
    try {
      const next = await getStatus();
      if (seq === requestSeqRef.current) {
        apply(next);
      }
    } catch {
      // ポーリング中の一時的な失敗は次回の取得で回復するため表示しない
    }
  }, [apply]);

  // 操作（参加・取りやめ・入室）を実行し、結果の状態を反映する。失敗時は理由を表示する
  const run = useCallback(
    async (action: () => Promise<RandomCallState>): Promise<RandomCallState | null> => {
      setBusy(true);
      requestSeqRef.current += 1;
      try {
        const next = await action();
        apply(next);
        return next;
      } catch (error) {
        const current = stateFromError(error);
        if (current) {
          apply(current);
          setNotice(current.detail ?? null);
        } else {
          setNotice(NETWORK_ERROR_NOTICE);
        }
        return null;
      } finally {
        setBusy(false);
      }
    },
    [apply]
  );

  // 画面に戻るたびに最新の状態を取得する（アプリ再起動・通話画面からの復帰。ストーリー4-8）
  useFocusEffect(
    useCallback(() => {
      setFocused(true);
      void refresh();
      return () => setFocused(false);
    }, [refresh])
  );

  const status = state?.status ?? 'none';
  const active = focused && status !== 'none';

  useEffect(() => {
    if (!active) {
      return;
    }
    const poll = setInterval(() => void refresh(), POLL_INTERVAL_MS);
    const tick = setInterval(() => setNow(Date.now()), 1000);
    return () => {
      clearInterval(poll);
      clearInterval(tick);
    };
  }, [active, refresh]);

  const join = useCallback(async () => {
    setNotice(null);
    await run(joinQueue);
  }, [run]);

  const cancel = useCallback(async () => {
    setNotice(null);
    cancelingRef.current = true;
    try {
      await run(cancelQueue);
    } finally {
      cancelingRef.current = false;
    }
  }, [run]);

  const enter = useCallback(async (): Promise<EnteredRoom | null> => {
    setNotice(null);
    const next = await run(enterCall);
    if (!next?.room) {
      return null;
    }
    return {
      roomName: next.room.room_name,
      endsAt: Date.parse(next.room.expires_at) - serverClockOffset(next),
    };
  }, [run]);

  const expiresAt = state?.waiting?.expires_at ?? state?.room?.expires_at;
  const remainingMs = expiresAt ? Math.max(0, Date.parse(expiresAt) - (now + clockOffset)) : null;

  return { status, remainingMs, notice, busy, join, cancel, enter };
}
