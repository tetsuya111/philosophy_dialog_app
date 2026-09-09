# タスクリスト

[design.md](design.md)の「設計」セクションを実行可能な単位に分解したもの。上から順に実施する。

- [x] 1. `react-native-reanimated`/`react-native-worklets`（New Architecture専用、実アプリでは未使用と判明）を`package.json`から削除する（`yarn remove`）。
- [x] 1a. （タスク実行中に追加で発覚）`react-native-pager-view`もOld Architectureでコンパイルエラー（`RNCViewPagerManagerDelegate`等codegenインターフェース未解決）を起こしたため削除。**→ 後日これは誤りと判明**: `@jitsi/react-native-sdk`のChat & Polls機能が内部で必要としており、削除するとMetroバンドリングが`UnableToResolveError`で失敗する。対応は[.kiro/specs/fix-jitsi-pager-view-dependency/](../fix-jitsi-pager-view-dependency/)を参照（別specとして切り出し、本specでは復元しない）。
- [x] 2. `frontend/app.json`の`expo.newArchEnabled`を`false`に変更する。
- [x] 3. `frontend/docs`向けの規約ドキュメント[docs/frontend.md](../../../docs/frontend.md)に、New Architectureを無効化している理由（`@jitsi/react-native-sdk`との非互換）と、reanimated/worklets削除の経緯を追記する。
- [x] 4. `npx expo prebuild --clean`（frontendディレクトリ）でネイティブプロジェクト（`android/`等）を再生成する。
- [x] 5. `npx expo run:android`（またはWindowsでは`npm run android:win`）でdev clientを再ビルド・再インストールする。→ ビルド・インストール自体は成功したが、Meeting画面表示時に[.kiro/specs/fix-jitsi-pager-view-dependency/](../fix-jitsi-pager-view-dependency/)のエラーが発生し、本来のクラッシュ（`Element type is invalid`）を確認する前にブロックされている。
- [ ] 6. [manuals/video-call-testing.md](../../../manuals/video-call-testing.md)の手順に従い、Home画面の「一人で対話を開始する」ボタンからMeeting画面を開き、クラッシュ（`Element type is invalid`）が再現しないこと・通話UIが表示されることを確認する。→ [fix-jitsi-pager-view-dependency](../fix-jitsi-pager-view-dependency/)の解消後に再実施。
- [ ] 7. 確認結果（直った/直らなかった）と、直らなかった場合の追加調査内容を`requirements.md`の「オープンクエスチョン」および本ファイルに反映する。
- [ ] 8. 作業ログを`logs/`に記録する。
