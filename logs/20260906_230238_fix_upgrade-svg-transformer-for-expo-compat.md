# 作業ログ: react-native-svg-transformerをExpo対応版にアップグレード

## 何を行ったか

- `@react-native/metro-babel-transformer@0.85.3`を追加した後、続けて`Cannot find module 'babel.config.js'`エラーが発生することを確認した。原因を調査し、`@react-native/metro-babel-transformer`が`@expo/metro-config`独自のモジュール解決（`moduleMapper.js`）と完全には互換性がなく、babel.config.jsの`extends`解決に失敗することが分かった。
- Web調査で`react-native-svg-transformer`の最新版（`1.5.3`）が`@expo/metro-config/babel-transformer`を優先的に使うExpo対応ロジック（`getExpoTransformer()`）を持つことを確認した。
- `react-native-svg-transformer@1.5.3`を`frontend/package.json`のdevDependenciesに追加し、Jitsi SDKが依存として持ち込む古い`1.2.0`より優先してトップレベルに解決されることを`yarn why`で確認した。

## なぜ行ったか

`@jitsi/react-native-sdk`が依存として持ち込む`react-native-svg-transformer@1.2.0`は、Expoの独自Metro基盤（`@expo/metro-config`）とうまく統合できない古い実装だった。`@react-native/metro-babel-transformer`を追加で挟む対応も試したが別のエラーが発生したため、根本的にはトランスフォーマー自体をExpo対応済みの新しいバージョンに上げることで解決するのが適切と判断した。

## 残作業

[CLAUDE.md](../CLAUDE.md)の方針により、Metro再起動・動作確認はユーザーに依頼する。
