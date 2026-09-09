# Jitsi Meetingビデオ通話画面のレンダリングクラッシュ修正 要件定義書

## 背景・課題（Working Backwards）

Android実機/エミュレータ上でdev clientアプリを起動し、Home画面の「一人で対話を開始する」ボタンからMeeting画面（`app/meeting.tsx`）に入ると、以下のConsole Error / Render Errorが発生し、通話画面が正しく表示されない。

```
Console Error
Error: Element type is invalid: expected a string (for built-in components) or a class/function
(for composite components) but got: number.
  at anonymous (http://192.168.1.224:8081/node_modules/expo-router/entry.bundle//&platfor...)

App: Error boundaries should implement getDerivedStateFromError().
In that method, return a state update to display an error message or fallback UI.

Render Error
Element type is invalid: expected a string (for built-in components) or a class/function
(for composite components) but got: number.
```

コールスタックには`@jitsi/react-native-sdk`内部（`.../react/features/base/app/components/BaseApp.tsx`の`componentDidCatch`）が含まれており、Jitsi SDKが提供するコンポーネントツリーの内部でクラッシュが発生している。ビデオ通話は本アプリの中核機能（[.kiro/steering/product.md](../../steering/product.md)参照）であり、この画面が使えないと哲学対話そのものができない。

## 参考情報（アップストリームの既知の問題）

このプロジェクトの`frontend/app.json`は`"newArchEnabled": true`（React NativeのNew Architecture / Fabric・TurboModulesを有効化）かつ`experiments.reactCompiler: true`の設定になっている。`@jitsi/react-native-sdk`（`package.json`で`^11.6.3`）は、New Architectureとの互換性についてアップストリームで複数の未解決課題が報告されている。

- [jitsi/jitsi-meet#17194](https://github.com/jitsi/jitsi-meet/issues/17194) — New Architecture有効時に`TurboModules are enabled, but mTurboModuleRegistry hasn't been set`でクラッシュ。`#16818`の重複としてクローズされており、明確な解決策は提示されていない。
- [jitsi/jitsi-meet#16443](https://github.com/jitsi/jitsi-meet/issues/16443) — SDK 11.5.1・React Native 0.79.5・React 19.0.0・New Architecture有効の環境で`JitsiMeeting`のエクスポート関連の問題が報告されている。
- [jitsi/jitsi-meet#16849](https://github.com/jitsi/jitsi-meet/issues/16849)、[#14912](https://github.com/jitsi/jitsi-meet/issues/14912) — より新しいReact Nativeバージョンでの非互換が継続的に報告されている。

このプロジェクトの環境（React Native `0.81.5`、React `19.1.0`、New Architecture有効）は上記の問題が報告されている環境と近く、今回のクラッシュも同種の非互換が原因である可能性が高い。ただし「Element type is invalid: ...got: number」という具体的なエラーメッセージ・完全なコンポーネントスタック（画面上で省略されている13フレーム）は未確認であり、断定はできていない。

## スコープ / Non-Goals

**スコープ:**

- `app/meeting.tsx`（Home画面の「一人で対話を開始する」ボタンから遷移する画面）を開いた際に発生する、今回報告されたクラッシュの解消。
- 原因がNew Architecture関連である場合の対応方針の決定（設計フェーズで、後述の候補から選定する）。

**Non-Goals（今回は対応しない）:**

- `@jitsi/react-native-sdk`自体のバグ修正・fork・パッチ適用（アップストリームの問題であり、このリポジトリ側での修正対象ではない）。
- New Architecture非対応が判明した場合の、Jitsi以外のライブラリ（`react-native-reanimated`, `react-native-worklets`等）のNew Architecture対応状況の網羅的な調査（今回のクラッシュに関係する範囲のみ扱う）。
- iOS/Web版での動作確認（今回はAndroidでの発生のみ確認済み。iOSで別途発生するかは未確認・スコープ外）。
- マッチング機能とビデオ通話画面の統合（[.kiro/specs/philosophy-dialog-app/requirements.md](../philosophy-dialog-app/requirements.md)の既知の課題であり、別タスク）。

## 成功指標

新機能ではなくバグ修正のため、以下を満たすことをもって成功とする（定量指標ではなく、動作確認可能な受け入れ基準で判定する）。

- [manuals/video-call-testing.md](../../../manuals/video-call-testing.md)の手順に従い、Home画面の「一人で対話を開始する」ボタンからMeeting画面に入った際、Console Error/Render Error（`Element type is invalid`）が発生しないこと。
- Jitsi Meetの通話UI（カメラ映像・マイク入力・ツールバー）が表示されること。

## ユーザーストーリー・受け入れ基準

**ユーザーストーリー**: As a ユーザー, I want Meeting画面を開いてもアプリがクラッシュしないでほしい, so that ビデオ通話機能を実際に使って哲学対話ができる。

- WHEN ユーザーがHome画面の「一人で対話を開始する」ボタンをタップし、Meeting画面（`app/meeting.tsx`）が遷移・マウントされたとき THE SYSTEM SHALL LogBoxに`Element type is invalid`のConsole Error/Render Errorを発生させることなく、Jitsi Meetの通話UIを表示する。
- IF 原因がReact NativeのNew Architecture（Fabric/TurboModules）と`@jitsi/react-native-sdk`の非互換であることが設計フェーズで確認された場合 THEN 対応方針（例: New Architectureの無効化、SDKバージョンの見直し等）を設計ドキュメント（design.md）に明記し、他の既存機能（expo-router, react-native-reanimated等、New Architecture前提で動作している可能性のある機能）の動作に回帰がないことを確認する。

**ユーザーストーリー**: As a 開発者, I want このクラッシュの根本原因を特定したい, so that その場しのぎの対処ではなく正しい修正を選べる。

- WHEN 本修正に着手するとき THE SYSTEM SHALL LogBoxの「Collapse all 13 frames」を展開する等して、クラッシュを起こしている具体的なコンポーネント（`@jitsi/react-native-sdk`内のどのコンポーネント/どのnative view管理か）を特定した上で設計を行う。

## 非機能要件

- 今回の修正が、New Architecture前提で動作している他の依存ライブラリ（`react-native-reanimated` ~4.1.1、`react-native-worklets` 0.5.1・`-core`、`react-native-screens`等）の動作を壊さないこと。
- 修正内容は[manuals/video-call-testing.md](../../../manuals/video-call-testing.md)に沿って手動で動作確認できること（自動テストの追加は今回のNon-Goalsに含む）。

## オープンクエスチョン（設計フェーズで確定させること）→ 大幅更新

- ~~LogBoxの省略されたコールスタックを展開し、クラッシュの直接の原因コンポーネントを特定する~~ → **一部確認**。`componentDidCatch`は`@jitsi/react-native-sdk`自身の`react/features/base/app/components/BaseApp.tsx`（`logger.error(error, info)`）であることを確認したが、`info.componentStack`（どのコンポーネントが原因か）はLogBox上で`(truncated)`となり内容を確認できていない。
- ~~`newArchEnabled: false`にした場合にクラッシュが再現しなくなるか~~ → **検証した。再現する。** New Architectureを無効化し（[.kiro/specs/fix-jitsi-config-network-error/](../fix-jitsi-config-network-error/)まで含む一連の対応を経て）実際に会議への接続・マイク/カメラ権限ダイアログまで到達できる状態にした上でも、同一の`Element type is invalid: ...got: number`クラッシュが発生した。**つまり本specの設計（[design.md](design.md)）が前提としていた「New Architecture非互換が原因」という仮説は誤りだったと判断せざるを得ない。**

### 新たに判明した、より有力な原因候補（依存パッケージのバージョン不整合）

`@jitsi/react-native-sdk`（`node_modules/@jitsi/react-native-sdk/package.json`）が宣言する`peerDependencies`と、`frontend/package.json`の実際のインストール内容を全て照合したところ、広範なバージョン不整合が判明した。

| パッケージ | Jitsi SDKが期待 | 実際のインストール | 差分 |
| --- | --- | --- | --- |
| `react-native` | `~0.77.0` | `0.81.5` | **4マイナーバージョン差**（最重要） |
| `react-native-device-info` | `12.1.0` | `^15.0.1` | 3メジャーバージョン差 |
| `react-native-get-random-values` | `1.11.0` | `^2.0.0` | 1メジャーバージョン差 |
| `react-native-performance` | `5.1.2` | `^6.0.0` | 1メジャーバージョン差 |
| `@react-native-google-signin/google-signin` | `10.1.0` | `^16.1.1` | 6メジャーバージョン差 |
| `@react-native-community/slider` | `4.5.6` | `^5.1.2` | 1メジャーバージョン差 |
| `@giphy/react-native-sdk` | `4.1.0` | `^5.0.1` | 1メジャーバージョン差 |
| `react-native-gesture-handler`/`safe-area-context`/`screens`/`svg`/`webview`/`video`等 | 個別バージョン指定 | いずれも数マイナーバージョン新しい | 軽微 |

加えて、Jitsi SDKが**独自にパッチしたGitHubフォーク**を要求している以下4パッケージが、フォークではなく**通常のnpmレジストリ版**でインストールされている。

| パッケージ | Jitsi SDKが期待 | 実際のインストール |
| --- | --- | --- |
| `react-native-background-timer` | `github:jitsi/react-native-background-timer#d180dfa...` | `^2.4.1`（npm版） |
| `react-native-calendar-events` | `github:jitsi/react-native-calendar-events#47f068d...` | `^2.2.0`（npm版） |
| `react-native-default-preference` | `github:jitsi/react-native-default-preference#c9bf63b...` | `^1.4.4`（npm版） |
| `react-native-sound` | `github:jitsi/react-native-sound#ea13c97...` | `^0.13.0`（npm版） |
| `react-native-orientation-locker` | `github:jitsi/react-native-orientation-locker#fe09565...` | `^1.7.0`（npm版） |

**この状態は、プロジェクトの初期セットアップ時にJitsi SDKのpeerDependenciesを「最新のnpmバージョン」でインストールしてしまい、Jitsi側が実際に動作検証しているバージョン（一部は独自フォック）と揃えていなかったことを示している。** `react-native`本体が4マイナーバージョンも離れていることは、React Native内部のレンダラー・コンポーネント登録機構の変更を考えると、"Element type is invalid...got: number"のような描画系エラーの原因として非常に有力である。

この新事実により、design.md（New Architecture無効化で解決するという設計）は前提が崩れており、design.mdの見直しが必要。

### `@jitsi/react-native-sdk`のバージョン別react-native対応状況（Web調査）

npmレジストリ・[jitsi-meet-release-notesのCHANGELOG-MOBILE-SDKS.md](https://github.com/jitsi/jitsi-meet-release-notes/blob/master/CHANGELOG-MOBILE-SDKS.md)を調査した結果、以下が判明した。

| `@jitsi/react-native-sdk`バージョン | 対応react-native | Architecture |
| --- | --- | --- |
| `11.6.3`（現在インストール中） | `~0.77.0` | Old Architecture（New Architectureは非互換、[.kiro/specs/fix-jitsi-meeting-crash/design.md](design.md)参照） |
| `12.0.0`〜`12.1.1` | `~0.79.7`（React 19.0.0） | Old Architecture |
| `13.0.0`（最新は`13.1.1`、`~0.85.0`要求） | `0.85.2` | **New Architecture・Fabric・Bridgeless Modeが必須**（変更履歴に明記） |

プロジェクトの`react-native`は`0.81.5`（Expo SDK 54が要求するバージョン）であり、**Jitsi SDKのどのバージョンの対応範囲にもちょうど一致しない**（11.x/12.xは0.81より古いバージョンまでしか対応せず、13.xは0.81より新しい0.85.2かつNew Architecture必須）。

**つまり、今回の一連の問題を本質的に解決するには、以下のいずれかの大きな方向性の決定が必要になる。**

1. **現状維持派**: `react-native`/Expo SDKのバージョンは変えず、`@jitsi/react-native-sdk@11.6.3`のpeerDependenciesが要求する個別パッケージ（`react-native-device-info`, `react-native-get-random-values`, `react-native-performance`, `@react-native-google-signin/google-signin`等、および独自フォークの4パッケージ）を、Jitsi指定の正確なバージョン・フォークにダウングレード/差し替える。`react-native`本体自体のバージョン差（0.77→0.81）は是正できないため、対応してもなお同種の描画エラーが残るリスクがある。
2. **アップグレード派**: `@jitsi/react-native-sdk`を`13.x`系にアップグレードし、`react-native`/Expo SDKを`0.85.2`系に、`newArchEnabled`を`true`に戻す。Jitsi側がNew Architectureに正式対応した最初のメジャーバージョンであるため、[.kiro/specs/fix-jitsi-meeting-crash/](fix-jitsi-meeting-crash/)でNew Architectureを無効化した本来の理由（当時のSDKバージョンがNew Architecture非対応だった）が解消される可能性がある。ただしExpo SDK・React Native・関連ライブラリ全体の大規模アップグレードとなり、影響範囲・作業量は大きい。
