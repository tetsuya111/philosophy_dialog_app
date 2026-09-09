# 作業ログ: NavigationContainer二重ネストエラーの根本原因（@react-navigation/coreリダイレクト）特定と修正

## 何を行ったか

- Metroが配信しているライブバンドルを取得し、`@react-navigation/core`の本物（v6.4.17）とexpo-router内製（v7）の2モジュールがそれぞれどのファイルからimportされているかを依存グラフから特定した。
- `@expo/cli/build/src/start/server/metro/withMetroMultiPlatform.js`のリゾルバを確認し、`EXPO_ROUTER_DISABLE_RN_NAVIGATION_CHECK`未設定時に**全ての`@react-navigation/core`インポート（node_modules内含む）を`expo-router/react-navigation`にリダイレクトする**実装を発見した。
- `components/Meeting.tsx`から`NavigationIndependentTree`のimportとラッパーを削除した。
- `frontend/.env`のコメントを、本当の理由（リダイレクト無効化がJitsi通話の必須条件）に書き直した。
- 暫定対応で追加していた`@react-navigation/native`の直接依存を`package.json`から削除した（hoistされた`6.1.18`はJitsi SDKの依存として残ることを確認）。
- `docs/frontend.md`の該当記述を正しい内容に書き直し、`.kiro/specs/fix-meeting-join-crash/requirements.md`を根本原因ベースで全面改訂、`.kiro/specs/fix-jitsi-nested-navigation-container/requirements.md`に訂正を追記した。

## なぜ行ったか

前回の暫定対応（本物の`@react-navigation/native`から`NavigationIndependentTree`をimport）で`Element type is invalid ... got: undefined`が発生した。調査の結果、本物の`@react-navigation/core`はv6であり`NavigationIndependentTree`（v7 API）を持たないことが原因だった。

さらに、そもそも二重ネストエラー（v7文言）がなぜJitsi側で出ていたのかを突き止めた。Jitsi SDKはv6の`independent={true}`で4つのNavigationContainerを独立ツリーにしているが、Expo CLIのリゾルバが`@react-navigation/core`を内製v7コアに差し替えていたため、v6の`independent`プロップが無視されて内側のConference/Lobbyコンテナがthrowしていた。以前追加したラッパーはRootにしか効かなかった。

`.env`のフラグでリダイレクトを無効化すればJitsiは本来のv6コアで動き、ラッパー不要・エラー消滅が期待できるため、その状態に整理した。

## 残作業

[CLAUDE.md](../CLAUDE.md)の方針により、Metroのキャッシュクリア再起動と「参加する」ボタン以降の動作確認はユーザーに依頼する。
