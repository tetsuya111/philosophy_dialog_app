# ランダムコールの設計ドキュメントを新規作成

## 何を行ったか

[.kiro/specs/random-call/design.md](../.kiro/specs/random-call/design.md) を新規作成した。主な設計判断は以下。

- ログインなしの利用者は、サーバー発行の利用者識別子（`X-Client-Id`、DBにはSHA-256のみ保存）ごとにゲスト用 `CustomUser` を自動作成して扱い、`matching` の外部キー構成を維持する。
- `CustomUser.matching_status` を廃止し、ユーザーの状態を待機列・`RoomMember` の行の有無から導出する。
- `post_save` シグナルによるグループ化をやめ、`matching/services.py` に `transaction.atomic` + `select_for_update` で集約する。
- タイムアウト・満了は、状態取得時の遅延評価と管理コマンド `expire_random_calls` の二段構え。画面反映は3秒ポーリング。
- フロントエンドは Home の「対話をはじめる」ボタンと既存の `app/meeting.tsx` / `Meeting*.tsx` を流用し、`onClose` / `endsAt` の任意 props のみ追加する。
- Web版のため `django-cors-headers` を導入する。

## なぜ行ったか

確定した要件定義（[requirements.md](../.kiro/specs/random-call/requirements.md)）をもとに実装方針を決めるため。
