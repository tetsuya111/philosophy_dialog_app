import { useRouter } from 'expo-router';
import React, { useEffect, useRef, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';

interface MeetingProps {
  room: string;
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

const Meeting = ({ room }: MeetingProps) => {
  const router = useRouter();
  // react-native-webのViewは実DOM上ではdivとしてレンダリングされ、
  // refはその実DOMノードを指す（JitsiMeetExternalAPIのparentNodeに渡すため必要）
  const containerRef = useRef<any>(null);
  const apiRef = useRef<JitsiMeetExternalApiInstance | null>(null);
  const [status, setStatus] = useState<Status>('loading');

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
        api.addEventListener('readyToClose', () => {
          router.back();
        });
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
  }, [room, router]);

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
