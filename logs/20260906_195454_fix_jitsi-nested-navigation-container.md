# 作業ログ: JitsiMeetingのNavigationContainer二重ネストエラー修正

## 何を行ったか

- `.kiro/specs/fix-jitsi-nested-navigation-container/requirements.md`を新規作成した。
- `frontend/components/Meeting.tsx`に`import { NavigationIndependentTree } from 'expo-router/react-navigation';`を追加し、`<JitsiMeeting ... />`を`<NavigationIndependentTree>`で囲んだ。

## なぜ行ったか

[.kiro/specs/upgrade-expo-sdk56-jitsi13/](../.kiro/specs/upgrade-expo-sdk56-jitsi13/)・[.kiro/specs/fix-worklets-core-missing-babel-plugins/](../.kiro/specs/fix-worklets-core-missing-babel-plugins/)の対応でMetroバンドリングが完了するようになった後、Meeting画面表示時に`Looks like you have nested a 'NavigationContainer' inside another`というConsole Errorが発生した。

`@jitsi/react-native-sdk`のソース（`RootNavigationContainer.tsx`）を確認したところ、Jitsi SDK自身が内部で`@react-navigation/native`の`NavigationContainer`を使っており、これがexpo-router自身のNavigationContainerの中にネストされることでReact Navigationが二重ネストと検知していると判明した。Jitsi SDK側はこれを`NavigationIndependentTree`でラップしておらず、アップストリームの実装ギャップであるため、ホストアプリ側（このリポジトリ）で`<JitsiMeeting>`の描画箇所を`NavigationIndependentTree`で囲むことで対応した。`NavigationIndependentTree`は`@react-navigation/native`への直接依存を避けるため、[.kiro/specs/upgrade-expo-sdk56-jitsi13/](../.kiro/specs/upgrade-expo-sdk56-jitsi13/)の方針通り`expo-router/react-navigation`経由でimportした。

## 残作業

[CLAUDE.md](../CLAUDE.md)の方針により、ビルド・動作確認（エラー解消、Jitsi内部の画面遷移が正しく動作するか）はユーザーに依頼する。
