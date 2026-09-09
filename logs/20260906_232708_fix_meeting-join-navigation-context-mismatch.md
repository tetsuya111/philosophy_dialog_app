# 作業ログ: 「参加する」ボタン押下時のNavigationContainer二重ネスト再発・nullエラーの修正

## 何を行ったか

- `.kiro/specs/fix-meeting-join-crash/requirements.md`を新規作成した。
- `@react-navigation/native@6.1.18`（Jitsi SDK自身が使用するバージョンと完全一致、既にhoistされていたため新規インストールは発生せず）を`frontend/package.json`の直接の依存関係に追加した。
- `frontend/components/Meeting.tsx`の`NavigationIndependentTree`のimport元を`expo-router/react-navigation`から`@react-navigation/native`に変更した。
- 同ファイルの`onReadyToClose`を、`jitsiMeeting.current?.close()`を先に呼んでから`router.back()`を呼ぶ順序に変更し、null安全にした。
- `docs/frontend.md`にこの意図的な例外を追記した。

## なぜ行ったか

Meeting画面のプリジョイン表示（[.kiro/specs/fix-jitsimeeting-element-invalid/](../.kiro/specs/fix-jitsimeeting-element-invalid/)で解決済み）の後、「参加する」ボタンを押すと以下3つのエラーが記録された。

1. `Looks like you have nested a 'NavigationContainer' inside another`（[.kiro/specs/fix-jitsi-nested-navigation-container/](../.kiro/specs/fix-jitsi-nested-navigation-container/)で対応したはずが再発）
2. `The action 'GO_BACK' was not handled by any navigator`
3. `Uncaught (in promise, id: 0) TypeError: Cannot read property 'close' of null`（`Meeting.tsx:20`）

調査の結果、1.の再発は、以前`expo-router/react-navigation`からimportしていた`NavigationIndependentTree`が、Jitsi SDK内部が実際に使う本物の`@react-navigation/native`パッケージ（`node_modules`にhoistされた`6.1.18`）とは**別モジュールインスタンス**（expo-router内部にバンドルされた独自コピー）だったため、React Contextが一致せず二重ネスト検知を回避できていなかったことが原因と判明した。本物の`@react-navigation/native`から`NavigationIndependentTree`をimportするよう修正した。

3.は`onReadyToClose`内で`router.back()`（Meeting画面をアンマウントさせうる）を`jitsiMeeting.current.close()`より先に呼んでいたため、アンマウントでrefが`null`になった後に`.close()`を呼んでエラーになっていたと判明した。呼び出し順序の入れ替えとオプショナルチェイニングで対応した。

## 残作業

[CLAUDE.md](../CLAUDE.md)の方針により、ビルド・動作確認はユーザーに依頼する。「参加する」ボタン押下時・通話終了時にエラーが解消するか確認が必要。
