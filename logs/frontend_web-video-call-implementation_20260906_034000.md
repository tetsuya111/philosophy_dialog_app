# Web版ビデオ通話（Jitsi Meet API）の実装

## 何を

`.kiro/specs/web-video-call-support/tasks.md`のタスク1〜7を実施。

- `frontend/components/Meeting.web.tsx`を、「モバイルアプリでのみご利用いただけます」という非対応メッセージ表示から、`https://meet.jit.si/external_api.js`（Jitsi Meet API）を動的に読み込んで実際に通話に参加できる実装に置き換えた。`react-native-web`が描画する`View`の実DOMノードを`parentNode`として渡し、`readyToClose`イベントで`expo-router`の`router.back()`を呼ぶことで、ネイティブ版（`Meeting.tsx`）の`onReadyToClose`と挙動を揃えた。スクリプト読み込み中・失敗時の表示も実装。
- `docs/frontend.md`のアーキテクチャ節に、Web版は`external_api.js`を使う旨を追記。
- `manuals/video-call-testing.md`に、Web版（`npm run web`）での確認手順（2ブラウザ間での映像・音声疎通、終了操作での画面遷移、エラー表示の確認）を追記。

`npx eslint`・`npx tsc --noEmit`で本ファイル起因のエラー・警告がないことを確認済み（`components/hello-wave.tsx`等に出ている`react-native-reanimated`関連のエラーは、並行して別セッションが進めている`fix-jitsi-meeting-crash`スペックの作業によるものであり、本タスクの対象外）。

## なぜ

ユーザーからの依頼（`.kiro/specs/web-video-call-support/`のtasks.mdに基づく実装）。Web版でも本アプリの中核機能であるビデオ通話を使えるようにするため。
