# 作業ログ: react-native-worklets-coreが要求する不足Babelプラグインの追加

## 何を行ったか

- `.kiro/specs/fix-worklets-core-missing-babel-plugins/requirements.md`を新規作成した。
- `frontend/package.json`に`@babel/plugin-proposal-nullish-coalescing-operator@7.18.6`・`@babel/plugin-transform-template-literals@7.29.7`をdevDependenciesとして追加した。
- `@babel/plugin-transform-template-literals`は無指定インストールだと`@babel/core@^8.0.0`を要求するBabel 8系（`8.0.1`）が誤って解決されたため、`^7.27.1`を明示指定してBabel 7系（`7.29.7`）に固定し直した。

## なぜ行ったか

[.kiro/specs/fix-jitsi-config-network-error/](../.kiro/specs/fix-jitsi-config-network-error/)で`babel.config.js`に`react-native-worklets-core/plugin`を追加した結果、Metroバンドリングが`Cannot find module '@babel/plugin-proposal-nullish-coalescing-operator'`で失敗するようになった。

`node_modules/react-native-worklets-core/src/plugin/index.js`を確認したところ、worklet関数を隔離コンパイルする際に5つのBabelプラグイン名をハードコードしており、そのうち2つ（`@babel/plugin-proposal-nullish-coalescing-operator`、`@babel/plugin-transform-template-literals`）が未インストールと判明した。1つずつ試すのではなく事前にソースを確認して両方を特定し、まとめて追加した。
