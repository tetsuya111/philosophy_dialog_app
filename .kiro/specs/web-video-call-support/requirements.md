# Web版ビデオ通話対応 要件定義書

## 前提の確認（「Android版とWeb版は一つのプロジェクトに共存できるか」について）

**できる。というより、既にできている。** 本プロジェクトはExpo（React Native, TypeScript, expo-router）で構築されており、Expoは元々iOS/Android/Webを単一コードベースから提供する仕組みを持つ（[docs/frontend.md](../../../docs/frontend.md)参照）。

- `npm run web`で既にWebビルドが起動できる（`frontend/package.json`）。
- プラットフォーム固有の実装は`Component.web.tsx`のようにファイル名で出し分ける規約が既にあり、まさに今回対象の`frontend/components/Meeting.tsx`（ネイティブ用）と`frontend/components/Meeting.web.tsx`（Web用）がその実例。
- したがって「共存させる」ための新規の仕組みは不要。両者は既に同じ`app/`・`components/`配下で共存しており、ビルド時にプラットフォームごとに`Meeting.tsx`か`Meeting.web.tsx`のどちらかへ自動的に振り分けられる。

**ただし現状、Web版の`Meeting.web.tsx`は「ビデオ会議はモバイルアプリでのみご利用いただけます」という非対応メッセージを表示するだけで、Web版では実際にビデオ通話ができない。** 本要件定義書は、「プロジェクトとしての共存」ではなく「Web版でも実際にビデオ通話機能を使えるようにする」ことを目的とする（この解釈で認識合わせ済み）。

## 背景・課題（Working Backwards）

`@jitsi/react-native-sdk`はネイティブモジュールであり、Android/iOSのdev client/ストアアプリでのみ動作する（[manuals/video-call-testing.md](../../../manuals/video-call-testing.md)）。一方、本アプリはExpoでWeb版もビルド可能であるにもかかわらず、Web版ユーザーは「モバイルアプリでのみ利用可能」という案内を見るだけで、哲学対話（ビデオ通話）という本アプリの中核機能（[.kiro/steering/product.md](../../steering/product.md)）を一切利用できない。

Jitsi Meetは元々Web向けのビデオ会議サービスであり、ブラウザから`https://meet.jit.si/<room>`に直接アクセスするだけで通話に参加できる。この性質を利用すれば、ネイティブモジュールを使わずにWeb版でも同じJitsiのルームに参加させることができるはずである。

## スコープ / Non-Goals

**スコープ:**

- `frontend/components/Meeting.web.tsx`を、現在の非対応メッセージ表示から、実際にJitsi Meetの通話に参加できる実装に置き換える。
- Android版（`Meeting.tsx`）と同じルーム名で、Web版からも同じ通話に参加できること。
- Web埋め込みには、Jitsiが提供する`https://meet.jit.si/external_api.js`（Jitsi Meet API）を使用する（単純な`<iframe src="https://meet.jit.si/<room>">`のみの埋め込みは採用しない。終了イベント検知等をネイティブ版の`onReadyToClose`と揃えやすいため、要件確認時にこの方式を採用することで合意済み）。

**Non-Goals（今回は対応しない）:**

- iOS版の対応状況の確認（[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)同様、今回はAndroid/Webのみを対象とし、iOSは別途）。
- Android版で発生している`Element type is invalid`クラッシュの修正そのもの（[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)で別途対応中。本要件はWeb版を対象とし、Android版の対応状況に依存しない）。
- Web版通話画面のUI/UXをネイティブ版と完全に一致させること（Jitsi側が提供するWeb UIをそのまま利用するため、ツールバー等の見た目はネイティブ版の`JitsiMeeting`コンポーネントとは異なりうる）。
- マッチング機能とビデオ通話画面の統合（[.kiro/specs/philosophy-dialog-app/requirements.md](../philosophy-dialog-app/requirements.md)の既知の課題であり、別タスク）。
- Web版向けの新しいネイティブ依存の追加（`react-native-webrtc`等のWeb版ポリフィルの導入は行わず、Jitsiが提供するWeb向け埋め込み手段を利用する前提とする。具体的な埋め込み方式はdesign.mdで検討）。

## 成功指標

新機能ではあるが計測基盤がないため（[.kiro/specs/philosophy-dialog-app/requirements.md](../philosophy-dialog-app/requirements.md)の「成功指標」と同様の理由）、以下の動作確認をもって成功とする。

- `npm run web`で起動したWeb版で、Home画面の「一人で対話を開始する」ボタンから遷移した際、「モバイルアプリでのみご利用いただけます」ではなく、実際にJitsi Meetの通話画面（カメラ映像・マイク入力）が表示される。
- Android版アプリと同じルーム名を指定してWeb版からアクセスした場合に、同じ通話に参加できる（映像・音声が相互に届く）。

## ユーザーストーリー・受け入れ基準

**ユーザーストーリー**: As a Webブラウザからアプリを使うユーザー, I want ブラウザからもビデオ通話に参加したい, so that モバイルアプリをインストールしなくても哲学対話ができる。

- WHEN ユーザーがWeb版でHome画面の「一人で対話を開始する」ボタンをタップし、Meeting画面（`app/meeting.tsx`）が表示されたとき THE SYSTEM SHALL `Meeting.web.tsx`経由でJitsi Meetの通話UIを表示し、カメラ・マイクの使用許可をブラウザに求める。
- WHEN ユーザーがブラウザのカメラ・マイク使用を許可したとき THE SYSTEM SHALL 指定されたルーム名の通話に参加し、映像・音声を送受信する。
- IF ブラウザがカメラ・マイクの使用を許可しない、またはWebRTCに対応していない場合 THEN THE SYSTEM SHALL エラーであることが分かる表示をする（現状の「モバイルアプリでのみ」という誤った案内文言のまま失敗させない）。

**ユーザーストーリー**: As a 開発者, I want Android版とWeb版で同じルーム名の扱いを共有したい, so that プラットフォームを問わず同じ通話に参加できる。

- WHEN Android版・Web版の双方で同一のルーム名（例: `solo-<timestamp>-<random>`）が渡されたとき THE SYSTEM SHALL 双方とも同じJitsiサーバー（`https://meet.jit.si/`）・同じルーム名で通話に参加する。

## 非機能要件

- Web版の実装は、Android版（`@jitsi/react-native-sdk`）に新たな依存や設定変更を要求しないこと（プラットフォーム別ファイルによる分離を維持する）。
- `app.json`の`web.output: "static"`（静的サイト出力）の制約内で動作すること（サーバーサイドの処理を新たに必要としない）。

