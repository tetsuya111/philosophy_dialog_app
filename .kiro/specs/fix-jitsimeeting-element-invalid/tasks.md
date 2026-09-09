# タスクリスト

[requirements.md](requirements.md)を元に、実行可能な単位に分解したもの（design.mdは作成せず要件定義から直接タスク化する方針）。上から順に実施する。

- [x] 1. `frontend/babel.config.js`の`react-native-worklets-core/plugin`を一時的にコメントアウトし、`Element type is invalid`が解消するか確認する → **解消せず**。worklets-core起因の仮説は否定された。設定を元に戻した（プラグイン有効のまま）。
- [x] 2. `components/Meeting.tsx`に`console.log('[diagnostic] typeof JitsiMeeting:', typeof JitsiMeeting, 'value:', JitsiMeeting);`を一時的に追加した。
- [x] 3. ユーザーが再度Meeting画面を開き、ターミナルログを確認 → `typeof JitsiMeeting: object value: {"$$typeof": Symbol(react.forward_ref), "render": [Function anonymous]}`。**`JitsiMeeting`自体は正常と判明**。
- [x] 4. `JitsiMeeting`は正常なため、LogBoxが示す行はエラーの実際の発生箇所ではなく代表表示と判断。`npx expo-doctor`で指摘されていた`react-native-screens`（`4.17.1`と`expo-router`内包の`4.27.0`）・`@react-native-async-storage/async-storage`（`1.23.1`と`@amplitude/analytics-react-native`内包の`1.24.0`）の重複を`4.27.0`・`1.24.0`にそれぞれ統一して解消した。
- [x] 5. `npx expo prebuild --clean`でネイティブプロジェクトを再生成し、ユーザーが再ビルド・動作確認 → **解消せず**。同一のエラー・同一タイミングで再発。
- [x] 6. `node_modules/@jitsi/react-native-sdk/react/features/base/app/components/BaseApp.tsx`の`componentDidCatch`に、`info.componentStack`を出力する診断用`console.log`を追加した（node_modules内への一時的な変更、JSのみの変更のためMetro再起動のみで反映可能・ネイティブ再ビルド不要）。
- [x] 7. ユーザーが再度Meeting画面を開き、`componentStack`の全文を取得できた。
- [x] 8. `componentStack`を分析し、`Icon`→`Container`→匿名コンポーネント（`IconComponent`=`props.src`）が原因箇所と特定。`@jitsi/react-native-sdk`のアイコンは`.svg`ファイルを直接importしており、`react-native-svg-transformer`（Metroのトランスフォーマー、Jitsi SDK自身の依存として既にインストール済み）が`frontend/metro.config.js`に設定されていなかったため、`.svg`インポートが生のアセット番号（数値）に解決され、それがそのままアイコンコンポーネントとして使われてクラッシュしていたと確定した。
- [x] 8a. `frontend/metro.config.js`に`react-native-svg-transformer`を設定した（`babelTransformerPath`・`assetExts`/`sourceExts`の調整）。
- [x] 9. 診断用の`console.log`を`components/Meeting.tsx`・`node_modules/@jitsi/react-native-sdk/.../BaseApp.tsx`の両方から削除した。
- [ ] 10. ユーザーにMetro再起動（キャッシュクリア推奨）の上で動作確認を依頼する（[CLAUDE.md](../../../CLAUDE.md)の方針によりClaude Codeは自動実行しない）。`Element type is invalid`が解消し、Jitsi Meetの通話UI（アイコン含む）が正しく表示されるか確認する。
- [x] 11. `docs/frontend.md`にmetro.config.jsの設定理由・`NavigationIndependentTree`の必要性を追記した。
- [ ] 12. 作業ログを`logs/`に記録する。
