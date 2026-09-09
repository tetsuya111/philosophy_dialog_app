# JitsiMeeting要素がElement type is invalidになる問題 要件定義書

## 背景・課題（Working Backwards）

[.kiro/specs/fix-jitsi-nested-navigation-container/](../fix-jitsi-nested-navigation-container/)でNavigationContainerの二重ネストを解消した後、Meeting画面表示時に以下のエラーが発生する。これは[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)で最初に報告されたクラッシュと同一の症状（`Element type is invalid: ...got: number`）だが、今回はスタックトレースが大幅に改善され、原因箇所をより正確に特定できた。

```
ERROR  2026-09-06T11:01:20.800Z [ERROR] [app:base-app]
[Error: Element type is invalid: expected a string (for built-in components) or a class/function (for composite components) but got: number.]

Code: components/Meeting.tsx
  33 |       <NavigationIndependentTree>
  34 |         {/* @ts-ignore */}
> 35 |         <JitsiMeeting
     |         ^
Call Stack
  Meeting (components\Meeting.tsx:35:9)
  MeetingScreen (app\meeting.tsx:8:10)
  RootLayout (app\_layout.tsx:15:7)
```

## 判明している事実

- スタックトレースは`components/Meeting.tsx:35`の`<JitsiMeeting`タグそのものを指しており、`@jitsi/react-native-sdk`内部の深い階層（[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)で最初に確認した`BaseApp.tsx`の`componentDidCatch`）ではなく、**`JitsiMeeting`という値自体がReactの`createElement`/Fiber生成の時点で「数値」になっている**ことを示している。
- `node_modules/@jitsi/react-native-sdk/index.tsx`のソースを確認したところ、`JitsiMeeting`は`export const JitsiMeeting = forwardRef<JitsiRefProps, IAppProps>((props, ref) => {...});`として正しくエクスポートされている（ソースコード上は正常なコンポーネント）。
- `@jitsi/react-native-sdk`の`package.json`の`"main"`は`"index.tsx"`（プリコンパイル済みではなく、Metroが直接Babel変換するソースファイル）。
- 「got: number」はMetroのモジュールID（内部的な依存関係マップの整数インデックス）が、本来解決されるべきモジュール本体の代わりに漏れ出た場合の典型的な症状であり、Babel変換の異常（`require()`呼び出しの変換ミス等）を示唆する。
- [.kiro/specs/fix-worklets-core-missing-babel-plugins/](../fix-worklets-core-missing-babel-plugins/)で`react-native-worklets-core/plugin`を有効化して以降、このプラグインは対象ファイル内の`'worklet'`ディレクティブを持つ関数を個別に隔離Babelコンパイルする処理（`makeWorklet`/`processWorkletFunction`）を行う。`index.tsx`自体には`'worklet'`ディレクティブは見当たらないが、`index.tsx`が読み込む`./react/bootstrap.native`・`./react/features/app/components/App.native`等の依存先のいずれかでworklet処理が行われ、その際の変換が`index.tsx`モジュール全体（の依存解決）に悪影響を与えている可能性がある（未確認・仮説）。

## スコープ / Non-Goals

**スコープ:**

- `<JitsiMeeting>`が`Element type is invalid: ...got: number`にならず、正しくコンポーネントとしてレンダリングされる状態にすること。

**Non-Goals（今回は対応しない）:**

- `@jitsi/react-native-sdk`自体のコード修正・fork。
- [.kiro/specs/fix-jitsi-nested-navigation-container/](../fix-jitsi-nested-navigation-container/)・[.kiro/specs/fix-worklets-core-missing-babel-plugins/](../fix-worklets-core-missing-babel-plugins/)で対応済みの内容の再調査（ただし、それらの対応が今回の問題の原因になっていないかの検証は含む）。

## 成功指標

- Home画面の「一人で対話を開始する」ボタンからMeeting画面を開いた際、`Element type is invalid`エラーが発生せず、Jitsi Meetの通話UIが表示されること。

## ユーザーストーリー・受け入れ基準

**ユーザーストーリー**: As a ユーザー, I want Meeting画面を開いた際に`JitsiMeeting`コンポーネントが正しく描画されてほしい, so that ビデオ通話機能を実際に使って哲学対話ができる。

- WHEN Meeting画面で`<JitsiMeeting>`がレンダリングされたとき THE SYSTEM SHALL `Element type is invalid`エラーを発生させない。

## 非機能要件

- 原因調査は、実際のスタックトレース・ソースコードの確認に基づいて行い、憶測で設定変更をしない（[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)・[.kiro/specs/fix-jitsi-pager-view-dependency/](../fix-jitsi-pager-view-dependency/)での反省を踏まえる）。

## オープンクエスチョン（設計フェーズ・追加調査で確定させること）

- ~~`react-native-worklets-core/plugin`が原因か~~ → **否定された**。`babel.config.js`から一時的にコメントアウトして再現確認したところ、`loadConfig`の`callInContext ... not a valid worklet`エラー（無効化したことによる別の想定内のエラー）は出たが、**`Element type is invalid ...got: number`は全く同じ箇所（`components/Meeting.tsx:35`の`<JitsiMeeting`）で引き続き発生した**。worklets-coreのBabel変換が原因ではないと確定した。
- **経緯の整理**: 本クラッシュは、New Architecture無効・Jitsi SDK 11.6.3の状態でも、New Architecture有効・Jitsi SDK 13.1.1の状態でも、いずれも発生している。ただし発生箇所は変化している。当初（[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)時点）はエラーが`@jitsi/react-native-sdk`内部の`BaseApp.tsx`の`componentDidCatch`で捕捉されており、`<JitsiMeeting>`自体は正常にレンダリングされ、その内部の深い階層の何かが原因だったと考えられる。しかし今回は`<JitsiMeeting`タグ自体（このリポジトリの`components/Meeting.tsx:35`）が直接の原因箇所としてスタックトレースに現れており、`JitsiMeeting`という値自体が生成された時点で不正になっていることを示す、**より根の浅い（かつ以前とは異なる）問題**である可能性が高い。
- ~~`JitsiMeeting`のインポート結果に問題がないか~~ → **問題なしと確認**。診断ログの結果、`typeof JitsiMeeting: object value: {"$$typeof": Symbol(react.forward_ref), "render": [Function anonymous]}`。正常な`forwardRef`コンポーネントであり、インポート自体は完全に正しい。

### 診断結果を踏まえた結論の更新

`JitsiMeeting`自体が正常であることが確定したため、LogBoxが表示する「`<JitsiMeeting`（`components/Meeting.tsx:38`）が原因」という表示は、**実際の原因箇所ではなく、新しいLogBoxの表示仕様（node_modules内の深いフレームを畳み、アプリコード側の最も近い呼び出し元を代表して表示する）による見かけ上の位置**だと判断する。ログのタイミング（`onUserMediaSuccess`が2回成功した直後にクラッシュが発生）から、実際の原因は[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)で最初に確認したのと同様、`@jitsi/react-native-sdk`内部の会議画面レンダリング処理の奥深くにあると考えられる。

**新たな有力候補**: [.kiro/specs/upgrade-expo-sdk56-jitsi13/tasks.md](../upgrade-expo-sdk56-jitsi13/tasks.md)で`npx expo-doctor`が指摘していた「`react-native-screens`の重複インストール（自分たちが指定した`4.17.1`と、`expo-router`が内包する`4.27.0`が共存）」が未解消のまま残っている。Fabric（New Architecture）ではネイティブView Managerの参照が内部的に数値コマンドマップを介するため、2つの異なるバージョンの`react-native-screens`が混在すると、Jitsi内部のnative-stackナビゲーション（Chat & Polls等）で不正な参照（数値）が発生する可能性がある。次の切り分け対象とする。

## 結果（対応済み）

- `yarn why react-native-screens`で確認したところ、`expo-router`自身が`react-native-screens@^4.26.0`を要求しており、Jitsi指定の`4.17.1`とは別に`node_modules/expo-router/node_modules/react-native-screens@4.27.0`という重複インストールが発生していた。expo-router自体の動作（アプリの基本ナビゲーション）を壊さないことを優先し、`react-native-screens`を`4.27.0`（同一メジャーバージョン内）に統一した。
- 同様に`@react-native-async-storage/async-storage`も、`@amplitude/analytics-react-native`が内部で`1.24.0`を要求しており重複していたため、`1.24.0`に統一した。
- `npx expo-doctor`で再確認したところ、重複依存の指摘は解消（22項目中19項目パス、残り3項目は既知・許容済みのリスクのみ）。

## オープンクエスチョン（追加）→ 根本原因を特定・解決

- ~~react-native-screens・async-storageの重複解消によりエラーが解消するか~~ → **解消せず**。同一のエラー・同一のタイミング（ビデオ用の`Got media constraints`の直後、`onUserMediaSuccess`の直前）で再発した。
- `node_modules/@jitsi/react-native-sdk/react/features/base/app/components/BaseApp.tsx`の`componentDidCatch`に`info.componentStack`を出力する一時的な診断ログを追加し、初めて`componentStack`の全文を取得できた（[.kiro/specs/fix-jitsi-meeting-crash/requirements.md](../fix-jitsi-meeting-crash/requirements.md)に残っていたオープンクエスチョンに対応）。

### 根本原因（確定）

`componentStack`の最も内側（原因に近い側）は以下だった。

```
at anonymous (...:416407:43)   ← IconComponent（実体はJitsiのアイコン。壊れている）
at RCTView / View
at Container (...)              ← Icon.tsxがレンダーするContainer
at Icon (...)                   ← @jitsi/react-native-sdk/.../icons/components/Icon.tsx
at RCTView / View
at TouchableHighlight
at ToolboxItem (...)
at AbstractAudioMuteButton (...)
...
at Prejoin (...)
```

`Icon.tsx`（`node_modules/@jitsi/react-native-sdk/react/features/base/icons/components/Icon.tsx`）は`<IconComponent { ...iconProps } .../>`（201行目、`IconComponent = props.src`）という形でアイコンをレンダーしている。`ToolboxItem.native.tsx`は`<Icon src={this.props.icon} .../>`としてこれを呼び出し、`AbstractAudioMuteButton`は`BaseAudioMuteButton.ts`経由で`icon = IconMic`（`../../icons/svg`からimport）を設定している。

`icons/svg/constants.ts`を確認したところ、`import { default as IconAI } from './AI.svg';`のように**`.svg`ファイルを直接JSモジュールとしてimportしている**ことが判明した。これは`react-native-svg-transformer`（Metroのカスタムbabelトランスフォーマー、`.svg`ファイルをSVG Reactコンポーネントに変換する）がMetro設定に組み込まれていることを前提にしたコードである。

`@jitsi/react-native-sdk`自身の`package.json`は`"react-native-svg-transformer": "1.2.0"`を依存として宣言しており、`frontend/node_modules`にも実際にインストールされている。しかし**`frontend/metro.config.js`にはこのトランスフォーマーが一切設定されていなかった**（`getDefaultConfig(__dirname)`をそのままexportするのみ）。

Metroにこの設定がないと、`.svg`ファイルはデフォルトのアセット扱いとなり、`import IconAI from './AI.svg'`は生のアセットID（**数値**）に解決される。この数値がそのままアイコンコンポーネント（`IconMic`等）として扱われ、`<IconComponent .../>`でReactの要素生成時に「Element type is invalid: ...got: number」が発生していた。

### 対応（実施済み）

`frontend/metro.config.js`に、`.svg`を`react-native-svg-transformer`で変換するよう設定した（`babelTransformerPath`の指定、`assetExts`から`svg`を除外し`sourceExts`に追加）。追加のパッケージインストールは不要（Jitsi SDK自身の依存として既にインストール済み）。

診断用に追加していた`components/Meeting.tsx`・`node_modules/@jitsi/react-native-sdk/.../BaseApp.tsx`の`console.log`は削除した。

### 追加の不足パッケージ（発覚・対応済み）

- `metro.config.js`設定後、`react-native-svg-transformer@1.2.0`（Jitsi SDKが依存として持ち込む古いバージョン）自身が内部で`@react-native/metro-babel-transformer`（react-native >= 0.73で使われる新パッケージ名）または`metro-react-native-babel-transformer`（旧パッケージ名）のいずれかを要求するが、Expoのプロジェクトはどちらもデフォルトではインストールしないため`Cannot find module 'metro-react-native-babel-transformer'`エラーが発生した。`@react-native/metro-babel-transformer@0.85.3`を追加してこのエラー自体は解消したが、続けて`Cannot find module 'babel.config.js'`という別のエラーが発生した。原因は`@react-native/metro-babel-transformer`が`@expo/metro-config`の独自モジュール解決（`moduleMapper.js`）と完全には互換性がなく、`babel.config.js`を`extends`する処理が正しく解決できないためと判明した。
- **最終対応**: `react-native-svg-transformer`自体を`1.5.3`（最新版）にアップグレードした。この版は`getExpoTransformer()`という関数で`@expo/metro-config/babel-transformer`を優先的に使う実装になっており（Expo公式ブログ曰く「Expo v50.0.0以降、`@expo/metro-config/babel-transformer`をupstreamトランスフォーマーとして使うようになったため、利用可能な場合はそちらを優先すべき」とコメントされている）、`@react-native/metro-babel-transformer`のような互換性のない代替パッケージを経由せず、Expo自身のtransformerを直接使うため、上記の問題が根本的に解消される。`yarn why`で確認したところ`1.5.3`が正しくトップレベルに解決され、Jitsi SDK自身が使う`1.2.0`（隔離された`node_modules`内）とは独立して共存している。

## 副次的に確認した事項（対応不要・記録のみ）

- ログに`The following feature flags are not supported: audioMute.enabled, fullscreen.enabled, audioOnly.enabled, pip-while-screen-sharing.enabled`という警告が出ている。`components/Meeting.tsx`の`flags`プロップで指定しているこれら4つのフラグ名は、Jitsi SDK 13.1.1では認識されなくなっている（クラッシュには関係しないが、将来的に`Meeting.tsx`のflags指定を最新のJitsi SDKドキュメントに合わせて見直す余地がある）。
