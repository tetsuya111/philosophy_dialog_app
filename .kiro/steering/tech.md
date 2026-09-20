# 技術スタック

## バックエンド (`backend/`)

- Django REST Framework（`djangorestframework-simplejwt` によるJWT認証。ランダムコールのAPIのみ、ログインなしの利用者識別子で認証する）
- CORSは `django-cors-headers`、ログは `structlog`
- Python、依存管理は `requirements.txt`、Lintは Ruff（`pyproject.toml`）
- DBは現状SQLite固定（`backend/db.sqlite3`）

詳細・アーキテクチャ規約は [docs/backend.md](../../docs/backend.md) を参照。

## フロントエンド (`frontend/`)

- Expo（React Native, TypeScript）
- ルーティングは expo-router（ファイルベース）
- 通話機能は `@jitsi/react-native-sdk`（Jitsi Meet SDK）。Web版はJitsiの `external_api.js`
- バックエンドAPIの接続先は `EXPO_PUBLIC_API_BASE_URL`（`frontend/.env`）、端末への保存は `@react-native-async-storage/async-storage`
- Lintは ESLint（`eslint-config-expo`）

詳細・アーキテクチャ規約は [docs/frontend.md](../../docs/frontend.md) を参照。

## 共通

- バックエンドとフロントエンドは共通のビルドツールを持たず、HTTP経由でのみ連携する独立したアプリとして開発・起動する。
