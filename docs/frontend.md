# フロントエンド (`frontend/`)

Expo（React Native, TypeScript, [expo-router](https://docs.expo.dev/router/introduction/) によるファイルベースルーティング）によるモバイル/Webフロントエンド。

## セットアップ

```bash
cd frontend
npm install
```

Android実機/エミュレータ向けのネイティブビルド（`npm run android` / Windowsでは`npm run android:win`）を行う場合は、事前に`ANDROID_HOME`環境変数がAndroid SDKのインストール先（例: Windowsのデフォルトでは`%LOCALAPPDATA%\Android\Sdk`）を指すように設定しておくこと。未設定の場合、Gradleビルドが`SDK location not found`エラーで失敗する（[.kiro/specs/fix-android-sdk-location-error/](../.kiro/specs/fix-android-sdk-location-error/)参照）。`frontend/android/local.properties`は`expo prebuild`のたびに再生成される生成物（`.gitignore`対象）のため、`ANDROID_HOME`側を恒久的に設定しておく方針とする。

## よく使うコマンド

```bash
npm run start    # Expo開発サーバー起動（QRコードからExpo Go/実機で確認）
npm run android  # Androidエミュレータ/実機で起動
npm run ios      # iOSシミュレータ/実機で起動
npm run web      # Webブラウザで起動
npm run lint     # ESLint実行（eslint-config-expo）
```

テストランナーは未設定。

## 設定

APIベースURLなど環境依存の値を扱う仕組みは現時点で未導入。追加する場合はExpoの規約に従い、クライアントに公開してよい値のみ `EXPO_PUBLIC_` プレフィックスの環境変数として扱うこと（非公開のシークレットを `EXPO_PUBLIC_*` に入れない）。アプリ自体の設定（名前・スキーム・バンドルID等）は `app.json` で管理する。

## アーキテクチャ

- ルーティングは `app/` 配下のファイルベースルーティング（expo-router）。`app/_layout.tsx` がルートレイアウト、`app/(tabs)/` がタブグループ（`index.tsx`=Home、`rooms.tsx`=Rooms、`_layout.tsx`でタブ構成を定義）、`app/modal.tsx` がモーダル画面。
- TypeScriptを使用し、パスエイリアス `@/*` は `frontend/` 直下を指す（`tsconfig.json` 参照）。
- 再利用可能なUIコンポーネントは `components/`（プラットフォーム分岐が必要なものは `Meeting.tsx` / `Meeting.web.tsx` のように `.web.tsx` サフィックスで出し分ける）、共通ロジックは `hooks/`、テーマ・定数は `constants/` に置く。
- スタイリングはCSSではなく React Native の `StyleSheet`/インラインスタイルを使用する。
- 通話・対話ルーム機能は `@jitsi/react-native-sdk`（Jitsi Meet）を利用する。Web版（`components/Meeting.web.tsx`）はネイティブモジュールが使えないため、Jitsiが提供する`https://meet.jit.si/external_api.js`（Jitsi Meet API）を動的に読み込み、`View`の実DOMノードに埋め込む方式を使う（[.kiro/specs/web-video-call-support/](../.kiro/specs/web-video-call-support/)参照）。
- Expo SDK 56（React Native 0.85系）を使用。SDK56では`app.json`に`expo.newArchEnabled`プロパティ自体が存在せず、New Architectureが常時有効固定になっている。当初`@jitsi/react-native-sdk@11.6.3`はNew Architecture非互換のため無効化していたが（[.kiro/specs/fix-jitsi-meeting-crash/](../.kiro/specs/fix-jitsi-meeting-crash/)）、`@jitsi/react-native-sdk@13.x`はNew Architecture・Fabric・Bridgeless Modeに正式対応したため、Expo SDK 56・Jitsi SDK 13.xへまとめてアップグレードした（[.kiro/specs/upgrade-expo-sdk56-jitsi13/](../.kiro/specs/upgrade-expo-sdk56-jitsi13/)参照）。
- `react-native-reanimated`/`react-native-worklets`は引き続き未使用（実際に使っていたのは`app/`から参照されないテンプレート由来の未使用コンポーネントのみ）のため未インストールのまま。アニメーションが必要になった場合は導入を検討すること。
- `@jitsi/react-native-sdk`が要求する周辺パッケージ（`react-native-svg`、`react-native-video`、`react-native-webrtc`、`react-native-device-info`、`@react-native-google-signin/google-signin`等、および`react-native-background-timer`/`calendar-events`/`default-preference`/`orientation-locker`/`sound`の独自GitHubフォーク）は、Jitsi SDKの`peerDependencies`が宣言する正確なバージョンに固定している。`npx expo install --check`が指摘するExpoの推奨バージョンとは意図的に異なる（Jitsi SDKとの互換性を優先しているため）。バージョンを変更する際は、まず`node_modules/@jitsi/react-native-sdk/package.json`の`peerDependencies`を確認すること（[.kiro/specs/fix-jitsi-pager-view-dependency/](../.kiro/specs/fix-jitsi-pager-view-dependency/)で憶測により`react-native-pager-view`を誤って削除した反省を踏まえる）。
- `frontend/babel.config.js`で`react-native-worklets-core/plugin`をBabelプラグインとして明示的に設定している。`babel-preset-expo`はこのプラグインを自動検出しないため必須（未設定だと、Jitsi SDK内部でworkletの実行時に`callInContext ... not a valid worklet`エラーが発生し、会議接続が失敗する。[.kiro/specs/fix-jitsi-config-network-error/](../.kiro/specs/fix-jitsi-config-network-error/)参照）。このプラグインは内部で`@babel/plugin-transform-shorthand-properties`・`@babel/plugin-transform-arrow-functions`・`@babel/plugin-proposal-optional-chaining`・`@babel/plugin-proposal-nullish-coalescing-operator`・`@babel/plugin-transform-template-literals`の5つをハードコードで要求するため、`frontend/package.json`の直接の依存関係として明示的に追加している（`babel-preset-expo`経由の暗黙のホイスティングに任せると、Expoのバージョンアップのたびに解決できなくなり`Cannot find module`エラーが再発するため。[.kiro/specs/fix-worklets-core-missing-babel-plugins/](../.kiro/specs/fix-worklets-core-missing-babel-plugins/)参照）。
- SDK56以降、expo-routerは`@react-navigation/*`パッケージとの併用不可（`expo-router/react-navigation`・`expo-router/js-tabs`が代替のエントリポイント）。`@jitsi/react-native-sdk`が内部で使う`@react-navigation/*`（Jitsi自身のnode_modules配下にネストされる）とは独立しており、アプリ側のコードから`@react-navigation/*`を直接importしないこと。
- `@jitsi/react-native-sdk`は内部でReact Navigation **v6**（`@react-navigation/native@6.x`・`core@6.x`、Jitsi SDK自身の依存としてhoistされる）の`NavigationContainer`を4つ（Root/Conference/Lobby/Settings）使い、いずれも v6 の`independent={true}`プロップで独立ツリーとして扱っている。一方expo-router（SDK56以降）は内製のReact Navigation **v7**コア（`node_modules/expo-router/build/react-navigation/`）で動く。両者は本来まったく別のモジュールインスタンスで、`<JitsiMeeting>`側にラッパー（`NavigationIndependentTree`等）は**不要**（`components/Meeting.tsx`参照）。
  - **必須設定**: `frontend/.env`の`EXPO_ROUTER_DISABLE_RN_NAVIGATION_CHECK=1`。このフラグが無いと、Expo CLIのMetroリゾルバ（`@expo/cli/build/src/start/server/metro/withMetroMultiPlatform.js`）が**node_modules内からのものを含む全ての`@react-navigation/core`インポートを`expo-router/react-navigation`（内製v7コア）にリダイレクト**する。するとJitsiの各コンテナがv7コアで動き、v6の`independent={true}`が無視されて`Looks like you have nested a 'NavigationContainer' inside another`エラーになり、会議画面・ロビーに入れない（[.kiro/specs/fix-meeting-join-crash/](../.kiro/specs/fix-meeting-join-crash/)参照）。同フラグは「アプリ側コードでの`@react-navigation/*`直接import禁止」チェックも無効化するが、アプリ側コードでは引き続き`@react-navigation/*`を直接importしないこと（画面遷移はexpo-routerに統一する）。
  - v6コアには`NavigationIndependentTree`（v7 API）が存在しないため、`@react-navigation/native`からimportすると`undefined`になり`Element type is invalid ... got: undefined`になる。使わないこと。
- `frontend/metro.config.js`で`react-native-svg-transformer`（`@jitsi/react-native-sdk`自身の依存として既にインストール済み）をBabelトランスフォーマーとして設定している。Jitsi SDKのアイコンは`.svg`ファイルを直接importする実装（例: `import IconMic from './mic.svg'`）になっており、このトランスフォーマーが無いと`.svg`が通常のアセット扱いとなり生の数値（アセットID）に解決されてしまう。その数値がそのままアイコンコンポーネントとして扱われ、`Element type is invalid: ...got: number`というクラッシュを引き起こす（[.kiro/specs/fix-jitsimeeting-element-invalid/](../.kiro/specs/fix-jitsimeeting-element-invalid/)参照）。
- `@jitsi/react-native-sdk`のAndroidビルドには、標準のExpoテンプレートにはない手動設定（`rootProject.ext.gradlePluginVersion`、`minSdkVersion`、通話に必要なパーミッション）が必要。これは`plugins/withJitsiAndroidGradle.js`（ローカルconfig plugin）と`expo-build-properties`（`app.json`）で`expo prebuild`のたびに自動適用されるようにしている。
