# READMEの新規作成・更新

## 何を

- `README.md`（ルート）: 最小限だった内容を、モノレポ構成と各ドキュメントへのリンクを含む索引として拡充。
- `backend/README.md`: 新規作成。セットアップ手順と `docs/backend.md` への導線を記載。
- `frontend/README.md`: `create-expo-app` 由来の英語テンプレートを、プロジェクト固有の内容の日本語READMEに全面差し替え。

## なぜ

CLAUDE.mdの「リポジトリ内のREADME.mdはすべて日本語で記載する」という規約に対し、`backend/`にREADMEが存在せず、`frontend/README.md`が英語のテンプレートのままだったため。ユーザーからの依頼で、現状の実装（backend: Django REST Framework、frontend: Expo/React Native）に合わせて各フォルダにREADMEを整備した。
