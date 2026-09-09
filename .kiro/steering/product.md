# プロダクト概要

`philosophy_dialog_app` — ランダムマッチ哲学対話アプリ。

ユーザーを4人単位でランダムにマッチングし、Jitsi Meetによるグループビデオ通話上で哲学対話を行うことを目的としたモバイル/Webアプリ。

## 主要フロー

1. ユーザー登録・ログイン（JWT認証、`backend/accounts/`）
2. マッチング待機列への参加・離脱（`backend/matching/`、`UserMatchingStatus`: `NONE` → `WATING` → `JOINED`）。待機列が4人に達すると自動的に`Room`（`matching/models.py`）が作成され、該当ユーザーがまとめて割り当てられる（`matching/signals.py`の`add_to_queue`）。
3. マッチング成立後、Jitsi Meetのビデオ通話画面（`frontend/components/Meeting.tsx`）で対話を行う

現状、Home画面（`frontend/app/(tabs)/index.tsx`）の「一人で対話を開始する」ボタンから、マッチングを介さず自動生成されたルーム名でJitsi Meet通話画面（`frontend/app/meeting.tsx`）に単独で入ることができる。ただしバックエンドの`Room`（マッチング成立時に複数人がまとめられる単位）とは連携しておらず、マッチング機能とビデオ通話画面の統合は未実装。

詳細は [docs/backend.md](../../docs/backend.md) / [docs/frontend.md](../../docs/frontend.md) を参照。
