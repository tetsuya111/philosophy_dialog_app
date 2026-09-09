# backend

`philosophy_dialog_app` のバックエンドAPI。Django REST Framework + `djangorestframework-simplejwt` によるJWT認証で、ユーザー登録・認証とランダムマッチングを提供する。

## セットアップ

```bash
python -m venv venv
./venv/Scripts/activate      # PowerShellの場合: venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

サーバーは http://localhost:8000 で起動する。

## ドキュメント

セットアップの詳細・よく使うコマンド・設定・アーキテクチャ（エンドポイント一覧、認証方式、マッチングロジックなど）は [../docs/backend.md](../docs/backend.md) を参照。

## Lint

```bash
ruff check .
```

（設定は `pyproject.toml`）
