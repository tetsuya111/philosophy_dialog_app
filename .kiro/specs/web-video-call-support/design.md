# Web版ビデオ通話対応 設計ドキュメント

## TL;DR

`frontend/components/Meeting.web.tsx`を、Jitsiが提供する`https://meet.jit.si/external_api.js`（Jitsi Meet API）を使った実装に置き換える。`react-native-web`が描画する`View`のDOMノードを`parentNode`としてAPIに渡し、iframeベースの通話UIをその中に埋め込む。新規の依存追加は行わず、既存の`.web.tsx`によるプラットフォーム分岐の枠組みの中で完結させる（[requirements.md](requirements.md)で合意済みの方針）。

## Non-Goals

[requirements.md](requirements.md)のNon-Goalsを引き継ぐ。加えて設計上、以下は対象外とする。

- `react-native-webview`など新規ライブラリの追加（[requirements.md](requirements.md)の非機能要件の通り、新規依存を避ける）。
- Jitsi Meet APIの全イベント・全設定オプションへの対応（終了検知（`readyToClose`）など、ネイティブ版の`Meeting.tsx`が使っているイベント・設定と対応の取れる範囲に留める）。

## 検討した代替案

### 案A: Jitsi Meet External API（`external_api.js`）を`View`のDOMノードに埋め込む（採用）

- 長所: [requirements.md](requirements.md)で合意済みの方式。iframeの生成・破棄をAPIが管理してくれる上、`readyToClose`等のイベントをJSで受け取れるため、ネイティブ版の`onReadyToClose`と同等の挙動をWeb版でも再現できる。新規依存が不要（スクリプトを動的に読み込むだけ）。
- 短所: サードパーティスクリプト（`https://meet.jit.si/external_api.js`）の読み込みに依存するため、そのスクリプトの仕様変更やCDN障害の影響を受ける。

### 案B: 単純な`<iframe src="https://meet.jit.si/<room>">`のみ埋め込む

- 却下理由: [requirements.md](requirements.md)の要件確認時に、終了イベント検知等をネイティブ版と揃えやすい案Aを採用することで合意済みのため不採用。

### 案C: `react-native-webview`のWeb実装を利用する

- 却下理由: `react-native-webview`はWebプラットフォームでもiframeベースの実装を提供するが、今回はWeb画面1箇所のためだけに新規ライブラリを追加することになり、[requirements.md](requirements.md)の非機能要件（新規依存を増やさない）に反する。`external_api.js`＋素の`View`で同等のことができるため採用しない。

## 設計

### 1. Jitsi Meet APIスクリプトの読み込み

`frontend/components/Meeting.web.tsx`内（またはWeb専用の小さなヘルパー）で、`https://meet.jit.si/external_api.js`を動的に`<script>`タグとして`document.head`に追加する。

- `window.JitsiMeetExternalAPI`が既に存在する場合は再読み込みしない（Meeting画面の再訪問・Fast Refreshでの二重読み込み防止）。
- 読み込み中は簡単なローディング表示、読み込み失敗時はエラー表示にする（[requirements.md](requirements.md)の「IF ブラウザがカメラ・マイクの使用を許可しない、またはWebRTCに対応していない場合」に加えて、スクリプト読み込み自体の失敗もこの分岐で扱う）。

### 2. `Meeting.web.tsx`の実装

- propsは既存の`{ room: string }`のまま変更しない（`app/meeting.tsx`は現状すでにプラットフォーム共通で`room`のみを渡す実装になっており、変更不要）。
- `useRef`でコンテナ用の`View`への参照を保持し、スクリプト読み込み完了後に`new window.JitsiMeetExternalAPI('meet.jit.si', { roomName: room, parentNode: <Viewの実DOMノード>, width: '100%', height: '100%', configOverwrite: { ... }, interfaceConfigOverwrite: { ... } })`でAPIインスタンスを生成する。
- ネイティブ版（`Meeting.tsx`）の`serverURL`（`https://meet.jit.si/`）と同じドメインを使う。
- `api.addEventListener('readyToClose', ...)`で、ネイティブ版の`onReadyToClose`と同様に`expo-router`の`useRouter().back()`を呼ぶ（Web版・ネイティブ版で「終了操作で前の画面に戻る」という挙動を揃える）。
- コンポーネントのアンマウント時（`useEffect`のクリーンアップ）に`api.dispose()`を呼び、APIインスタンス・iframeを破棄する。

### 3. ルーム名の共有

`app/meeting.tsx`は変更不要。Android版・Web版とも同じ`room`パラメータを`Meeting`コンポーネントに渡す既存の仕組みをそのまま使う（[requirements.md](requirements.md)の「開発者」ストーリーの受け入れ基準を満たす）。

## 横断的関心事

- **セキュリティ・プライバシー**: `https://meet.jit.si/external_api.js`というサードパーティスクリプトを読み込む。通話サーバー自体（`https://meet.jit.si/`）は既にネイティブ版（`Meeting.tsx`の`serverURL`）でも使用しているものと同一で、新たなデータ送信先が増えるわけではない。
- **パフォーマンス・スケーラビリティ**: スクリプトはページ内で一度だけ読み込む（`window.JitsiMeetExternalAPI`の存在チェック）。対象範囲外（本要件のスコープはWeb版1画面のみ）。
- **オブザーバビリティ**: 影響なし（[requirements.md](requirements.md)の通り、自動収集の仕組みは導入しない）。
- **テスト戦略**: 手動確認のみ。[manuals/video-call-testing.md](../../../manuals/video-call-testing.md)にWeb版の確認手順（`npm run web`で起動し、別のブラウザタブ/別端末から同じルーム名の`https://meet.jit.si/<room>`にアクセスして映像・音声が繋がることを確認）を追記する（実装タスクの一つとする）。
- **ロールアウト計画**: `Meeting.web.tsx`のみの変更であり、Android版・iOS版には影響しない。問題があれば`Meeting.web.tsx`を元の非対応メッセージ表示に戻すだけでロールバックできる。

## 既存アーキテクチャとの整合性

[docs/frontend.md](../../../docs/frontend.md)の「アーキテクチャ」には現状、Web版のビデオ通話実装について記載がない（「通話・対話ルーム機能は`@jitsi/react-native-sdk`（Jitsi Meet）を利用する」というネイティブ版の記載のみ）。実装時に、Web版は`external_api.js`を使う旨を追記し、単一情報源の原則（[docs/prompt-guidelines.md](../../../docs/prompt-guidelines.md)）を保つ。
