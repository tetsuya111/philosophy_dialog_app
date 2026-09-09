# react-native-pager-view未解決エラー修正 要件定義書

## 背景・課題（Working Backwards）

Android実機/エミュレータでdev clientを起動し、Meeting画面（`app/meeting.tsx`）を開こうとすると、以下のMetroバンドリングエラーが発生し、画面が表示されない。

```
There was a problem loading the project.
This development build encountered the following error.

com.facebook.react.common.DebugServerException: The development...
URL: http://192.168.1.224:8081/node_modules/expo-router/entry.b...
{"type":"UnableToResolveError","originModulePath":"C:\\Users\\U...
```

Metroターミナルの完全なログでは以下の通り。

```
Unable to resolve "react-native-pager-view" from "node_modules\react-native-tab-view\src\PagerViewAdapter.tsx"
```

依存関係のインポートスタックは以下の経路であり、いずれもアプリのコード（`app/`・`components/`）から直接importしているものではない。

```
app/meeting.tsx
 → components/Meeting.tsx
 → @jitsi/react-native-sdk (index.tsx)
 → .../app/components/App.native.tsx
 → .../app/middlewares.native.ts → middlewares.any.ts → middleware.ts
 → .../mobile/navigation/components/RootNavigationContainer.tsx
 → .../conference/components/ConferenceNavigationContainer.tsx
 → .../chat/components/ChatAndPollsNavigator.tsx
 → @react-navigation/material-top-tabs
 → react-native-tab-view
 → react-native-tab-view/src/PagerViewAdapter.tsx
 → react-native-pager-view（ここで解決失敗）
```

つまり`@jitsi/react-native-sdk`が内部で提供するチャット/投票（Chat & Polls）機能のUI（`ChatAndPollsNavigator`）が、タブ表示のために`@react-navigation/material-top-tabs`（→`react-native-tab-view`→`react-native-pager-view`）を利用しており、`react-native-pager-view`がインストールされていないため解決に失敗している。

### 発生経緯（[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)との関係）

`fix-jitsi-meeting-crash`のNew Architecture無効化作業（`newArchEnabled: false`）の中で、`react-native-pager-view@8.0.0`（当時プロジェクトの`package.json`にインストールされていたバージョン）がOld Architecture環境でKotlinコンパイルエラー（`RNCViewPagerManagerDelegate`/`RNCViewPagerManagerInterface`が未解決、いずれもNew Architecture専用のcodegen生成インターフェース）を起こしたため、その時点でアプリの`app/`配下から直接使われていないことを確認した上で`yarn remove`していた。

しかし今回判明した通り、`react-native-pager-view`は**アプリコードからは未使用でも、`@jitsi/react-native-sdk`の内部機能（Chat & Polls）が依存する実際に必要なパッケージ**だった。削除時の調査（アプリの`app/`/`components/`配下のみをgrep）が`node_modules`内の依存関係の依存関係（Jitsi SDK自身が要求するパッケージ）まで追えていなかったことが誤りの原因である。

`@jitsi/react-native-sdk`自身の`package.json`を確認したところ、以下のバージョンが依存として宣言されている。

```
"@react-navigation/material-top-tabs": "6.6.13",
"react-native-tab-view": "3.5.2",
"react-native-pager-view": "6.8.1",
```

プロジェクトに元々入っていた`8.0.0`は、Jitsi SDKが実際に想定・テストしているバージョン（`6.8.1`）よりも新しい。`8.0.0`でNew Architecture専用のcodegenインターフェースが必須になった一方、`6.8.1`はその変更以前のバージョンである可能性が高い（設計フェーズで検証が必要）。

## スコープ / Non-Goals

**スコープ:**

- Meeting画面を開いた際に発生する、`react-native-pager-view`の`UnableToResolveError`（Metroバンドリングエラー）の解消。
- `newArchEnabled: false`（[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)で決定済み、変更しない）を維持したまま、`react-native-pager-view`を含むAndroidネイティブビルド（`gradlew app:assembleDebug`）が成功する状態にすること。

**Non-Goals（今回は対応しない）:**

- New Architectureの再有効化（`fix-jitsi-meeting-crash`で`@jitsi/react-native-sdk`自体の非互換を理由に無効化を決定済みであり、本タスクでは覆さない）。
- `@jitsi/react-native-sdk`が内部で提供するChat & Polls機能自体の動作確認・機能テスト（本タスクはビルド・画面表示のブロッカー解消が目的であり、Chat & Polls機能を実際に開いて動作確認するかは[manuals/video-call-testing.md](../../../manuals/video-call-testing.md)の既存範囲外。必要であれば別途manualsに追記する）。
- `react-native-pager-view`以外の、削除済みパッケージ（`react-native-reanimated`/`react-native-worklets`）の復元（これらは実アプリ・Jitsi SDKいずれからも未使用であることを確認済みであり、対象外）。
- 依存関係全体（`package.json`の全パッケージ）に対する、同種の「app未使用だがJitsi SDK内部で必要」ケースの網羅的な再監査（今回発生した`react-native-pager-view`のみを対象とする）。

## 成功指標

- Home画面の「一人で対話を開始する」ボタンからMeeting画面に遷移した際、`UnableToResolveError`（`react-native-pager-view`関連）によるバンドリング失敗が発生しないこと。
- `newArchEnabled: false`の状態で、Androidネイティブビルド（`npx expo run:android` / `npm run android:win`）が`react-native-pager-view`のコンパイルエラーなく成功すること。
- [manuals/video-call-testing.md](../../../manuals/video-call-testing.md)の既存手順に従い、Jitsi Meetの通話UIが表示されること（[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)の成功指標を再度満たすこと）。

## ユーザーストーリー・受け入れ基準

**ユーザーストーリー**: As a ユーザー, I want Meeting画面を開いてもバンドリングエラーが起きないでほしい, so that ビデオ通話機能を実際に使って哲学対話ができる。

- WHEN Meeting画面（`app/meeting.tsx`）のバンドルがMetroにリクエストされたとき THE SYSTEM SHALL `react-native-pager-view`を含むすべてのimportを解決し、`UnableToResolveError`を発生させない。

**ユーザーストーリー**: As a 開発者, I want `newArchEnabled: false`の環境でも`react-native-pager-view`のネイティブビルドが通ってほしい, so that Jitsi SDKのChat & Polls機能を含むアプリ全体をビルド・実行できる。

- WHEN `newArchEnabled: false`の状態でAndroidネイティブビルド（`gradlew app:assembleDebug`）を実行したとき THE SYSTEM SHALL `react-native-pager-view`のKotlinコンパイルをエラーなく完了する。
- IF 現在インストール可能などのバージョンの`react-native-pager-view`もOld Architectureでコンパイルできないことが設計フェーズで判明した場合 THEN THE SYSTEM SHALL 代替案（例: Chat & Polls機能を無効化する設定がJitsi SDK側にあるか等）をdesign.mdに検討・明記する。

## 非機能要件

- `react-native-pager-view`のバージョン選定は、`@jitsi/react-native-sdk`が実際に依存として宣言しているバージョン（`6.8.1`）との整合性を優先する（Jitsi SDKが動作検証済みの組み合わせから逸脱しない）。
- 依存パッケージを削除・変更する際は、アプリの`app/`/`components/`配下だけでなく、`node_modules`内の依存関係（特に`@jitsi/react-native-sdk`のような中核機能を提供するSDKの依存ツリー）まで確認する（今回の教訓。[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)の反省点として明記する）。

## オープンクエスチョン（設計フェーズで確定させること）

- ~~`react-native-pager-view@6.8.1`がOld Architectureでコンパイルできるか~~ → **一部解決・新たな問題が判明**: Androidネイティブビルド（Kotlinコンパイル）自体は成功した。しかしMeeting画面表示時にアプリがクラッシュし、logcatに以下のエラーが記録された。

  ```
  E DevLauncher: com.facebook.jni.CppException: Compiling JS failed: 458488:77:';' expected
  E AndroidRuntime: FATAL EXCEPTION: mqt_js
  E AndroidRuntime: java.lang.RuntimeException: Attempting to call JS function on a bad application bundle: AppRegistry.runApplication()
  ```

  つまりMetroが生成したJSバンドル自体に構文エラーがあり、Hermes（またはJSエンジン）がバンドルのコンパイルに失敗している。バンドル行458488列77付近が原因だが、具体的にどのモジュール由来かは未特定。

- **追加調査で判明した事実**: Metro開発サーバーに対して`node_modules/expo-router/entry.bundle`を直接リクエストして取得したバンドルを確認したところ、この回では構文エラーは含まれておらず、正常に末尾（`__r(0);`と`sourceMappingURL`）まで完結していた。したがって、(a) Metroのキャッシュが後から回復した、(b) 実機アプリが送るリクエストパラメータ（例: Hermes向けのtransformオプション等）が今回の直接リクエストと異なり、特定の条件でのみ発生する、のいずれかの可能性がある。**現時点で確実に再現する手順が確立できていない。**
- `react-native-pager-view@6.8.1`が原因かどうか自体も未確定（バージョン変更の直後に発生したため疑わしいが、他のモジュール由来の可能性も残る）。
- `react-native-tab-view`（`3.5.2`、peerDependencyとして`react-native-pager-view: *`を要求）・`@react-navigation/material-top-tabs`（`6.6.13`）についても、プロジェクトの`package.json`に明示的な依存として追加すべきか、`@jitsi/react-native-sdk`経由の推移的依存のままで解決可能かを確認する。
- 次のアクション（[tasks.md](tasks.md)）: ユーザーに、Metroのキャッシュをクリアして（`npx expo start -c`相当、またはdev client側で「Reload」）再度Meeting画面を開いてもらい、同じ`Compiling JS failed`エラーが再現するか確認する。再現する場合は、バンドルを直接取得して該当行の内容を特定する。
