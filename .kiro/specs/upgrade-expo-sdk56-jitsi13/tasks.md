# タスクリスト

[requirements.md](requirements.md)を元に、実行可能な単位に分解したもの。段階的に確認しながら上から順に実施する（design.mdは作成せず要件定義から直接タスク化する方針）。

## フェーズ1: Expo SDKアップグレード

- [x] 1. `npx expo install expo@^56.0.0`でExpo SDK本体をアップグレードする。→ `expo@56.0.21`、`react-native@0.85.3`、`react@19.2.3`。
- [x] 2. `npx expo install --fix`で関連パッケージ（react-native本体含む）をSDK 56の対応バージョンに揃える。
- [x] 3. `npx expo-doctor`を実行し、警告・エラーの内容を確認する。→ 当初6項目失敗。詳細は下記。
- [x] 4. `frontend/package.json`の変更内容を確認 → `app.json`にも変更（プラグイン等の追記）があったが問題なし。

### expo-doctorで判明した追加対応

- [x] 4a. `app.json`のスキーマエラー（`newArchEnabled`・`android.edgeToEdgeEnabled`がSDK56では無効なプロパティ）を修正 → 両方削除（**SDK56ではNew Architectureは常時有効でトグル自体が廃止されている**と判明したため、フェーズ3のタスク8は不要になった）。
- [x] 4b. 「SDK56ではexpo-routerとreact-navigationの併用不可」の指摘に対応。`app/_layout.tsx`（`@react-navigation/native`→`expo-router`）、`components/haptic-tab.tsx`（`@react-navigation/bottom-tabs`/`elements`→`expo-router/react-navigation`、型は`ComponentProps<typeof PlatformPressable>`に変更）を移行。未使用と判明した`@react-navigation/bottom-tabs`・`elements`・`native`・`stack`を`package.json`から削除。
- [x] 4c. 不足していたpeer dependency（`@react-native-async-storage/async-storage`、`@expo/metro-runtime`、`@expo/log-box`）を追加（`@expo/log-box`は無指定だと誤ってSDK57系が入ったため`^56.0.14`を明示指定）。

## フェーズ2: Jitsi SDKアップグレード

- [x] 5. `@jitsi/react-native-sdk`を`13.1.1`にアップグレードする。
- [x] 6. アップグレード後の`peerDependencies`を確認。11.6.3時点より対象範囲がSDK56に近づいており、不一致は以下のみだった: `react-native-svg`, `react-native-video`, `react-native-webrtc`, `react-native-webview`, `react-native-worklets-core`（コミットハッシュ更新）、`react-native-device-info`, `@react-native-google-signin/google-signin`, `@react-native-community/netinfo`, `@amplitude/analytics-react-native`, `@react-native-async-storage/async-storage`, `react-native-gesture-handler`, `react-native-safe-area-context`, `react-native-screens`, `react-native-splash-view`、および独自フォーク5パッケージ。（`react-native-pager-view`は`6.8.1`のまま変更不要だった）
- [x] 7. 6.の内容に基づき、`frontend/package.json`の該当パッケージをすべてJitsi指定の正確なバージョン・フォークに更新した。
  - **副次的な問題**: `yarn add`でGitHubフォーク（`https://github.com/jitsi/...`）を取得する際、gitのSSL証明書検証エラー（`unable to get local issuer certificate`）が発生。`git config --global http.sslbackend schannel`（Windows証明書ストアを使う設定）で解決した。

## フェーズ3: New Architecture有効化

- [x] 8. ~~`newArchEnabled`を`true`に戻す~~ → **不要と判明**。SDK56では`newArchEnabled`プロパティ自体がapp.jsonのスキーマから削除されており（New Architectureが常時有効固定のため）、フェーズ1のタスク4aで対応済み。
- [x] 9. `docs/frontend.md`の記述をSDK56へのアップグレードに伴い更新した。
- [x] 10. `frontend/babel.config.js`の`react-native-worklets-core/plugin`設定 → Jitsi 13.1.1でも`react-native-worklets-core`は引き続きpeerDependencyのため、設定を維持（変更不要）。

### 現時点で判明している未解消のリスク（`npx expo-doctor`より）

- **重複依存**: `@react-native-async-storage/async-storage`（自分たちの指定1.23.1 vs `@amplitude/analytics-react-native`が内包する1.24.0）、`react-native-screens`（自分たちの指定4.17.1 vs `expo-router`が内包する4.27.0）。ネイティブモジュールの重複はビルドエラーの原因になりうるため、実機ビルド時に注視する。
- **Hermes V1メモリリーク既知の不具合**: Expo SDK 56（`expo@56.0.21`のHermes）に既知のメモリ回帰があり、SDK57（RN 0.86.2+）で修正されている。Jitsi 13.1.1の`peerDependencies`が`react-native: ~0.85.0`（0.86系は対象外）と明記しているため、今回はSDK56に留まる判断とした。動作確認で問題があれば再検討する。

## フェーズ4: ビルド・動作確認

- [x] 11. `npx expo prebuild --clean`でネイティブプロジェクトを再生成する。→ 成功。`newArchEnabled=true`が`android/gradle.properties`に反映されていることを確認。`local.properties`は今回も自動生成されなかったため`sdk.dir`を手動で再作成した（[fix-android-sdk-location-error](../fix-android-sdk-location-error/)の既知の挙動）。
- [ ] 12. ユーザーに、Androidエミュレータ・実機でのビルド・動作確認を依頼する（[CLAUDE.md](../../../CLAUDE.md)の方針によりClaude Codeは自動実行しない）。
  - `Element type is invalid`クラッシュが再発しないか。
  - Home画面・Rooms画面等、Jitsi以外の既存画面が問題なく動作するか。
- [ ] 13. 発生した問題を都度切り分け、必要に応じて新規specとして記録する（本タスクリストで大量の問題を一度に扱わない）。

## フェーズ5: 完了処理

- [ ] 14. 動作確認完了後、[.kiro/specs/fix-jitsi-meeting-crash/tasks.md](../fix-jitsi-meeting-crash/tasks.md)を本アップグレードの内容で更新し、元のタスクを完了とする。
- [ ] 15. 作業ログを`logs/`に記録する。
