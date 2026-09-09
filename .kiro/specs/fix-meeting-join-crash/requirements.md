# 「参加する」ボタン押下時のエラー修正 要件定義書

## 背景・課題（Working Backwards）

[.kiro/specs/fix-jitsimeeting-element-invalid/](../fix-jitsimeeting-element-invalid/)の対応によりMeeting画面（プリジョイン画面）が正しく表示されるようになった。続けて「参加する」ボタンを押すと、実際にXMPP接続・ルーム作成・ロビー入室（knocking）までは進むが、ログに以下の複数のエラーが記録され、会議画面に入れずHome側へ戻ってしまう。

1. `Looks like you have nested a 'NavigationContainer' inside another. ...wrap the container in 'NavigationIndependentTree' explicitly.`（[.kiro/specs/fix-jitsi-nested-navigation-container/](../fix-jitsi-nested-navigation-container/)で対応したはずだが、会議参加・ロビー入室のタイミングで再発）
2. `The action 'GO_BACK' was not handled by any navigator. Is there any screen to go back to?`（開発時のみの警告）
3. `Uncaught (in promise, id: 0) TypeError: Cannot read property 'close' of null`（`components/Meeting.tsx`、`onReadyToClose`内の`jitsiMeeting.current.close()`）

## 根本原因（確定）

### 1. NavigationContainerの二重ネストエラー

Metroが実際に配信しているバンドルの依存グラフと、`@expo/cli`のリゾルバ実装を確認した結果、以下が確定した。

- `@jitsi/react-native-sdk`はReact Navigation **v6**（`@react-navigation/native@6.1.18`・`core@6.4.17`、Jitsi SDK自身の依存としてトップレベルにhoist）を使い、`RootNavigationContainer`・`ConferenceNavigationContainer`・`LobbyNavigationContainer`・`SettingsNavigationContainer`の4つの`<NavigationContainer independent={true}>`を持つ。`independent`プロップは**v6のAPI**で、v6コア（`@react-navigation/core/src/BaseNavigationContainer.tsx`、文言は`pass 'independent={true}' explicitly`）はこれを尊重する。
- expo-router（SDK56以降）は内製のReact Navigation **v7**コア（`node_modules/expo-router/build/react-navigation/core/`、文言は`wrap the container in 'NavigationIndependentTree' explicitly`）で動く。v7コアは`independent`プロップを**無視**し、`NavigationIndependentTreeContext`（v7 API）で独立ツリーを判定する。
- **決定的要因**: `@expo/cli/build/src/start/server/metro/withMetroMultiPlatform.js`（590〜614行目）のMetroリゾルバは、環境変数`EXPO_ROUTER_DISABLE_RN_NAVIGATION_CHECK`が未設定かつexpo-routerがインストールされている場合、**node_modules内からのものを含む全ての`@react-navigation/core`インポートを`expo-router/react-navigation`（内製v7コア）にリダイレクト**する（`if (moduleName === '@react-navigation/core') return doResolve('expo-router/react-navigation');`）。
- その結果、Jitsiの本物のv6 `@react-navigation/native`が読み込む`@react-navigation/core`が内製v7コアに差し替えられ、Jitsiの4つのコンテナはv7コアで動作していた。v7コアはv6の`independent={true}`を無視するため、Rootの内側にマウントされるConference/Lobby/Settingsコンテナが「二重ネスト」と判定されてthrowしていた（v7文言のエラーはここから出ていた）。エラーは会議参加（Conference）・ロビー入室（Lobby）のタイミングで発生し、これはユーザー報告のタイミングと完全に一致する。
- [.kiro/specs/fix-jitsi-nested-navigation-container/](../fix-jitsi-nested-navigation-container/)で`expo-router/react-navigation`の`NavigationIndependentTree`で`<JitsiMeeting>`を囲んだ対応は、（v7コアで動いていた）Rootコンテナに対してだけ効いていた。v7コアの`BaseNavigationContainer`は子孫に対して独立フラグをfalseにリセットするため、その内側のConference/Lobby/Settingsコンテナには効かず、再発した。

### 2. `NavigationIndependentTree`が`undefined`になった理由（本specの途中経過）

本spec着手時の暫定対応（本物の`@react-navigation/native`から`NavigationIndependentTree`をimport）は誤りだった。`frontend/.env`に`EXPO_ROUTER_DISABLE_RN_NAVIGATION_CHECK=1`を設定した時点で上記リダイレクトが無効化され、Jitsiは純粋なv6コアで動くようになる。v6コアは`NavigationIndependentTree`（v7 API）をエクスポートしていないため、importした値が`undefined`となり`Element type is invalid: ... got: undefined`が発生した。

### 3. `onReadyToClose`内でのnullエラー

`components/Meeting.tsx`の`onReadyToClose`は`router.back()`を呼んだ**直後**に`jitsiMeeting.current.close()`を呼んでいた。`router.back()`でMeeting画面がアンマウントされrefが`null`になった後に`.close()`を呼ぶため`TypeError`になっていた（1.のエラーで会議画面が崩れ、Jitsiが`onReadyToClose`を発火させた際に顕在化）。

## スコープ / Non-Goals

**スコープ:**

- Jitsi SDKが本来想定するv6コアで動作するよう、`@react-navigation/core`のリダイレクトを無効化し、二重ネストエラーを解消する。
- `onReadyToClose`のnull安全性を修正する。

**Non-Goals（今回は対応しない）:**

- `The action 'GO_BACK' was not handled by any navigator`警告への個別対応（1.の解消により連鎖的に消える見込み。残る場合は別途調査）。
- Jitsi SDKのロビー（Lobby）機能自体の動作確認・カスタマイズ。
- `flags`プロップの非サポートフラグ（[.kiro/specs/fix-jitsimeeting-element-invalid/](../fix-jitsimeeting-element-invalid/)で記録済み）の見直し。

## 成功指標

- 「参加する」ボタンを押した際、`Looks like you have nested a 'NavigationContainer' inside another`エラーがログに出ず、会議画面（またはロビー画面）が表示されること。
- 通話を終了・退出した際、`Cannot read property 'close' of null`エラーが発生せず、Home画面等に正しく戻れること。

## ユーザーストーリー・受け入れ基準

**ユーザーストーリー**: As a ユーザー, I want 「参加する」を押した後もエラーが出ずに通話できてほしい, so that ビデオ通話機能を実際に使って哲学対話ができる。

- WHEN 「参加する」ボタンを押し、Jitsiの会議・ロビー用NavigationContainerがマウントされるとき THE SYSTEM SHALL 二重ネストエラーを発生させない。
- WHEN 通話終了処理（`onReadyToClose`）が呼ばれたとき THE SYSTEM SHALL `jitsiMeeting.current`が`null`であっても例外を発生させず、安全に処理を完了する。

## 非機能要件

- アプリ側のコードでは引き続き`@react-navigation/*`を直接importしない（画面遷移はexpo-routerに統一）。今回の対応はリゾルバ設定（環境変数）のみで完結させ、Jitsi SDKのコードには手を入れない。

## 結果（対応済み）

- `frontend/.env`に`EXPO_ROUTER_DISABLE_RN_NAVIGATION_CHECK=1`を設定した（リポジトリにコミットされる想定。`.gitignore`は`.env*.local`のみ除外）。これにより`@react-navigation/core`→内製v7コアへのリダイレクトが無効化され、Jitsiは本物のv6コアで動作する。**このフラグはJitsi通話機能の必須設定**であり、`.env`内のコメントと[docs/frontend.md](../../../docs/frontend.md)に理由を明記した。
- `components/Meeting.tsx`から`NavigationIndependentTree`のimportとラッパーを削除した（v6の`independent={true}`が機能するため不要）。
- 暫定対応で追加していた`@react-navigation/native`の直接依存を`frontend/package.json`から削除した（Jitsi SDKの依存として`6.1.18`が引き続きhoistされていることを確認済み）。
- `onReadyToClose`を、`jitsiMeeting.current?.close()`を先に呼んでから`router.back()`を呼ぶ順序に変更した。

## オープンクエスチョン（実装・検証で確定させること）

- Metroをキャッシュクリアして再起動し、「参加する」ボタン押下後に会議画面（またはロビー画面）が表示され、二重ネストエラー・`GO_BACK`警告・`close of null`エラーがいずれも出ないことを実機で確認する。
- 上記で解消しない場合、ログ上のエラー文言が v6（`pass 'independent={true}'`）か v7（`wrap the container in 'NavigationIndependentTree'`）かで、どちらのコアがJitsi側で使われているかを切り分ける。
