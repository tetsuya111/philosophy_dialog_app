# フロントエンドのセットアップ手順を yarn install に変更

## 何を行ったか

- `docs/frontend.md` と `frontend/README.md` のセットアップ手順を `npm install` から `yarn install` に変更し、yarn を使う理由と Node 22 未満での `--ignore-engines` を追記した。

## なぜ行ったか

`npm install` が `ERESOLVE` で失敗したため。`@jitsi/react-native-sdk@13.1.1` は `@react-native-async-storage/async-storage@1.23.1` を peerDependencies で厳密に指定するが、`package.json` は `@amplitude/analytics-react-native` との重複解消のため意図的に `1.24.0` にしており（2026-09-06）、npm は食い違いをエラーとする。リポジトリの依存関係は元々 `yarn.lock` で管理されており、yarn では警告のみでインストールできる。
