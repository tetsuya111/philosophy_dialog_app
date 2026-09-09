# 作業ログ: Meeting画面クラッシュ（Compiling JS failed）の調査

## 何を行ったか

- `react-native-pager-view@6.8.1`導入後、ユーザーがAndroidビルド（`npm run android:win`）を実行し、ビルド自体（Kotlinコンパイル含む）は成功、`UnableToResolveError`も再発しないことを確認した。
- しかしMeeting画面表示時にアプリがクラッシュしたため、`adb logcat`でエラー内容を直接調査した。
- logcatから`com.facebook.jni.CppException: Compiling JS failed: 458488:77:';' expected`という、Metroが生成したJSバンドル自体の構文エラーを発見した。
- 原因箇所を特定するため、`node_modules/expo-router/entry.bundle`をMetro開発サーバーから直接HTTP取得して内容を確認したが、この回では構文エラーは含まれておらず正常なバンドルだった。
- `.kiro/specs/fix-jitsi-pager-view-dependency/requirements.md`・`tasks.md`にここまでの調査結果を反映した。

## なぜ行ったか

ユーザーから「結果は変わらず」の報告と、Meeting画面での新しいクラッシュ画面（`Attempting to call JS function on a...`、画面上で切れていた）の共有を受け、原因特定のため。画面のスクリーンショットだけでは全文が読めなかったため、[CLAUDE.md](../CLAUDE.md)の方針（frontendのビルド実行はしない）に反しない範囲で、既に起動中のエミュレータ・Metroに対する読み取り専用の調査（`adb logcat`、Metroへの直接HTTPリクエスト）を行い、根本原因の特定を試みた。

## 分かったこと・残課題

- Androidネイティブビルド自体は正常。問題はJSバンドルのコンパイル段階で発生している。
- 原因がバンドルのどのモジュール由来かは未特定（`react-native-pager-view@6.8.1`が疑わしいが確証はない）。
- 再取得したバンドルでは再現しなかったため、Metroのキャッシュ状態や実機からのリクエストパラメータ依存で発生条件が変わる可能性がある。
- ユーザーに、Metroのキャッシュクリア後の再現有無の確認を依頼した（`.kiro/specs/fix-jitsi-pager-view-dependency/tasks.md`タスク4・5）。
