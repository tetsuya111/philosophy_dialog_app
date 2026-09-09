# 作業ログ: react-native-worklets-core用Babelプラグイン不足の再発と恒久対応

## 何を行ったか

- `@babel/plugin-transform-shorthand-properties`・`@babel/plugin-transform-arrow-functions`を追加インストールした。
- `react-native-worklets-core`が要求する5つのBabelプラグイン全て（上記2つ＋既存の`@babel/plugin-proposal-optional-chaining`・`@babel/plugin-proposal-nullish-coalescing-operator`・`@babel/plugin-transform-template-literals`）を`frontend/package.json`の直接の依存関係として明示的に固定した。
- `.kiro/specs/fix-worklets-core-missing-babel-plugins/requirements.md`・`docs/frontend.md`に恒久対応の内容を反映した。

## なぜ行ったか

[.kiro/specs/upgrade-expo-sdk56-jitsi13/](../.kiro/specs/upgrade-expo-sdk56-jitsi13/)でExpo SDK 56にアップグレードした後、`npm run android:win`で`Cannot find module '@babel/plugin-transform-shorthand-properties'`エラーが発生した。これは[.kiro/specs/fix-worklets-core-missing-babel-plugins/](../.kiro/specs/fix-worklets-core-missing-babel-plugins/)で以前対応した問題と同種で、当時は`shorthand-properties`・`arrow-functions`は`babel-preset-expo`の依存ツリー経由で暗黙的に解決できていたが、SDK56の`babel-preset-expo@56.0.20`で依存関係の構成が変わり、暗黙のホイスティングでは解決できなくなったと判明した。

同じ問題がExpoのバージョンアップのたびに再発するリスクがあるため、今後は`react-native-worklets-core`が要求する5つのBabelプラグイン全てを、暗黙のホイスティングに頼らず`package.json`に直接の依存関係として明示することにした。

## 残作業

再度Metroキャッシュクリア＋再起動でバンドリングが完了するか、[CLAUDE.md](../CLAUDE.md)の方針によりユーザーに確認を依頼する。
