# プロジェクト構造

```
.
├── backend/           # Django REST Framework API
│   ├── backend/        # Djangoプロジェクト本体（settings.py, urls.py, wsgi/asgi）
│   ├── accounts/        # ユーザー登録・認証（新規アプリの雛形）
│   ├── matching/        # ランダムマッチング（待機列・Room）
│   ├── shared/           # アプリ横断のミドルウェア等
│   └── manage.py
├── frontend/          # Expo (React Native, TypeScript) アプリ
│   ├── app/             # expo-routerのファイルベースルーティング
│   ├── components/       # 再利用可能なUIコンポーネント
│   ├── hooks/             # 共通ロジック（カスタムフック）
│   └── constants/          # テーマ・定数
├── docs/              # 各種ドキュメント（CLAUDE.mdの索引先）
├── .kiro/             # steering / specs / hooks（本ファイル群）
└── logs/              # 作業ログ（詳細は CLAUDE.md の「作業ログ」セクション参照）
```

## 命名・配置の規約

- バックエンドの新規Djangoアプリは `accounts/` の構成（`models.py` / `serializers.py` / `views.py` / `urls.py`）に倣う。詳細は [docs/backend.md](../../docs/backend.md)。
- フロントエンドのプラットフォーム固有実装は `Component.web.tsx` のようにプラットフォームサフィックスで出し分ける。詳細は [docs/frontend.md](../../docs/frontend.md)。
- 機能追加時は実装より先に `.kiro/specs/<feature-slug>/` に `requirements.md` → `design.md` → `tasks.md` を書く（[.kiro/specs/README.md](../specs/README.md)）。
