# 作業ログ: react-native-pager-view未解決エラーの要件定義作成

## 何を行ったか

- `.kiro/specs/fix-jitsi-pager-view-dependency/requirements.md`を新規作成した。
- `.kiro/specs/fix-jitsi-meeting-crash/tasks.md`に、タスク1で行った`react-native-pager-view`削除が誤りだったことと、新specへのリンクを追記した。

## なぜ行ったか

Androidエミュレータでdev clientを起動しMeeting画面を開いたところ、以下のMetroバンドリングエラーで画面が表示できなかった。

```
Unable to resolve "react-native-pager-view" from "node_modules\react-native-tab-view\src\PagerViewAdapter.tsx"
```

インポートスタックを確認した結果、`@jitsi/react-native-sdk`が内部で提供するChat & Polls機能（`ChatAndPollsNavigator.tsx`）が`@react-navigation/material-top-tabs`→`react-native-tab-view`経由で`react-native-pager-view`に依存しており、`fix-jitsi-meeting-crash`の作業中に「アプリコードから未使用」と判断して削除したのが誤りだったと判明した（`node_modules`内の依存関係の依存関係までは確認できていなかった）。

`@jitsi/react-native-sdk`自身の`package.json`は`react-native-pager-view: 6.8.1`を依存として宣言しており、プロジェクトに元々入っていた`8.0.0`（New Architecture専用のcodegenインターフェースを要求し、Old Architectureでコンパイルエラーになったバージョン）より古い。`6.8.1`であればOld Architectureでコンパイルできる可能性が高く、設計フェーズで検証する。

`fix-jitsi-meeting-crash`本体のバグ（`Element type is invalid`クラッシュの確認）とは別の技術的課題（依存関係のバージョン選定）のため、新規specとして切り出した。
