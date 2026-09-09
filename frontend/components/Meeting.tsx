import React, { useCallback, useRef } from 'react';

import { JitsiMeeting } from '@jitsi/react-native-sdk';

import { useRouter } from 'expo-router';


interface MeetingProps {
  room: string;
}

const Meeting = ( { room }: MeetingProps ) => {
  const jitsiMeeting = useRef(null);
  const router = useRouter();

  const onReadyToClose = useCallback(() => {
    // @ts-ignore
    jitsiMeeting.current?.close();
    router.back();
  }, [router]);

  const onEndpointMessageReceived = useCallback(() => {
      console.log('You got a message!');
  }, []);

  const eventListeners = {
        onReadyToClose,
        onEndpointMessageReceived
  };

  // NOTE: No NavigationIndependentTree wrapper is needed here. Jitsi's own
  // NavigationContainers already pass `independent={true}` (React Navigation v6
  // API), which works as long as Jitsi resolves the real v6
  // `@react-navigation/core`. That is guaranteed by
  // EXPO_ROUTER_DISABLE_RN_NAVIGATION_CHECK=1 in `frontend/.env`, which stops
  // Expo CLI from redirecting `@react-navigation/core` to expo-router's
  // vendored v7 core (where the v6 `independent` prop is ignored).
  return (
      // @ts-ignore
      <JitsiMeeting
          config = {{
            hideConferenceTimer: true,
            // customToolbarButtons: [
            //   {
            //     icon: "https://w7.pngwing.com/pngs/987/537/png-transparent-download-downloading-save-basic-user-interface-icon-thumbnail.png",
            //     id: "btn1",
            //     text: "Button one"
            //   }, {
            //     icon: "https://w7.pngwing.com/pngs/987/537/png-transparent-download-downloading-save-basic-user-interface-icon-thumbnail.png",
            //     id: "btn2",
            //     text: "Button two"
            //   }
            // ],
            // toolbarButtons: [ 'microphone', 'camera', 'screensharing', 'overflowmenu', 'hangup' ],
            whiteboard: {
                enabled: true,
                collabServerBaseUrl: "https://meet.jit.si/",
            },
            analytics: {
                disabled: true
            }
          }}
          eventListeners = { eventListeners as any }
          flags = {{
              "audioMute.enabled": true,
              "ios.screensharing.enabled": true,
              "fullscreen.enabled": false,
              "audioOnly.enabled": false,
              "android.screensharing.enabled": true,
              "pip.enabled": true,
              "pip-while-screen-sharing.enabled": true,
              "conference-timer.enabled": true,
              "close-captions.enabled": false,
              "toolbox.enabled": true,
          }}
          ref = { jitsiMeeting }
          style = {{ flex: 1 }}
          room = { room }
          serverURL = { "https://meet.jit.si/" } />
  );
};

export default Meeting;