# 作業ログ: react-native-worklets-coreのBabelプラグイン未設定を修正

## 何を行ったか

- `frontend/babel.config.js`を新規作成し、`presets: ['babel-preset-expo']`と`plugins: [['react-native-worklets-core/plugin']]`を設定した。
- `docs/frontend.md`にこの設定の必要性を追記した。
- `.kiro/specs/fix-jitsi-config-network-error/requirements.md`を、特定した根本原因（worklet未変換）に基づいて全面的に書き直した。

## なぜ行ったか

Meeting画面で「参加→即切断→再参加でinvalid urlエラー」が実機・エミュレータ・Wi-Fi・モバイルデータ通信のいずれでも共通して再現していた。PCのブラウザ版Jitsiでは問題が起きないことも確認済みで、ネットワーク/回線起因の仮説はすべて排除されていた。

LogBoxで完全なエラーメッセージ（`Error: In callInContext the function parameter is not a valid worklet and cannot be called between contexts or from/to JS from/to a context.`）を確認できたことで、原因を特定できた。`@jitsi/react-native-sdk`は`react-native-worklets-core`に直接依存しており（`package.json`で確認済み）、そのライブラリの公式README（`node_modules/react-native-worklets-core/README.md`）には`babel.config.js`に`react-native-worklets-core/plugin`を追加する必要があると明記されていた。しかしこのプロジェクトには`babel.config.js`自体が存在せず（`babel-preset-expo`のみに依存）、`babel-preset-expo`はこのプラグインを自動検出しないため、Jitsi SDK内部のworklet呼び出しが変換されないまま実行され、エラーになっていたと判断した。

この結論は、エミュレータ・実機・Wi-Fi・モバイルデータのいずれでも同一の問題が再現すること（Babel設定はプラットフォーム非依存）、PCブラウザ版では問題が起きないこと（ブラウザ版はreact-native-worklets-coreを使わない別クライアント）とも整合する。

## 残作業

Metroのキャッシュをクリアして再起動し、実機・エミュレータの両方で問題が解消するかの確認が必要（[CLAUDE.md](../CLAUDE.md)の方針により、frontendの起動・確認はユーザーに依頼する）。
