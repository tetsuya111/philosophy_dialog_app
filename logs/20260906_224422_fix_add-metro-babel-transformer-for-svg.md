# 作業ログ: react-native-svg-transformerが要求するmetro-babel-transformerの追加

## 何を行ったか

- `@react-native/metro-babel-transformer@0.85.3`を`frontend/package.json`のdevDependenciesに追加した。
- `.kiro/specs/fix-jitsimeeting-element-invalid/requirements.md`に結果を反映した。

## なぜ行ったか

`metro.config.js`に`react-native-svg-transformer`を設定した後、`Cannot find module 'metro-react-native-babel-transformer'`エラーが発生した。`node_modules/react-native-svg-transformer/index.js`を確認したところ、内部で`@react-native/metro-babel-transformer`（react-native >= 0.73で使われる新パッケージ名）を先に試し、失敗したら`metro-react-native-babel-transformer`（旧パッケージ名）にフォールバックする実装だった。Expoプロジェクトは通常どちらのパッケージもインストールしないため両方とも見つからずエラーになっていた。

インストール済みの`react-native`（`0.85.3`）と同じバージョンの`@react-native/metro-babel-transformer`を追加することで、react-native-svg-transformerの1つ目の候補が解決されるようにした。

## 残作業

[CLAUDE.md](../CLAUDE.md)の方針により、Metro再起動・動作確認はユーザーに依頼する。
