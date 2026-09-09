# Expo SDK 56 / React Native 0.85 / Jitsi SDK 13.x への大規模アップグレード 要件定義書

## 背景・課題（Working Backwards）

[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)で調査した結果、Meeting画面のクラッシュ（`Element type is invalid: ...got: number`）はNew Architecture無効化では解消せず、真の原因は`@jitsi/react-native-sdk@11.6.3`が要求する`react-native ~0.77.0`と、プロジェクトの`react-native 0.81.5`（Expo SDK 54）との大きなバージョン差にあると判断した。

Web調査の結果、`@jitsi/react-native-sdk`のバージョン別react-native対応は以下の通り。

| `@jitsi/react-native-sdk` | 対応react-native | Architecture |
| --- | --- | --- |
| `11.6.3`（現行） | `~0.77.0` | Old Architecture |
| `12.0.0`〜`12.1.1` | `~0.79.7` | Old Architecture |
| `13.0.0`〜`13.1.1`（最新） | `0.85.2` | **New Architecture・Fabric・Bridgeless必須** |

また、Expo SDKとreact-nativeの対応は以下の通り（[Expo SDK 56 changelog](https://expo.dev/changelog/sdk-56)等より）。

| Expo SDK | 対応react-native |
| --- | --- |
| 54（現行） | `~0.81` |
| 55 | `~0.83` |
| **56** | **`~0.85`** |

プロジェクトの`react-native`はどのJitsi SDKバージョンの対応範囲にも合致しない「谷間」にあるため、ユーザーと協議の結果、**Jitsi SDK 13.x系・Expo SDK 56・React Native 0.85系・New Architecture有効へ、まとめてアップグレードする**方針を決定した（[.kiro/specs/fix-jitsi-meeting-crash/requirements.md](../fix-jitsi-meeting-crash/requirements.md)のオープンクエスチョン参照）。

## スコープ / Non-Goals

**スコープ:**

- `frontend`のExpo SDKを`54`→`56`（React Native `~0.81`→`~0.85`）にアップグレードする。
- `@jitsi/react-native-sdk`を`11.6.3`→`13.x`（`13.1.1`）にアップグレードする。
- `frontend/app.json`の`expo.newArchEnabled`を`true`に戻す（Jitsi SDK 13.xがNew Architecture必須のため）。
- Jitsi SDK 13.xの`peerDependencies`に合わせて、関連パッケージ（`react-native-device-info`、`react-native-get-random-values`、`react-native-performance`、`@react-native-google-signin/google-signin`、独自フォーク4パッケージ等）のバージョンを揃える。
- [.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)・[.kiro/specs/fix-jitsi-pager-view-dependency/](../fix-jitsi-pager-view-dependency/)・[.kiro/specs/fix-jitsi-config-network-error/](../fix-jitsi-config-network-error/)・[.kiro/specs/fix-worklets-core-missing-babel-plugins/](../fix-worklets-core-missing-babel-plugins/)で対応した内容のうち、New Architecture無効化を前提としていたもの（`react-native-reanimated`/`react-native-worklets`の削除、`react-native-pager-view`のバージョン固定等）を、New Architecture有効化後も問題ないか再確認・必要に応じて見直す。

**Non-Goals（今回は対応しない）:**

- Expo SDK 57以降へのさらなるアップグレード（今回はJitsi 13.xが要求する範囲＝SDK 56までとする）。
- バックエンド（`backend/`）側の変更（本アップグレードはフロントエンドのみに閉じる）。
- Jitsi以外の機能（今回のアップグレードで意図せず壊れた場合を除き、機能追加・改修は行わない）。
- 自動テストの追加（既存方針通り、[manuals/video-call-testing.md](../../../manuals/video-call-testing.md)による手動確認とする）。

## 成功指標

- `npx expo-doctor`でExpo SDK関連の警告・エラーが（許容範囲を超えて）出ないこと。
- Androidエミュレータ・実機（Xiaomi Redmi Note 9S）の両方で、Home画面の「一人で対話を開始する」からMeeting画面に遷移し、`Element type is invalid`クラッシュが発生せず、Jitsi Meetの通話UIが表示されること。
- [.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)の元々の成功指標（クラッシュなくJitsi通話UIが表示される）を満たすこと。

## ユーザーストーリー・受け入れ基準

**ユーザーストーリー**: As a ユーザー, I want Meeting画面がクラッシュせずに動作してほしい, so that ビデオ通話機能を実際に使って哲学対話ができる。

- WHEN Expo SDK 56・React Native 0.85・`@jitsi/react-native-sdk@13.x`・New Architecture有効の状態でMeeting画面を開いたとき THE SYSTEM SHALL `Element type is invalid`エラーを発生させることなく通話UIを表示する。

**ユーザーストーリー**: As a 開発者, I want アップグレードによって他の既存機能が壊れないことを確認したい, so that Jitsi以外の画面（Home、Rooms等）が問題なく動作し続ける。

- WHEN アップグレード後にHome画面・Rooms画面等の既存画面を確認したとき THE SYSTEM SHALL New Architecture有効化前と同様に動作する（レンダリングエラー・クラッシュが新たに発生しない）。

## 非機能要件

- アップグレード作業は段階的に行い、各ステップ（Expo SDKアップグレード→Jitsi SDKアップグレード→New Architecture有効化→依存パッケージ整合）ごとに動作確認できる単位に分割する（[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)で複数の問題が連鎖して発生した経験を踏まえ、一度に大量の変更を積み重ねない）。
- 依存パッケージのバージョンは、`@jitsi/react-native-sdk@13.x`が実際に宣言する`peerDependencies`を正として揃える（[.kiro/specs/fix-jitsi-pager-view-dependency/](../fix-jitsi-pager-view-dependency/)・[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)での反省を踏まえ、憶測でバージョンを選ばない）。

## オープンクエスチョン（設計・実装で確定させること）

- Expo SDK 54→56への移行に伴う破壊的変更（`npx expo install --check`・`expo-doctor`の指摘事項）の内容と対応方法。
- New Architecture有効化に伴い、[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)で削除した`react-native-reanimated`/`react-native-worklets`が本当に不要のままか（Expo SDK 56のデフォルトテンプレートが要求する可能性を再確認する）。
- `react-native-pager-view`のバージョンを、New Architecture向けに再度`8.x`系（当初削除した理由がNew Architecture専用のcodegenインターフェース不足だったため）に戻すべきか、`6.8.1`のまま（Jitsi 13.xがどのバージョンを要求するか未確認）で良いかを確認する。
- `frontend/babel.config.js`の`react-native-worklets-core/plugin`設定が、Jitsi SDK 13.x・New Architecture環境でも引き続き必要か確認する。
