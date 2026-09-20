import { useRouter } from 'expo-router';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface MeetingProps {
  room: string;
  /** 通話を閉じるとき（通話終了操作・endsAt到達）に、直前の画面へ戻る前に1回だけ呼ばれる */
  onClose?: () => void;
  /** この時刻（ミリ秒）に達したら通話を自動で閉じる（ランダムコールの有効時間の満了） */
  endsAt?: number;
}

interface JitsiMeetExternalApiInstance {
  addEventListener: (event: string, listener: (...args: unknown[]) => void) => void;
  dispose: () => void;
}

declare global {
  interface Window {
    JitsiMeetExternalAPI?: new (
      domain: string,
      options: Record<string, unknown>
    ) => JitsiMeetExternalApiInstance;
  }
}

// ネイティブ版（Meeting.tsx）のJitsiMeetingコンポーネントと同じサーバーを使う
const JITSI_DOMAIN = 'meet.jit.si';
const JITSI_EXTERNAL_API_SRC = `https://${JITSI_DOMAIN}/external_api.js`;

function loadJitsiExternalApi(): Promise<void> {
  if (window.JitsiMeetExternalAPI) {
    return Promise.resolve();
  }

  const existingScript = document.querySelector<HTMLScriptElement>(
    `script[src="${JITSI_EXTERNAL_API_SRC}"]`
  );
  if (existingScript) {
    return new Promise((resolve, reject) => {
      existingScript.addEventListener('load', () => resolve());
      existingScript.addEventListener('error', () => reject(new Error('failed to load existing script')));
    });
  }

  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = JITSI_EXTERNAL_API_SRC;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error(`failed to load ${JITSI_EXTERNAL_API_SRC}`));
    document.head.appendChild(script);
  });
}

type Status = 'loading' | 'ready' | 'error';

const Meeting = ({ room, onClose, endsAt }: MeetingProps) => {
  const router = useRouter();
  // react-native-webのViewは実DOM上ではdivとしてレンダリングされ、
  // refはその実DOMノードを指す（JitsiMeetExternalAPIのparentNodeに渡すため必要）
  const containerRef = useRef<any>(null);
  const apiRef = useRef<JitsiMeetExternalApiInstance | null>(null);
  const [status, setStatus] = useState<Status>('loading');
  // onClose が変わってもJitsiを作り直さないよう、最新の値をrefで参照する
  const onCloseRef = useRef(onClose);
  // readyToClose と endsAt が重なっても、onClose と router.back() を二重に実行しない
  const closedRef = useRef(false);

  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);

  const closeMeeting = useCallback(() => {
    if (closedRef.current) {
      return;
    }
    closedRef.current = true;
    apiRef.current?.dispose();
    apiRef.current = null;
    onCloseRef.current?.();
    router.back();
  }, [router]);

  useEffect(() => {
    let cancelled = false;

    loadJitsiExternalApi()
      .then(() => {
        if (cancelled) {
          return;
        }
        if (!containerRef.current || !window.JitsiMeetExternalAPI) {
          setStatus('error');
          return;
        }

        const api = new window.JitsiMeetExternalAPI(JITSI_DOMAIN, {
          roomName: room,
          parentNode: containerRef.current,
          width: '100%',
          height: '100%',
        });
        apiRef.current = api;
        api.addEventListener('readyToClose', closeMeeting);
        setStatus('ready');
      })
      .catch(() => {
        if (!cancelled) {
          setStatus('error');
        }
      });

    return () => {
      cancelled = true;
      apiRef.current?.dispose();
      apiRef.current = null;
    };
  }, [room, closeMeeting]);

  useEffect(() => {
    if (endsAt === undefined) {
      return;
    }
    const timer = setTimeout(closeMeeting, Math.max(0, endsAt - Date.now()));
    return () => clearTimeout(timer);
  }, [endsAt, closeMeeting]);

  return (
    <View style={styles.container}>
      <View ref={containerRef} style={StyleSheet.absoluteFill} />
      {status !== 'ready' && (
        <View style={[StyleSheet.absoluteFill, styles.overlay]}>
          <Text style={styles.text}>
            {status === 'loading'
              ? '読み込み中...'
              : 'ビデオ通話を読み込めませんでした。ネットワーク接続、またはブラウザのカメラ/マイクの使用許可を確認してください。'}
          </Text>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  overlay: {
    alignItems: 'center',
    backgroundColor: '#fff',
    justifyContent: 'center',
  },
  text: {
    color: '#555',
    fontSize: 16,
    padding: 24,
    textAlign: 'center',
  },
});

export default Meeting;
