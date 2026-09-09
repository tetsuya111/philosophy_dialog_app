# 作業ログ: expo-routerのreact-navigation直接import禁止チェックを無効化

## 何を行ったか

- `frontend/.env`を新規作成し、`EXPO_ROUTER_DISABLE_RN_NAVIGATION_CHECK=1`を設定した。
- `.kiro/specs/fix-meeting-join-crash/requirements.md`・`docs/frontend.md`に経緯を反映した。

## なぜ行ったか

前回の対応（`components/Meeting.tsx`で本物の`@react-navigation/native`から`NavigationIndependentTree`をimportする）の結果、expo-router自身が持つビルド時チェック（「アプリの依存グラフに`@react-navigation/*`が含まれてはいけない」）に引っかかり、Metroバンドリングが`As of SDK 56, expo-router is no longer compatible with react-navigation.`エラーで失敗するようになった。

このエラーメッセージ自体が案内する`EXPO_ROUTER_DISABLE_RN_NAVIGATION_CHECK=1`という環境変数は、今回のようにJitsi SDKとの相互運用のために意図的に`@react-navigation/*`を使うケース向けに用意された正規の回避手段のため、`frontend/.env`に設定した。秘密情報を含まないためリポジトリにコミットされる想定（`.gitignore`は`.env*.local`のみ除外）。

## 残作業

[CLAUDE.md](../CLAUDE.md)の方針により、Metro再起動・ビルド確認・「参加する」ボタンの動作確認はユーザーに依頼する。
