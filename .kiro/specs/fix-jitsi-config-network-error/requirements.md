# Jitsi会議接続時の断続的エラー（invalid url / worklet関連）修正 要件定義書

## 背景・課題（Working Backwards）

Home画面の「一人で対話を開始する」ボタンからMeeting画面に遷移すると、以下の流れで問題が発生する。**Androidエミュレータ・実機（Xiaomi Redmi Note 9S、Wi-Fi/モバイルデータ通信の両方）で共通して再現する。**

1. 「一人で対話を開始する」ボタンを押す。
2. 「ミーティングに参加しています」（Joining meeting）という表示が出る。
3. まもなく「あなたは切断されました」（You have been disconnected）ダイアログが表示される（「キャンセル」「今すぐ再参加」ボタン付き）。
4. 「今すぐ再参加」（Rejoin Now）ボタンを押すと、`invalid url`エラーが発生する。

## 根本原因（特定済み）

logcat/LogBoxの詳細なエラーメッセージを確認したところ、以下が記録されていた。

```
[ERROR] [app:lib-jitsi-meet] Failed to load config from https://meet.jit.si/config.js?room=solo-1788671326758-rnxkc7
Error: In callInContext the function parameter is not a valid worklet and cannot be called between contexts or from/to JS from/to a context.
```

これは`react-native-worklets-core`（JSIベースのworklet実行ライブラリ）が発するエラーメッセージであり、ネットワークエラーではなく**Babelによるworklet関数の変換が行われていない**ことを示している。

### 特定した根本原因

- `@jitsi/react-native-sdk`（`package.json`）は`react-native-worklets-core`を直接の依存として宣言しており（`"react-native-worklets-core": "https://github.com/jitsi/react-native-worklets-core.git#..."`）、SDK内部（音声処理等）で実際に使用している。
- `react-native-worklets-core`の公式README（`node_modules/react-native-worklets-core/README.md`）には、セットアップ手順として**`babel.config.js`に`react-native-worklets-core/plugin`をBabelプラグインとして追加する必要がある**と明記されている。
- しかし`frontend/`ディレクトリには**`babel.config.js`が存在しない**（`package.json`の"main"がexpo-router経由でMetroのデフォルト設定を使っており、`babel-preset-expo`のみに依存している）。
- `babel-preset-expo`自体には`react-native-worklets-core`のプラグインを自動検出・自動適用する仕組みは無い（`node_modules/babel-preset-expo`内を検索したが該当する記述は見つからなかった）。
- 結果として、`react-native-worklets-core`内でworkletとして実行されるべき関数（`'worklet'`ディレクティブを持つ関数）がBabelで変換されないまま実行され、`callInContext`（worklet専用の実行コンテキスト呼び出し）に通常のJS関数が渡されるため、上記のエラーが発生していると判断できる。

### この結論が過去の観測結果と整合すること

- **エミュレータ・実機（Wi-Fi/モバイルデータ）で同一の問題が再現する**: Babelのビルド設定はプラットフォーム・ネットワークに依存しないため、整合する。
- **PCのブラウザでは問題が起きない**: ブラウザ版のJitsi Meetは`react-native-worklets-core`を使用しない別のWebクライアントであるため、影響を受けない。整合する。
- **エラーメッセージが毎回微妙に異なっていた**（`TypeError: Network request failed`だったり、今回の`worklet`エラーだったりする）: `loadConfig`処理内部でworklet呼び出しに失敗するタイミング・経路が実行のたびに異なり、异なるエラーとして表面化していた可能性が高い（すべて同一の「worklet変換が行われていない」という根本原因に起因すると推測される）。
- **`invalid url`（Rejoin Now押下時）**: 根本の接続失敗が解消されない限り、再接続処理も同じ理由で失敗し続け、[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)で確認した`appNavigate`のURL再構築処理に想定外の状態で到達し、副次的に発生している可能性が高い（worklet問題が解消すれば同時に解消される可能性が高いと考える）。

## スコープ / Non-Goals

**スコープ:**

- `frontend/babel.config.js`を新規作成し、`react-native-worklets-core/plugin`をBabelプラグインとして正しく設定する。
- 上記対応により、Meeting画面での「あなたは切断されました」→`invalid url`という一連の問題が解消することを実機・エミュレータの両方で確認する。

**Non-Goals（今回は対応しない）:**

- `meet.jit.si`（公開Jitsiサーバー）から自前ホストのJitsiサーバーへの切り替え。
- [.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)・[.kiro/specs/fix-jitsi-pager-view-dependency/](../fix-jitsi-pager-view-dependency/)・[.kiro/specs/fix-adb-install-user-restricted/](../fix-adb-install-user-restricted/)で対応済みの問題の再調査。
- `react-native-worklets-core`自体のバグ修正・fork・パッチ適用（アップストリームのライブラリであり、このリポジトリ側での修正対象ではない。今回はBabel設定の追加のみで対応する）。
- `react-native-reanimated`/`react-native-worklets`（[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)で削除済み、New Architecture専用）の再導入。今回追加する`react-native-worklets-core`は別のパッケージであり、Old Architectureでも動作する。

## 成功指標

- Home画面の「一人で対話を開始する」ボタンからMeeting画面を開いた際、「あなたは切断されました」ダイアログが表示されずに会議に接続できること。
- LogBox/logcatに`callInContext the function parameter is not a valid worklet`エラーが記録されないこと。
- Jitsi Meetの通話UI（カメラ映像・マイク入力・ツールバー）が表示されること（[.kiro/specs/fix-jitsi-meeting-crash/](../fix-jitsi-meeting-crash/)の元々の成功指標に合流する）。
- Androidエミュレータ・実機（Xiaomi Redmi Note 9S）の両方で確認する。

## ユーザーストーリー・受け入れ基準

**ユーザーストーリー**: As a ユーザー, I want Meeting画面を開いた際に会議接続がすぐ切断されないでほしい, so that ビデオ通話機能を実際に使って哲学対話ができる。

- WHEN `frontend/babel.config.js`に`react-native-worklets-core/plugin`を追加し、Metroのキャッシュをクリアして再起動したとき THE SYSTEM SHALL Meeting画面表示時に`callInContext ... not a valid worklet`エラーを発生させない。
- WHEN Home画面の「一人で対話を開始する」ボタンを押し、Meeting画面に遷移したとき THE SYSTEM SHALL 「あなたは切断されました」ダイアログを表示させることなく会議に接続する。

## 非機能要件

- Babel設定の追加は、`react-native-worklets-core`公式README記載の標準的な手順に従う（独自の回避策を取らない）。
- 変更後は必ずMetroのキャッシュをクリアして再起動する（Babel変換はキャッシュされるため、キャッシュクリアなしでは変更が反映されない点に注意）。

## オープンクエスチョン（実装・検証で確定させること）

- `babel.config.js`追加後、`npx expo start -c`（またはdev clientの再ビルド）でMetroキャッシュをクリアした上で、実際に問題が解消するか実機・エミュレータで確認する。
- `babel-preset-expo`と`react-native-worklets-core/plugin`のプラグイン適用順序（他のBabelプラグインとの兼ね合い）で問題が起きないか確認する。
- 解消しない場合、`react-native-worklets-core`のバージョン（`node_modules`にインストールされているコミットハッシュ）と、`@jitsi/react-native-sdk`が要求するバージョンとの整合性を再確認する。
