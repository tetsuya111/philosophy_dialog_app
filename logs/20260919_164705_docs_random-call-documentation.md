# ランダムコール実装に伴うドキュメント更新（tasks.md タスク12）

## 何を行ったか

- `docs/backend.md`: 管理コマンド、CORS・レート制限の設定、`matching` の構成（利用者識別子による認証、状態の導出、サービス層、定数、期限切れ処理）を追記し、旧マッチングの説明を置き換えた。
- `docs/frontend.md`: `EXPO_PUBLIC_API_BASE_URL` と `adb reverse tcp:8000 tcp:8000`、`lib/` の役割、通話画面の `mode` / `endsAt` を追記。
- `CLAUDE.md`: 「バックエンドはCORS未対応」を現状に更新し、マニュアル一覧に `manuals/random-call-testing.md` を追加。
- `.kiro/steering/`: product.md の主要フロー、structure.md、tech.md を現状に更新。
- `manuals/random-call-testing.md` を新規作成（4つの利用者識別子の用意の仕方、`add_dummy_waiters`、確認項目、トラブルシューティング）。

## なぜ行ったか

実装内容を各ドキュメントに反映し、次のセッションや手動確認で前提を把握できるようにするため。
