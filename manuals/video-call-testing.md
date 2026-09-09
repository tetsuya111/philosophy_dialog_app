# ビデオ通話（Jitsi Meet SDK）のテスト手順

`frontend/components/Meeting.tsx` が実装しているビデオ通話（`@jitsi/react-native-sdk`）を手元で動作確認するための手順。

## 前提・制約

- `@jitsi/react-native-sdk` はネイティブモジュールのため、**Expo Goでは動作しない**。ネイティブのdev clientビルド（`npx expo run:android` / `npx expo run:ios`）が必要。
- **Web版は別実装**。`frontend/components/Meeting.web.tsx` は`@jitsi/react-native-sdk`ではなく、Jitsiが提供する`https://meet.jit.si/external_api.js`（Jitsi Meet API）を使って通話に参加する（[.kiro/specs/web-video-call-support/](../.kiro/specs/web-video-call-support/)参照）。`npm run web`で起動すればブラウザから確認できる。
- Home画面（`app/(tabs)/index.tsx`）の「一人で対話を開始する」ボタンから、マッチングを介さず単独でMeeting画面（`app/meeting.tsx`）に入れる。ルーム名は`solo-<timestamp>-<random>`の形式で自動生成される。

## 手順

### 1. ネイティブdev clientをビルド・起動する

```bash
cd frontend
npx expo run:android   # frontend/android/ は生成済みなのでそのままビルド可能
# macOSの場合: npx expo run:ios
```

初回起動時、カメラ・マイクの権限を求められたら許可する。ビルドに失敗する場合は `npx expo prebuild --clean` を試す。

**Windows + Androidエミュレータの場合**、環境によっては下記「トラブルシューティング」の`Reloading`で止まる問題が発生するため、代わりに以下を使うと確実（詳細は後述）。

```bash
npm run android:win
```

### 2. アプリ上でMeeting画面に入る

ビルドしたdev clientを起動し、Home画面の「一人で対話を開始する」ボタンをタップしてMeeting画面に入る。カメラ映像・マイク入力がJitsi Meetの通話画面上に表示されることを確認する。ルーム名は起動時のログ、またはURL（`/meeting?room=...`）から確認できる。

### 3. 2人での通話を確認する

`Meeting.tsx` の `serverURL` は公開サーバー `https://meet.jit.si/` を指しているため、2台目のアプリ端末を用意しなくても、PCやスマホのブラウザで同じルーム名のURL（例: `https://meet.jit.si/<手順2で確認したルーム名>`）を開けば、アプリ側と映像・音声が繋がるかを確認できる。

- アプリ側の映像・音声がブラウザ側に届くか
- ブラウザ側の映像・音声がアプリ側に届くか
- 通話終了操作（`onReadyToClose`）でHome画面に戻るか

### 4. Web版を確認する

```bash
cd frontend
npm run web
```

ブラウザでHome画面の「一人で対話を開始する」ボタンから遷移し、Jitsi Meetの通話画面（カメラ映像・マイク入力）が表示されることを確認する（カメラ・マイクの使用許可を求められたら許可する）。

- 別のブラウザタブ、または別端末のブラウザで同じルーム名のURL（`https://meet.jit.si/<ルーム名>`）を開き、映像・音声が双方向に届くかを確認する。
- 通話終了操作でHome画面に戻るかを確認する。
- スクリプト（`https://meet.jit.si/external_api.js`）が読み込めない場合や、カメラ/マイクの許可が得られない場合は、「ビデオ通話を読み込めませんでした」というエラー表示になることを確認する。

## トラブルシューティング

- カメラ/マイクが起動しない: OS側の権限設定（Android設定アプリ／iOS設定アプリ）でアプリに許可が下りているか確認する。
- ビルドが通らない: `frontend/android/` が古い可能性があるため `npx expo prebuild --clean` → `npx expo run:android` を再実行する。
- 通話にそもそも参加できない: 端末がインターネットに到達できているか、`https://meet.jit.si/` へブラウザから直接アクセスできるかを確認する（社内ネットワーク等でWebRTCがブロックされている場合がある）。
- **Androidエミュレータで起動後「Reloading...」から進まない**: Metro（`localhost:8081`）への接続に失敗している。原因調査の結果、このプロジェクトの開発機（Windows + ノートン360）では、エミュレータがデフォルトで使う`10.0.2.2:8081`経由の接続で、chunked encodingのレスポンスが壊れて失敗する事象を確認した（`java.net.ProtocolException: Expected leading [0-9a-fA-F] character but was 0xd`。生のTCP接続・pingは通るため、単純な遮断ではなくHTTP通信内容を検査するセキュリティソフトのWeb保護機能が原因と考えられる）。`adb reverse tcp:8081 tcp:8081`を設定した上で、dev clientに`localhost:8081`への接続を明示的に指示すると回避できる。
  - この回避策を自動化したのが`frontend/scripts/run-android.ps1`（`npm run android:win`）。`npx expo run:android`の代わりにこれを使うと、adb reverseの設定とlocalhost接続の強制を自動で行う。
  - 手動で直す場合:
    ```bash
    adb reverse tcp:8081 tcp:8081
    adb shell am start -a android.intent.action.VIEW -d "frontend://expo-development-client/?url=http%3A%2F%2Flocalhost%3A8081"
    ```
  - 同様の症状が他の開発機で起きる場合、ノートン等のセキュリティソフトのWeb保護/HTTPスキャン機能を一時的に無効化して切り分けるのも有効。
