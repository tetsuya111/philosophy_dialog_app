# バックエンド (`backend/`)

Django REST Framework による API。認証は `djangorestframework-simplejwt` を使ったJWT。

## セットアップ

```bash
cd backend
python -m venv venv
./venv/Scripts/activate      # PowerShellの場合: venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
```

## よく使うコマンド

```bash
python manage.py runserver              # 開発サーバー起動 (http://localhost:8000)
python manage.py migrate                # マイグレーション適用
python manage.py makemigrations         # モデル変更後のマイグレーション作成
python manage.py createsuperuser        # 管理ユーザー作成
python manage.py test                   # 全テスト実行
python manage.py test accounts          # 特定アプリのテストのみ実行
python manage.py test accounts.tests.ClassName.test_method_name  # 単一テストの実行
python manage.py check                  # サーバーを起動せず設定を検証
```

## 設定

現状、設定は `backend/backend/settings.py` に直書きされており、環境変数からの読み込みは未導入（`SECRET_KEY` はコード内にハードコード、`DEBUG = True` 固定、`DATABASES` は常にリポジトリ直下の `db.sqlite3` を使うSQLite固定）。本番相当の環境を用意する際は、シークレットやDB接続先を環境変数化する対応が別途必要になる。

## アーキテクチャ

- `backend/backend/` がDjangoプロジェクト本体のパッケージ（`settings.py`、ルートの `urls.py`、`wsgi.py`/`asgi.py`）。`ROOT_URLCONF` は `backend.urls`。
- Djangoアプリは `backend/` 直下に配置する（例: `accounts/`、`matching/`）。新規アプリを追加する際は `backend/backend/settings.py` の `INSTALLED_APPS` に登録し、`backend/backend/urls.py` から `include()` でURLを組み込むこと。
- 認証はセッションではなく、ステートレスなJWT（`rest_framework_simplejwt`）を使用する。`REST_FRAMEWORK.DEFAULT_PERMISSION_CLASSES` はグローバルに `IsAuthenticated` がデフォルトのため、ユーザー登録・ログインのような公開エンドポイントを新設する場合は明示的に `authentication_classes = []` / `permission_classes = []` を設定する必要がある（`accounts/views.py` の `RegisterView`/`LoginView` を参照）。
- JWTはレスポンスボディで返さず、ログイン時に `httponly` Cookie（Cookie名は `shared/middleware.py` の `ACCESS_TOKEN_COOKIE_NAME`）としてブラウザ/クライアントに設定する。`shared.middleware.AuthorizationHeaderMiddleware` が、`/api/auth/login/` と `/swagger/` を除く全リクエストでこのCookieを読み取り `Authorization: JWT <token>` ヘッダーに詰め替えるため、DRF側は通常のJWT認証と同じ流れで動作する。
- 認証関連エンドポイント（`accounts/urls.py`、`/api/auth/` 配下）:
  - `POST /api/auth/register/` — 新規ユーザー作成（公開）
  - `POST /api/auth/login/` — ログイン。成功時はアクセストークンをhttponly Cookieに設定（公開）
  - `GET /api/auth/logout/` — ログアウト（Cookie削除）
  - `GET /api/auth/user/me/` — 認証中ユーザーの取得
  - `DELETE /api/auth/delete/` — 認証中ユーザー自身の削除
- マッチング関連エンドポイント（`matching/urls.py`、`/api/matching/` 配下）:
  - `GET /api/matching/join/` — 待機列（`WaitingQueue`）への参加
  - `GET /api/matching/cancel/` — 待機列からの離脱
  - ユーザーのマッチング状態は `accounts.CustomUser.matching_status`（`accounts/choices.py` の `UserMatchingStatus`: `NONE`/`WATING`/`JOINED`）で管理する。
  - 待機列は `matching/signals.py` の `post_save` シグナル（`add_to_queue`）で監視しており、`WaitingQueue` の件数が `WAITING_LIMIT_N`（現状4）に達すると、先頭4件のユーザーをまとめて `Room` に割り当て、対象の `WaitingQueue` を削除する（4人単位のグループマッチング）。
- `accounts/` は今後アプリを追加する際の雛形。`serializers.py` にDRFシリアライザ、`views.py` にAPIビュー、`urls.py` をプロジェクトルートから `/api/<app>/` プレフィックスでincludeする、という構成に従うこと。
