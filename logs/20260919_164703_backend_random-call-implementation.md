# ランダムコールのバックエンド実装（tasks.md タスク1〜8）

## 何を行ったか

[.kiro/specs/random-call/design.md](../.kiro/specs/random-call/design.md) に従い、`backend/matching/` を作り直した。

- 設定: `django-cors-headers` を導入（`requirements.txt`、`settings.py` の `INSTALLED_APPS` / `MIDDLEWARE` / `CORS_ALLOWED_ORIGINS` / `CORS_ALLOW_HEADERS`）。利用者識別子発行のレート制限 `matching_client: 30/hour` を追加。
- モデル: `GuestClient` を追加、`WaitingQueue.user` を OneToOne 化、`Room` に `room_name` / `status` / `end_reason` / `expires_at` / `ended_at` を追加し M2M `users` を `RoomMember` に置き換え（制約 `one_active_room_per_user`）。マイグレーション `matching/0004_random_call.py`（既存の待機行・ルーム行を削除）。
- `accounts.CustomUser.matching_status` と `accounts/choices.py` を削除（`accounts/0004`）。`UserView` のレスポンスから `matching_status` を除外。`matching/signals.py` を削除。
- 新規: `matching/constants.py`（人数・待機5分・有効時間30分）、`authentication.py`（`X-Client-Id` による `ClientIdAuthentication`）、`services.py`（参加・取りやめ・グループ化・入退室・満了を `transaction.atomic` + `select_for_update` で集約）、管理コマンド `expire_random_calls` / `add_dummy_waiters`。
- API: `POST client/` / `GET status/` / `POST join/` / `POST cancel/` / `POST call/enter/` / `POST call/leave/`（旧 `GET join/`・`GET cancel/` は削除）。
- テスト: `matching/tests.py` に28件（サービス層・API・CORS・レート制限）。`python manage.py test` は全件成功。

## なぜ行ったか

ログインなしで「待機 → 4人マッチング → グループ専用ルームでの通話 → 満了」を成立させるため。既存実装の不備（キャンセルが元の待機行を消さない、GETで状態変更、成立時に状態が NONE に戻る、シグナル依存で排他なし）も合わせて解消した。

## 補足

- `backend/tests/test.py`（手動実行用スクリプト）は旧 `GET join/`・`GET cancel/` を呼んでおり、今回の変更後は動かない。未修正。
- `matching/tests.py` に残る Ruff の指摘は PT009（unittest形式のassert）のみで、Django の `TestCase` を使うため対象外とした。
