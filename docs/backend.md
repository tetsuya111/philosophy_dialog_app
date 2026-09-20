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
python manage.py expire_random_calls    # ランダムコールの待機タイムアウト・通話の満了を処理する(本番では1分間隔で定期実行)
python manage.py add_dummy_waiters 3    # 手動確認用: ダミーのゲストを待機列に追加する(DEBUG=Trueのときのみ)
```

`requirements.txt` に依存パッケージを追加した場合(例: ランダムコールで追加した `django-cors-headers`)は、`pip install -r requirements.txt` を再実行すること。

## 設定

現状、設定は `backend/backend/settings.py` に直書きされており、環境変数からの読み込みは未導入（`SECRET_KEY` はコード内にハードコード、`DEBUG = True` 固定、`DATABASES` は常にリポジトリ直下の `db.sqlite3` を使うSQLite固定）。本番相当の環境を用意する際は、シークレットやDB接続先を環境変数化する対応が別途必要になる。

- CORS: `django-cors-headers` を導入済み。許可するオリジンは環境変数 `CORS_ALLOWED_ORIGINS`(カンマ区切り、既定 `http://localhost:8081` = Expo Webの開発サーバー)で指定する。ランダムコールの利用者識別子を送る `X-Client-Id` ヘッダーを `CORS_ALLOW_HEADERS` に追加している。
- レート制限: `REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"]` の `matching_client`(利用者識別子の発行、IPごとに `30/hour`)。

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
- ランダムコール(`matching/`、`/api/matching/` 配下。仕様は [.kiro/specs/random-call/](../.kiro/specs/random-call/design.md))
  - **ログインなしで使う。** JWTではなく、`POST /api/matching/client/` でサーバーが発行した利用者識別子を `X-Client-Id` ヘッダーで送り、`matching/authentication.py` の `ClientIdAuthentication` で認証する(ビュー単位で `authentication_classes` を差し替えており、グローバル設定と `accounts` のJWT認証には影響しない)。識別子ごとにゲスト用の `CustomUser`(`guest-...`、パスワード無効)と `GuestClient`(識別子のSHA-256のみ保存)を作る。
  - エンドポイント: `POST client/`(発行、認証不要) / `GET status/` / `POST join/` / `POST cancel/` / `POST call/enter/` / `POST call/leave/`。状態を変えるものはすべて `POST`。
  - ユーザーの状態(`none`/`waiting`/`matched`/`in_call`)はDBに保存せず、`WaitingQueue` と `RoomMember`(`is_active`・`joined_at`)の行の有無から導出する(`services.get_state()`)。旧 `CustomUser.matching_status` は廃止した。
  - 状態を変える処理はすべて `matching/services.py` に集約し、`transaction.atomic()` + `select_for_update()` で同時実行時の不整合を防ぐ。待機列が `GROUP_SIZE`(4)に達すると `join_queue()` の中で先頭4人を `Room` にまとめる(`post_save` シグナルは使わない)。
  - 設定値(人数・待機タイムアウト5分・通話の有効時間30分)は `matching/constants.py` の1箇所で管理する。
  - タイムアウト・満了は常駐ワーカーを使わず、`status`/`join`/`call/enter` の先頭で `expire_stale()` を呼ぶ遅延評価と、管理コマンド `expire_random_calls` の二段構えで処理する。
  - ログは `structlog.get_logger("matching")` で出す(利用者識別子・ルーム名は出さない)。
- `accounts/` は今後アプリを追加する際の雛形。`serializers.py` にDRFシリアライザ、`views.py` にAPIビュー、`urls.py` をプロジェクトルートから `/api/<app>/` プレフィックスでincludeする、という構成に従うこと。
