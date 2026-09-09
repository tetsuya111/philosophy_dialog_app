# 作業ログ: Expo SDK 56 / React Native 0.85 / Jitsi SDK 13.xへの大規模アップグレード

## 何を行ったか

- `.kiro/specs/upgrade-expo-sdk56-jitsi13/`にrequirements.md・tasks.mdを新規作成した。
- `frontend`のExpo SDKを`54`→`56`（React Native `0.81.5`→`0.85.3`、React`19.1.0`→`19.2.3`）にアップグレードした。
- `app.json`のスキーマエラーを修正（`newArchEnabled`・`android.edgeToEdgeEnabled`がSDK56では無効なプロパティと判明し削除。**SDK56ではNew Architectureが常時有効固定**）。
- SDK56で「expo-routerとreact-navigationの併用不可」になったため、`app/_layout.tsx`・`components/haptic-tab.tsx`のimportを`expo-router`/`expo-router/react-navigation`経由に移行し、未使用になった`@react-navigation/bottom-tabs`・`elements`・`native`・`stack`を削除した。
- 不足していたpeer dependency（`@react-native-async-storage/async-storage`、`@expo/metro-runtime`、`@expo/log-box`）を追加した。
- `@jitsi/react-native-sdk`を`11.6.3`→`13.1.1`にアップグレードした（New Architecture・Fabric・Bridgeless Mode対応の最初のメジャーバージョン）。
- Jitsi 13.1.1の`peerDependencies`に基づき、`react-native-svg`・`react-native-video`・`react-native-webrtc`・`react-native-webview`・`react-native-worklets-core`（コミット更新）・`react-native-device-info`・`@react-native-google-signin/google-signin`・`@react-native-community/netinfo`・`@amplitude/analytics-react-native`・`@react-native-async-storage/async-storage`・`react-native-gesture-handler`・`react-native-safe-area-context`・`react-native-screens`・`react-native-splash-view`、および独自GitHubフォーク5パッケージ（`background-timer`/`calendar-events`/`default-preference`/`orientation-locker`/`sound`）を、Jitsi指定の正確なバージョン・フォークに揃えた。
- `docs/frontend.md`を今回のアップグレード内容に合わせて更新した。
- `npx expo prebuild --clean`でネイティブプロジェクトを再生成し、`android/gradle.properties`で`newArchEnabled=true`を確認した。`local.properties`は今回も自動生成されなかったため`sdk.dir`を手動で再作成した。

## なぜ行ったか

[.kiro/specs/fix-jitsi-meeting-crash/](../.kiro/specs/fix-jitsi-meeting-crash/)の調査で、Meeting画面のクラッシュ（`Element type is invalid: ...got: number`）がNew Architecture無効化では解消せず、真の原因が`@jitsi/react-native-sdk@11.6.3`の要求する`react-native ~0.77.0`とプロジェクトの`react-native 0.81.5`の大きなバージョン差にあると判明した。Web調査の結果、Jitsi SDK 13.x系がNew Architecture・RN 0.85.2に正式対応した最初のメジャーバージョンと分かったため、ユーザーと協議の上、Expo SDK 56・Jitsi SDK 13.x・New Architecture有効へまとめてアップグレードする方針を決定した。

## 副次的に対応した問題

- `yarn add`でJitsiの独自GitHubフォークパッケージを取得する際、gitのSSL証明書検証エラー（`unable to get local issuer certificate`、企業プロキシ等の影響とみられる）が発生。`git config --global http.sslbackend schannel`（Windows証明書ストアを使う設定）で解決した。

## 残っているリスク（`npx expo-doctor`で確認済み、対応保留）

- 重複ネイティブモジュール: `@react-native-async-storage/async-storage`（1.23.1 vs `@amplitude/analytics-react-native`内包の1.24.0）、`react-native-screens`（4.17.1 vs `expo-router`内包の4.27.0）。実機ビルド時にネイティブビルドエラーとして顕在化する可能性がある。
- Hermes V1の既知のメモリリーク回帰（Expo SDK56/RN0.85系）。SDK57（RN0.86.2+）で修正されているが、Jitsi 13.1.1が`react-native: ~0.85.0`のみを対象としているため今回はSDK56のまま進めた。

## 残作業

[CLAUDE.md](../CLAUDE.md)の方針により、Androidエミュレータ・実機でのビルド・動作確認はユーザーに依頼する（`.kiro/specs/upgrade-expo-sdk56-jitsi13/tasks.md`タスク12）。`Element type is invalid`クラッシュが解消したか、Home/Rooms等の既存画面に回帰がないかを確認する必要がある。
