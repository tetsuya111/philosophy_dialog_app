# プロダクト概要

`philosophy_dialog_app` — ランダムマッチ哲学対話アプリ。

ユーザーを4人単位でランダムにマッチングし、Jitsi Meetによるグループビデオ通話上で哲学対話を行うことを目的としたモバイル/Webアプリ。

## 主要フロー

1. Home画面（`frontend/app/(tabs)/index.tsx`）の「対話をはじめる」でランダムコールの待機列に参加する。**ログインは不要**で、サーバーが発行した利用者識別子で利用者を見分ける（`backend/matching/`）
2. 待機列に4人揃うと自動的にグループ（`Room`）が作られ、グループ専用のJitsiルーム名が発行される。待機は5分でタイムアウトし、マッチング前ならいつでも取りやめられる
3. 「対話に参加」でJitsi Meetの通話画面（`frontend/app/meeting.tsx` → `components/Meeting.tsx` / `Meeting.web.tsx`）に入る。通話の有効時間は30分で、満了すると通話画面が自動で閉じる

このほか、「一人で対話を開始する」ボタンから、マッチングを介さず自動生成されたルーム名で単独で通話画面に入ることもできる。ユーザー登録・ログイン（JWT認証、`backend/accounts/`）のAPIは存在するが、フロントエンドからは未使用。ランダムコールの仕様は [.kiro/specs/random-call/](../specs/random-call/requirements.md) を参照。

詳細は [docs/backend.md](../../docs/backend.md) / [docs/frontend.md](../../docs/frontend.md) を参照。
