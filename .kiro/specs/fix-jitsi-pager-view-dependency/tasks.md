# タスクリスト

[requirements.md](requirements.md)を元に、実行可能な単位に分解したもの（design.mdは作成せず要件定義から直接タスク化する方針）。上から順に実施する。

- [x] 1. `react-native-pager-view`を、`@jitsi/react-native-sdk`が依存として宣言しているバージョン`6.8.1`で`package.json`に追加する（`yarn add react-native-pager-view@6.8.1`）。→ peer dependency警告なくインストール成功。
- [x] 2. `frontend`ディレクトリで`npx expo prebuild --clean`を実行し、ネイティブプロジェクト（`android/`）を再生成する。→ 成功。なお`frontend/android/local.properties`は今回も自動生成されなかった（[fix-android-sdk-location-error](../fix-android-sdk-location-error/)の既知の挙動）ため、`SDK location not found`の再発防止に`sdk.dir`を手動で再作成した。
- [x] 3. ユーザーがAndroidネイティブビルド（`npm run android:win`）を実行 → **ビルド自体（`react-native-pager-view@6.8.1`のKotlinコンパイル含む）は成功**。`UnableToResolveError`も再発しなかった。
- [x] 3a.（新たに発覚）Meeting画面表示時にアプリがクラッシュ。logcat調査により`com.facebook.jni.CppException: Compiling JS failed: 458488:77:';' expected`（Metroが生成したJSバンドル自体の構文エラー）と判明。Claude Code側で`node_modules/expo-router/entry.bundle`を直接取得して再検証したところ、その回では構文エラーは再現せず正常なバンドルが返った。requirements.mdに詳細を反映済み。
- [ ] 4. ユーザーに、Metroのキャッシュをクリアして（dev client側のdevメニューで「Reload」、改善しなければ一度Metroを停止し`npx expo start -c`相当のキャッシュクリア付き再起動）再度Meeting画面を開いてもらい、`Compiling JS failed`エラーが再現するか確認してもらう（[CLAUDE.md](../../../CLAUDE.md)の方針によりClaude Codeは自動実行しない）。
- [ ] 5. タスク4で再現する場合、その時点のエラーメッセージ（行番号・列番号が今回と同じ458488:77か、変わっているか）とlogcatの該当箇所を共有してもらい、Claude Code側でバンドルの該当行を特定する。再現しない場合は解消したものとして扱う。
- [ ] 6. 確認結果を`requirements.md`の「オープンクエスチョン」および本ファイルに反映する。
- [ ] 7. 解消が確認できたら、[.kiro/specs/fix-jitsi-meeting-crash/tasks.md](../fix-jitsi-meeting-crash/tasks.md)のタスク6（Meeting画面のクラッシュ確認）に進めることをそちらのtasks.mdに反映する。
- [ ] 8. 作業ログを`logs/`に記録する。
