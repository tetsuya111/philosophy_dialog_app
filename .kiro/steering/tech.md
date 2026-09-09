# 技術スタック

## バックエンド (`backend/`)

- Django REST Framework（`djangorestframework-simplejwt` によるJWT認証）
- Python、依存管理は `requirements.txt`、Lintは Ruff（`pyproject.toml`）
- DBは現状SQLite固定（`backend/db.sqlite3`）

詳細・アーキテクチャ規約は [docs/backend.md](../../docs/backend.md) を参照。

## フロントエンド (`frontend/`)

- Expo（React Native, TypeScript）
- ルーティングは expo-router（ファイルベース）
- 通話機能は `@jitsi/react-native-sdk`（Jitsi Meet SDK）
- Lintは ESLint（`eslint-config-expo`）

詳細・アーキテクチャ規約は [docs/frontend.md](../../docs/frontend.md) を参照。

## 共通

- バックエンドとフロントエンドは共通のビルドツールを持たず、HTTP経由でのみ連携する独立したアプリとして開発・起動する。
