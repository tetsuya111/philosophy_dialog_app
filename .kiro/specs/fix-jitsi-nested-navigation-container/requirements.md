# Jitsi埋め込み時のNavigationContainer二重ネストエラー修正 要件定義書

## 背景・課題（Working Backwards）

[.kiro/specs/upgrade-expo-sdk56-jitsi13/](../upgrade-expo-sdk56-jitsi13/)・[.kiro/specs/fix-worklets-core-missing-babel-plugins/](../fix-worklets-core-missing-babel-plugins/)の対応によりMetroバンドリングが完了するようになった後、Meeting画面表示時に以下のConsole Errorが発生する。

```
2026-09-06T10:42:13.099Z [ERROR] [app:base-app]
Error: Looks like you have nested a 'NavigationContainer' inside another. Normally you need only one container at the root of the app, so this was probably an error. If this was intentional, wrap the container in 'NavigationIndependentTree' explicitly.
```

コールスタックは`components/Meeting.tsx:33`の`<JitsiMeeting`から発生している。

## 根本原因（特定済み）

`@jitsi/react-native-sdk`のソース（`node_modules/@jitsi/react-native-sdk/react/features/mobile/navigation/components/RootNavigationContainer.tsx`）を確認したところ、Jitsi SDK自身が内部で`@react-navigation/native`の`NavigationContainer`を使って、会議・チャット等の画面遷移を管理していることを確認した（1行目`import { NavigationContainer, ... } from '@react-navigation/native';`、61行目で`<NavigationContainer>`を使用）。

一方、このアプリ（`app/`配下）はexpo-routerでルーティングしており、expo-router自身も内部で（React Navigationをベースにした）ルートの`NavigationContainer`を持つ。`app/meeting.tsx`（expo-routerのルート画面）の中で`<Meeting>`→`<JitsiMeeting>`をレンダリングすると、expo-routerの外側のNavigationContainerの中に、Jitsi SDKが持つ内側のNavigationContainerがネストされる形になり、React Navigationが二重ネストとして検知しエラーを出している。

Jitsi SDK側の`RootNavigationContainer.tsx`は、この二重ネストを想定した`NavigationIndependentTree`（React Navigationが提供する、意図的なネストを許可するためのラッパー）を使っていない。これはJitsi SDK自身の実装上のギャップであり、このリポジトリ側で修正できない（アップストリームのコード）。

## スコープ / Non-Goals

**スコープ:**

- ホストアプリ側（このリポジトリ）で、`<JitsiMeeting>`を描画する箇所を`NavigationIndependentTree`（`expo-router/react-navigation`経由で利用可能なことを確認済み。`expo-router/react-navigation` → `./native` → `../core`の再エクスポートチェーンに含まれる）で囲み、Jitsi内部のNavigationContainerを「意図的な独立したネスト」として扱えるようにする。

**Non-Goals（今回は対応しない）:**

- `@jitsi/react-native-sdk`自体のコード修正・fork（`RootNavigationContainer.tsx`に`NavigationIndependentTree`を追加するのが本来望ましい対応だが、アップストリームの修正対象でありこのリポジトリでは行わない）。
- [.kiro/specs/upgrade-expo-sdk56-jitsi13/](../upgrade-expo-sdk56-jitsi13/)・[.kiro/specs/fix-worklets-core-missing-babel-plugins/](../fix-worklets-core-missing-babel-plugins/)で対応済みの内容の再調査。

## 成功指標

- Home画面の「一人で対話を開始する」ボタンからMeeting画面を開いた際、`Looks like you have nested a 'NavigationContainer' inside another`のConsole Errorが発生しないこと。
- Jitsi Meetの通話UIが正常に表示・操作できること（画面遷移含む）。

## ユーザーストーリー・受け入れ基準

**ユーザーストーリー**: As a ユーザー, I want Meeting画面を開いた際にナビゲーション関連のエラーが出ないでほしい, so that ビデオ通話機能を実際に使って哲学対話ができる。

- WHEN Meeting画面（`components/Meeting.tsx`）で`<JitsiMeeting>`がレンダリングされたとき THE SYSTEM SHALL `NavigationContainer`の二重ネストエラーを発生させない。

## 非機能要件

- `NavigationIndependentTree`は、SDK56移行時の方針（[docs/frontend.md](../../../docs/frontend.md)参照）に従い、`@react-navigation/native`を直接の依存関係に追加せず、`expo-router/react-navigation`経由でimportする。

## 結果（対応済み）

`components/Meeting.tsx`で、`import { NavigationIndependentTree } from 'expo-router/react-navigation';`を追加し、`<JitsiMeeting ... />`全体を`<NavigationIndependentTree>...</NavigationIndependentTree>`で囲んだ。

## 訂正（後日判明）

上記の対応は**Rootコンテナにしか効かず、本質的な解決ではなかった**。真の原因は、Expo CLIのMetroリゾルバが`@react-navigation/core`（Jitsiが使うv6コア）をexpo-router内製のv7コアにリダイレクトしていたことで、Jitsi自身の`independent={true}`（v6 API）が無視されていた点にある。会議参加時にマウントされる内側のコンテナ（Conference/Lobby）で同じエラーが再発したため、[.kiro/specs/fix-meeting-join-crash/](../fix-meeting-join-crash/)で根本対応（`EXPO_ROUTER_DISABLE_RN_NAVIGATION_CHECK=1`でリダイレクトを無効化）に切り替え、本specで追加したラッパーは削除した。

## オープンクエスチョン（実装・検証で確定させること）

- `NavigationIndependentTree`で`<JitsiMeeting>`を囲んだ後、`Looks like you have nested a 'NavigationContainer'`エラーが解消するか、Jitsi内部の画面遷移（Chat & Polls、プリジョイン画面等）が正しく動作するかを実機・エミュレータで確認する。
- Web版（`components/Meeting.web.tsx`）は`JitsiMeeting`（React Nativeコンポーネント）を使わず別方式（`external_api.js`）のため、本対応の対象外（変更していない）。
