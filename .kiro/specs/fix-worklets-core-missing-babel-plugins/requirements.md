# react-native-worklets-coreが要求するBabelプラグイン不足の修正 要件定義書

## 背景・課題（Working Backwards）

[.kiro/specs/fix-jitsi-config-network-error/](../fix-jitsi-config-network-error/)で`frontend/babel.config.js`を新規作成し`react-native-worklets-core/plugin`を有効化した結果、Metroバンドリングが以下のエラーで失敗するようになった。

```
Android Bundling failed 33755ms node_modules\expo-router\entry.js (4712 modules)
 ERROR  Error: ...\node_modules\@jitsi\react-native-sdk\react\features\base\lib-jitsi-meet\functions.native.ts: Cannot find module '@babel/plugin-proposal-nullish-coalescing-operator'
...
Did you mean "@babel/plugin-transform-optional-chaining"?
```

スタックトレースの末尾は`react-native-worklets-core/src/plugin/index.js`の`makeWorklet`/`processWorkletFunction`であり、worklet関数を個別にBabelで再変換する内部処理中に発生している。

## 根本原因（特定済み）

`node_modules/react-native-worklets-core/src/plugin/index.js`（417〜421行目）を確認したところ、worklet関数を隔離してコンパイルする際に、以下5つのBabelプラグインをハードコードで指定していることが判明した。

```js
"@babel/plugin-transform-shorthand-properties",
"@babel/plugin-transform-arrow-functions",
"@babel/plugin-proposal-optional-chaining",
"@babel/plugin-proposal-nullish-coalescing-operator",
["@babel/plugin-transform-template-literals", { loose: true }],
```

このうち`@babel/plugin-proposal-optional-chaining`・`@babel/plugin-proposal-nullish-coalescing-operator`は、Babel 7.16以降で対応する`@babel/plugin-transform-*`パッケージに統合され廃止された名称であり、現在の`@babel/core`（`7.28.6`）環境では別パッケージとして単独インストールされていない限り解決できない。

`frontend/node_modules`を実際に確認した結果は以下の通り。

| プラグイン | 状態 |
| --- | --- |
| `@babel/plugin-transform-shorthand-properties` | インストール済み |
| `@babel/plugin-transform-arrow-functions` | インストール済み |
| `@babel/plugin-proposal-optional-chaining` | インストール済み（他の依存経由で解決できている） |
| `@babel/plugin-proposal-nullish-coalescing-operator` | **未インストール**（今回報告されたエラーの直接原因） |
| `@babel/plugin-transform-template-literals` | **未インストール**（`nullish-coalescing-operator`を解決した直後に同様のエラーとして発生することが予想される） |

つまり、今回報告されたエラーを個別に解消しても、その直後に`@babel/plugin-transform-template-literals`不足の同種エラーが連鎖して発生する見込みである。

## スコープ / Non-Goals

**スコープ:**

- `@babel/plugin-proposal-nullish-coalescing-operator`・`@babel/plugin-transform-template-literals`を`frontend/package.json`の依存関係に追加し、`react-native-worklets-core`のworkletコンパイルがエラーなく完了する状態にすること。

**Non-Goals（今回は対応しない）:**

- `react-native-worklets-core`自体のコード修正・fork（アップストリームの実装がハードコードで古いパッケージ名を参照している問題であり、このリポジトリ側での修正対象ではない）。
- [.kiro/specs/fix-jitsi-config-network-error/](../fix-jitsi-config-network-error/)本体の検証（worklet設定が正しく機能してMeeting画面の接続問題が解消するかの確認）は、本specの対応完了後に改めて行う。

## 成功指標

- `npx expo start -c`（キャッシュクリア）でMetroバンドリングを実行した際、`Cannot find module '@babel/plugin-proposal-*'`・`@babel/plugin-transform-template-literals`のいずれのエラーも発生せず、バンドリングが完了すること。

## ユーザーストーリー・受け入れ基準

**ユーザーストーリー**: As a 開発者, I want Metroバンドリングが`react-native-worklets-core`のworklet変換で失敗しないでほしい, so that [.kiro/specs/fix-jitsi-config-network-error/](../fix-jitsi-config-network-error/)で追加したBabel設定が正しく機能する状態でJitsiの動作確認を進められる。

- WHEN Metroが`@jitsi/react-native-sdk`内のworklet関数をコンパイルするとき THE SYSTEM SHALL `@babel/plugin-proposal-nullish-coalescing-operator`・`@babel/plugin-transform-template-literals`のいずれについても`Cannot find module`エラーを発生させない。

## 非機能要件

- 追加するBabelプラグインのバージョンは、既存の`@babel/core`（`7.28.6`）・他の`@babel/plugin-transform-*`系パッケージ（`7.27.1`系）とメジャーバージョンの整合を取る。

## 結果（対応済み）

`yarn add -D`で2パッケージを追加した。なお`@babel/plugin-transform-template-literals`は無指定でインストールすると誤って`8.0.1`（`@babel/core@^8.0.0`を要求するBabel 8系）が解決されてしまったため、`^7.27.1`を明示指定して`7.29.7`（`@babel/core@^7.0.0-0`と互換）に固定し直した。

- `@babel/plugin-proposal-nullish-coalescing-operator@7.18.6`
- `@babel/plugin-transform-template-literals@7.29.7`

## 再発（[.kiro/specs/upgrade-expo-sdk56-jitsi13/](../upgrade-expo-sdk56-jitsi13/)アップグレード後）

Expo SDK 56へのアップグレード後、今度は以下のエラーで再発した。

```
Android Bundling failed 61261ms node_modules\expo-router\entry.js (4933 modules)
 ERROR  Error: ...\@jitsi\react-native-sdk\react\features\base\lib-jitsi-meet\functions.native.ts: Cannot find module '@babel/plugin-transform-shorthand-properties'
```

`frontend/node_modules`を再確認したところ、以下の通り状況が入れ替わっていた。

| プラグイン | 状態（今回） |
| --- | --- |
| `@babel/plugin-transform-shorthand-properties` | **未インストール**（今回の直接原因） |
| `@babel/plugin-transform-arrow-functions` | **未インストール**（次に連鎖するエラーと予想される） |
| `@babel/plugin-proposal-optional-chaining` | インストール済み |
| `@babel/plugin-proposal-nullish-coalescing-operator` | インストール済み（前回対応分） |
| `@babel/plugin-transform-template-literals` | インストール済み（前回対応分） |

**根本原因**: 前回（SDK54時点）は`shorthand-properties`・`arrow-functions`が`babel-preset-expo`の依存ツリー経由で暗黙的に（ホイスティングにより）解決できていたが、SDK56の`babel-preset-expo@56.0.20`では依存関係の構成が変わり、この2つが暗黙に解決されなくなった。`react-native-worklets-core`が要求する5つのBabelプラグインは、**明示的に依存関係へ追加しない限りExpoのバージョンアップのたびに再発しうる**、恒久的なリスクであることが分かった。

## オープンクエスチョン（実装・検証で確定させること）→ 更新

- ~~2つのパッケージ追加後、バンドリングが最後まで完了するか~~ → 一度は完了を確認したが、SDK56アップグレードで別の2プラグインが不足し**再発した**。
- **恒久対応を実施済み**: `react-native-worklets-core`が要求する5つのBabelプラグイン全てを`frontend/package.json`の直接の依存関係として明示的に追加した。

  ```
  "@babel/plugin-proposal-optional-chaining": "^7.21.0",
  "@babel/plugin-proposal-nullish-coalescing-operator": "^7.18.6",
  "@babel/plugin-transform-arrow-functions": "^7.27.1",
  "@babel/plugin-transform-shorthand-properties": "^7.27.1",
  "@babel/plugin-transform-template-literals": "^7.27.1",
  ```

  これにより、今後Expo/babel-preset-expoのバージョンアップで依存ツリーのホイスティング状況が変わっても、この5つが暗黙的に消えることはなくなる。
- バンドリングが完了した後、[.kiro/specs/fix-jitsi-config-network-error/](../fix-jitsi-config-network-error/)・[.kiro/specs/upgrade-expo-sdk56-jitsi13/](../upgrade-expo-sdk56-jitsi13/)の本題（Meeting画面のクラッシュ・接続問題）が実際に解消するかを実機・エミュレータで再確認する。
