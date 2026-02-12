import React, { useEffect, useRef } from 'react';
import './JitsiMeeting.css';

const JitsiMeeting = ({ roomName, roomId, domain = 'meet.jit.si', onLeave }) => {
  const jitsiContainerRef = useRef(null);
  const jitsiApiRef = useRef(null);

  useEffect(() => {
    // Jitsi Meet External APIをロード
    const loadJitsiScript = () => {
      return new Promise((resolve, reject) => {
        if (window.JitsiMeetExternalAPI) {
          resolve();
          return;
        }

        const script = document.createElement('script');
        script.src = 'https://meet.jit.si/external_api.js';
        script.async = true;
        script.onload = resolve;
        script.onerror = reject;
        document.body.appendChild(script);
      });
    };

    const initJitsi = async () => {
      try {
        await loadJitsiScript();

        if (jitsiApiRef.current) {
          jitsiApiRef.current.dispose();
        }

        const options = {
          roomName: roomName,
          width: '100%',
          height: '100%',
          parentNode: jitsiContainerRef.current,
          configOverwrite: {
            startWithAudioMuted: false,
            startWithVideoMuted: false,
            enableWelcomePage: false,
            prejoinPageEnabled: false,
            disableDeepLinking: true,
          },
          interfaceConfigOverwrite: {
            SHOW_JITSI_WATERMARK: false,
            SHOW_WATERMARK_FOR_GUESTS: false,
            TOOLBAR_BUTTONS: [
              'microphone',
              'camera',
              'closedcaptions',
              'desktop',
              'fullscreen',
              'fodeviceselection',
              'hangup',
              'profile',
              'chat',
              'recording',
              'livestreaming',
              'etherpad',
              'sharedvideo',
              'settings',
              'raisehand',
              'videoquality',
              'filmstrip',
              'stats',
              'shortcuts',
              'tileview',
              'download',
              'help',
              'mute-everyone',
            ],
          },
        };

        const api = new window.JitsiMeetExternalAPI(domain, options);
        jitsiApiRef.current = api;

        // イベントリスナー
        api.addEventListener('readyToClose', () => {
          if (onLeave) {
            onLeave();
          }
        });

        api.addEventListener('participantLeft', () => {
          console.log('Participant left');
        });

      } catch (error) {
        console.error('Failed to load Jitsi Meet:', error);
      }
    };

    initJitsi();

    return () => {
      if (jitsiApiRef.current) {
        jitsiApiRef.current.dispose();
        jitsiApiRef.current = null;
      }
    };
  }, [roomName, domain, onLeave]);

  return (
    <div className="jitsi-container">
      <div className="jitsi-header">
        <h2>ルーム: {roomName}</h2>
        <button className="leave-btn" onClick={onLeave}>
          退出
        </button>
      </div>
      <div ref={jitsiContainerRef} className="jitsi-meet" />
    </div>
  );
};

export default JitsiMeeting;
